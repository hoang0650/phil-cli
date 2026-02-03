import sys
import os
import secrets
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Header, Depends, Security, Request, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.orm import Session

# --- IMPORTS TỪ PROJECT ---
sys.path.append(os.getcwd())

# 1. Database & Models
from src.database.session import engine, Base, get_db, SessionLocal
from src.database.models import User, AuditLog, ApiKey
from src.services.bootstrap import create_initial_superuser
from src.services.audit import record_audit_log

# 2. Agent Logic
from src.agent_graph import app_graph

# --- CONFIG & LIFESPAN ---

# Tạo bảng tự động (Trong môi trường Prod nên dùng Alembic Migration)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print(">>> SYSTEM STARTUP: Checking database connection...")
    db = SessionLocal()
    try:
        # Tự động tạo Admin nếu chưa có
        create_initial_superuser(db)
    except Exception as e:
        print(f">>> STARTUP ERROR: {e}")
    finally:
        db.close()
    
    yield # Server chạy tại đây
    
    # --- SHUTDOWN ---
    print(">>> SYSTEM SHUTDOWN")

app = FastAPI(title="Phil AI Global Gateway", lifespan=lifespan)

# --- CONFIG VARIABLES ---
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "phil_default_secret") # Nên có default để test

# --- PYDANTIC MODELS (Input/Output) ---

class ChatRequest(BaseModel):
    user_input: str
    image_url: Optional[str] = None

class UserSyncPayload(BaseModel):
    username: str
    role: str
    plan_type: str
    is_paid: bool

class KeyRequest(BaseModel):
    username: str 

class KeyResponse(BaseModel):
    key: str
    owner: str
    is_active: bool

class CreateKeyRequest(BaseModel):
    owner: str
    role: str = "user"

# --- SECURITY DEPENDENCIES (QUAN TRỌNG) ---

async def get_current_user(
    api_key: str = Security(api_key_header), 
    db: Session = Depends(get_db)
):
    """
    Xác thực API Key từ Database PostgreSQL.
    Trả về: User Object
    """
    # 1. Tìm Key trong DB
    key_record = db.query(ApiKey).filter(ApiKey.key == api_key).first()
    
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid API Key"
        )
    
    if not key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="API Key is revoked"
        )

    # 2. Lấy thông tin chủ sở hữu (User)
    user = db.query(User).filter(User.username == key_record.owner).first()
    if not user:
        raise HTTPException(status_code=404, detail="Owner of this key not found")

    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Chỉ cho phép Admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin privileges required"
        )
    return current_user

async def verify_webhook_secret(x_webhook_secret: str = Header(...)):
    """Bảo vệ Webhook endpoint"""
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Webhook Secret")

# --- 1. WEBHOOK ENDPOINT (Sync User từ Node Server) ---

@app.post("/webhooks/sync-user")
async def sync_user_data(
    payload: UserSyncPayload, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_webhook_secret)
):
    """
    Node Server gọi vào đây để cập nhật trạng thái User (Upsert)
    """
    print(f">>> Received Sync for user: {payload.username} | Plan: {payload.plan_type}")
    
    try:
        # Kiểm tra user có tồn tại không
        user = db.query(User).filter(User.username == payload.username).first()
        
        if user:
            # Update
            user.role = payload.role
            user.plan_type = payload.plan_type
            # Logic mapping is_paid -> is_active hoặc field riêng
            user.is_active = True 
        else:
            # Create new
            user = User(
                username=payload.username,
                role=payload.role,
                plan_type=payload.plan_type,
                is_active=True,
                hashed_password="EXTERNAL_AUTH" # User này không login bằng pass ở đây
            )
            db.add(user)
        
        db.commit()
        return {"status": "synced", "username": payload.username}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync Failed: {str(e)}")

# --- 2. KEY GENERATION (Self-Service) ---

@app.post("/v1/keys/generate")
async def generate_api_key(
    req: KeyRequest, 
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == req.username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register via Main Website.")
    
    if user.plan_type == "free" and user.role != "admin":
        pass 

    new_key_str = f"pk_{secrets.token_urlsafe(32)}"
    
    try:
        new_api_key = ApiKey(
            key=new_key_str,
            owner=user.username,
            is_active=True
        )
        db.add(new_api_key)
        
        # Ghi Audit Log
        record_audit_log(
            db=db,
            actor=user.username,
            role=user.role,
            action="GENERATE_KEY",
            target=new_key_str[:10] + "..."
        )
        
        db.commit()
        
        return {
            "api_key": new_key_str,
            "plan": user.plan_type,
            "message": "Key generated successfully."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. CHAT ENDPOINT (Main Service) ---

@app.post("/v1/chat")
async def chat_endpoint(
    req: ChatRequest, 
    user: User = Depends(get_current_user), # Đã xác thực qua DB
    db: Session = Depends(get_db)
):
    # Logic Agent
    inputs = {
        "user_id": user.username,
        "user_input_vn": req.user_input,
        "image_url": req.image_url,
        "iterations": 0,
        "technical_plan": "", "code": "", "exec_result": ""
    }
    
    try:
        final_state = app_graph.invoke(inputs)     
        return {
            "response": final_state.get('final_response_vn', "No response"),
            "status": "success",
            "user": user.username
        }
    except Exception as e:
        return {"response": f"System Error: {str(e)}", "status": "error"}

# --- 4. PROJECT MANAGEMENT (Audit Log Demo) ---

@app.delete("/v1/projects/{project_id}")
async def delete_project(
    project_id: str, 
    request: Request,
    user: User = Depends(get_current_user), # Yêu cầu login
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    
    record_audit_log(
        db=db,
        actor=user.username,
        role=user.role,
        action="DELETE_PROJECT",
        target=project_id,
        details={
            "ip_address": client_ip,
            "user_agent": request.headers.get("user-agent"),
            "status": "success"
        }
    )
    
    return {"status": "deleted", "project_id": project_id}

# --- 5. ADMIN ENDPOINTS ---

@app.post("/v1/admin/keys")
async def admin_create_key(
    req: CreateKeyRequest, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Admin tạo key thủ công cho ai đó"""
    new_key_str = f"pk_{secrets.token_urlsafe(32)}"
    
    api_key = ApiKey(key=new_key_str, owner=req.owner, is_active=True)
    db.add(api_key)
    
    record_audit_log(db, admin.username, "admin", "ADMIN_CREATE_KEY", req.owner)
    db.commit()
    
    return {"api_key": new_key_str, "owner": req.owner}

@app.get("/v1/admin/keys", response_model=List[KeyResponse])
async def admin_list_keys(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    keys = db.query(ApiKey).all()
    return keys 

@app.delete("/v1/admin/keys/{target_key}")
async def admin_revoke_key(
    target_key: str, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    key_record = db.query(ApiKey).filter(ApiKey.key == target_key).first()
    if key_record:
        key_record.is_active = False
        record_audit_log(db, admin.username, "admin", "REVOKE_KEY", target_key)
        db.commit()
        return {"message": "Key revoked"}
    
    raise HTTPException(status_code=404, detail="Key not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)