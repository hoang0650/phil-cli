import sys
import os
import secrets
import httpx
import json
import logging
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

# 2. Agent Logic & Model Integration
from src.agent_graph import app_graph
from src.config import Config
from src.security.policy import get_security_policy, validate_tool_access, filter_content_security
from src.sandbox.manager import initialize_sandboxing, cleanup_sandboxes

# --- CONFIG & LIFESPAN ---

# Tạo bảng tự động (Trong môi trường Prod nên dùng Alembic Migration)
Base.metadata.create_all(bind=engine)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print(">>> SYSTEM STARTUP: Checking database connection...")
    db = SessionLocal()
    try:
        # Tự động tạo Admin nếu chưa có
        create_initial_superuser(db)
        
        # Initialize sandboxing
        sandbox_manager = initialize_sandboxing()
        logger.info(f"Sandboxing initialized: {'enabled' if sandbox_manager.enabled else 'disabled'}")
        
        # Test phil-ai model connectivity
        await test_phil_ai_connection()
        
    except Exception as e:
        print(f">>> STARTUP ERROR: {e}")
    finally:
        db.close()
    
    yield # Server chạy tại đây
    
    # --- SHUTDOWN ---
    print(">>> SYSTEM SHUTDOWN")
    cleanup_sandboxes()

app = FastAPI(title="Phil AI Global Gateway", lifespan=lifespan)

# --- CONFIG VARIABLES ---
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "phil_default_secret") # Nên có default để test

# --- PYDANTIC MODELS (Input/Output) ---

class ChatRequest(BaseModel):
    user_input: str
    image_url: Optional[str] = None
    use_sandbox: bool = True  # Enable sandboxing by default
    security_level: Optional[str] = "high"  # Security level for MCP tools

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

class ModelResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int
    security_check: Dict[str, Any]

# --- PHIL-AI MODEL INTEGRATION ---

async def test_phil_ai_connection():
    """Test connection to phil-ai models"""
    try:
        model_config = Config.get_model_config()
        brain_endpoint = model_config["brain"]["endpoint"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{brain_endpoint}/health")
            if response.status_code == 200:
                logger.info(f"✅ Phil-AI Brain model connected: {brain_endpoint}")
            else:
                logger.warning(f"⚠️  Phil-AI Brain model health check failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Failed to connect to Phil-AI models: {str(e)}")

async def call_phil_ai_model(endpoint: str, prompt: str, model_name: str, max_tokens: int = 4096) -> Dict[str, Any]:
    """Call phil-ai model endpoint"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = await client.post(f"{endpoint}/chat/completions", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "tokens_used": result["usage"]["total_tokens"],
                    "model": result["model"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Model returned status {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call model: {str(e)}"
        }

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

# --- 3. CHAT ENDPOINT (Main Service with Phil-AI Integration) ---

@app.post("/v1/chat", response_model=ModelResponse)
async def chat_endpoint(
    req: ChatRequest, 
    user: User = Depends(get_current_user), # Đã xác thực qua DB
    db: Session = Depends(get_db)
):
    """
    Chat endpoint với Phil-AI model integration và security features
    """
    
    # Security content filtering
    content_filter = filter_content_security(req.user_input, "prompt", user.username)
    if not content_filter["allowed"]:
        logger.warning(f"Content blocked for user {user.username}: {content_filter['reason']}")
        return ModelResponse(
            response=f"Content blocked by security policy: {content_filter['reason']}",
            model_used="security_filter",
            tokens_used=0,
            security_check={"blocked": True, "reason": content_filter["reason"]}
        )
    
    # Get model configuration
    model_config = Config.get_model_config()
    
    try:
        # Call Phil-AI Brain model
        brain_endpoint = model_config["brain"]["endpoint"]
        brain_model = model_config["brain"]["model_name"]
        
        logger.info(f"Calling Phil-AI Brain model: {brain_model} at {brain_endpoint}")
        
        result = await call_phil_ai_model(
            endpoint=brain_endpoint,
            prompt=req.user_input,
            model_name=brain_model
        )
        
        if not result["success"]:
            logger.error(f"Model call failed: {result['error']}")
            return ModelResponse(
                response=f"Model error: {result['error']}",
                model_used=brain_model,
                tokens_used=0,
                security_check={"error": True, "details": result["error"]}
            )
        
        # Filter model response
        response_filter = filter_content_security(result["response"], "response", user.username)
        if not response_filter["allowed"]:
            logger.warning(f"Model response blocked: {response_filter['reason']}")
            return ModelResponse(
                response=f"Model response blocked by security policy: {response_filter['reason']}",
                model_used=brain_model,
                tokens_used=result["tokens_used"],
                security_check={"blocked": True, "reason": response_filter["reason"]}
            )
        
        # Record audit log
        record_audit_log(
            db=db,
            actor=user.username,
            role=user.role,
            action="CHAT_REQUEST",
            target=brain_model,
            details={
                "prompt_length": len(req.user_input),
                "response_length": len(result["response"]),
                "tokens_used": result["tokens_used"],
                "security_level": req.security_level,
                "sandbox_enabled": req.use_sandbox
            }
        )
        
        return ModelResponse(
            response=result["response"],
            model_used=result["model"],
            tokens_used=result["tokens_used"],
            security_check={"passed": True, "level": req.security_level}
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return ModelResponse(
            response=f"System error: {str(e)}",
            model_used="error",
            tokens_used=0,
            security_check={"error": True, "details": str(e)}
        )

# --- 4. SANDBOX EXECUTION ENDPOINT ---

@app.post("/v1/sandbox/execute")
async def sandbox_execute(
    command: str,
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute commands in sandboxed environment
    """
    from src.sandbox.manager import get_sandbox_manager
    
    sandbox_manager = get_sandbox_manager()
    
    if not sandbox_manager.enabled:
        return {"status": "error", "message": "Sandboxing is disabled"}
    
    try:
        # Create sandbox for user session
        sandbox_info = sandbox_manager.create_sandbox(session_id, task_type="user_command")
        
        if sandbox_info.get("status") == "error":
            return sandbox_info
        
        container_id = sandbox_info["container_id"]
        
        # Execute command in sandbox
        result = sandbox_manager.execute_command(container_id, command)
        
        # Record audit log
        record_audit_log(
            db=db,
            actor=user.username,
            role=user.role,
            action="SANDBOX_EXECUTE",
            target=container_id,
            details={
                "command": command,
                "exit_code": result.get("exit_code"),
                "status": result.get("status"),
                "session_id": session_id
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Sandbox execution error: {str(e)}")
        return {"status": "error", "message": f"Sandbox execution failed: {str(e)}"}

# --- 5. PROJECT MANAGEMENT (Audit Log Demo) ---

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

# --- 6. ADMIN ENDPOINTS ---

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

# --- 7. SECURITY STATUS ENDPOINT ---

@app.get("/v1/security/status")
async def security_status(
    user: User = Depends(get_current_user)
):
    """Get current security configuration status"""
    policy = get_security_policy()
    config = Config.get_model_config()
    
    return {
        "security_level": policy.security_level.value,
        "sandbox_enabled": Config.SANDBOX_ENABLED,
        "phil_ai_models": {
            "brain": config["brain"]["model_name"],
            "vision": config["vision"]["model_name"],
            "ears": config["ears"]["model_name"],
            "mouth": config["mouth"]["model_name"]
        },
        "policy_summary": policy.get_policy_summary(),
        "local_models": Config.USE_LOCAL_MODELS,
        "anthropic_api_disabled": not Config.ANTHROPIC_API_KEY
    }