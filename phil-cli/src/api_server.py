from fastapi import FastAPI, HTTPException, Header, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import sys
import os

# Import module Database & Logic Agent
sys.path.append(os.getcwd())
from src.agent_graph import app_graph
from src import database

# Khởi tạo DB ngay khi chạy Server
app = FastAPI(title="Phil AI Global Gateway")
database.init_db()
database.ensure_root_admin()


# Security Scheme
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
NODE_BACKEND_URL = os.getenv("NODE_BACKEND_URL")
# --- MODELS ---
class ChatRequest(BaseModel):
    user_input: str
    image_url: Optional[str] = None
    # Lưu ý: Không cần user_id trong input nữa, sẽ lấy từ API Key owner

class CreateKeyRequest(BaseModel):
    owner: str
    role: str = "user" # 'admin' or 'user'

class KeyResponse(BaseModel):
    key: str
    owner: str
    role: str
    is_active: bool
    created_at: str

# Model dữ liệu mà Node Server sẽ gửi sang
class UserSyncPayload(BaseModel):
    username: str
    role: str       # 'admin', 'user'
    plan_type: str  # 'free', 'pro', 'enterprise'
    is_paid: bool

class KeyRequest(BaseModel):
    username: str # User phải gửi username để định danh
    # Trong thực tế, user nên gửi Access Token của Node Server, 
    # và Phil sẽ gọi Node để verify token đó lấy username.

# --- SECURITY: WEBHOOK VERIFICATION ---

async def verify_webhook_secret(x_webhook_secret: str = Header(...)):
    """Chỉ chấp nhận request có Secret Key đúng từ Node Server"""
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Webhook Secret")

# --- 1. WEBHOOK ENDPOINT (Node Server gọi vào đây) ---

@app.post("/webhooks/sync-user")
async def sync_user_data(payload: UserSyncPayload, authorized: bool = Depends(verify_webhook_secret)):
    """
    Nhận thông tin user từ Node Server (Sau khi thanh toán thành công).
    """
    print(f">>> Received Sync for user: {payload.username} | Plan: {payload.plan_type}")
    
    success = database.sync_external_user(
        username=payload.username,
        role=payload.role,
        plan_type=payload.plan_type,
        is_paid=payload.is_paid
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Database Sync Failed")
        
    return {"status": "synced", "limits": "updated_based_on_plan"}

# --- 2. KEY GENERATION (User gọi vào đây) ---

@app.post("/v1/keys/generate")
async def generate_api_key(req: KeyRequest, x_node_token: Optional[str] = Header(None)):
    
    # 1. Kiểm tra user có tồn tại trong DB nội bộ chưa (Do Webhook sync chưa?)
    user = database.get_user_info(req.username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register/pay at the Main Website first.")
    
    # 2. Kiểm tra điều kiện thanh toán/Gói cước
    if not user['is_paid'] and user['plan_type'] != 'free':
         raise HTTPException(status_code=402, detail="Payment required for this plan.")
    
    # 3. Tạo Key
    new_key = database.create_key(req.username, role=user['role'])
    
    return {
        "api_key": new_key,
        "plan": user['plan_type'],
        "daily_limit": user['limits_daily'],
        "message": "Key generated based on your subscription status."
    }

# --- ENDPOINTS DÀNH CHO USER ---

@app.post("/v1/chat")
async def chat_endpoint(req: ChatRequest, user: dict = Depends(get_current_user)):
    """Endpoint chat chính. User ID tự động lấy từ API Key Owner."""
    
    # Logic Agent
    inputs = {
        "user_id": user['owner'], # <--- TỰ ĐỘNG LẤY TỪ DB
        "user_input_vn": req.user_input,
        "image_url": req.image_url,
        "iterations": 0,
        "technical_plan": "", "code": "", "exec_result": ""
    }
    
    try:
        final_state = app_graph.invoke(inputs)
        return {
            "response": final_state['final_response_vn'],
            "status": "success",
            "user": user['owner']
        }
    except Exception as e:
        return {"response": f"System Error: {str(e)}", "status": "error"}

# --- ENDPOINTS QUẢN TRỊ (ADMIN ONLY) ---

@app.post("/v1/admin/keys", response_model=dict)
async def create_api_key(req: CreateKeyRequest, admin: dict = Depends(get_admin_user)):
    """Admin tạo key mới cho khách hàng"""
    new_key = database.create_key(req.owner, req.role)
    return {"message": "Created successfully", "api_key": new_key, "owner": req.owner}

@app.get("/v1/admin/keys", response_model=List[KeyResponse])
async def list_api_keys(admin: dict = Depends(get_admin_user)):
    """Admin xem danh sách toàn bộ key"""
    # Convert datetime object to string for JSON serialization if necessary
    keys = database.list_all_keys()
    # Simple formatting ensure
    return [
        {**k, "created_at": str(k["created_at"])} for k in keys
    ]

@app.delete("/v1/admin/keys/{target_key}")
async def revoke_api_key(target_key: str, admin: dict = Depends(get_admin_user)):
    """Admin thu hồi key của ai đó"""
    database.revoke_key(target_key)
    return {"message": f"Key {target_key} revoked successfully."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)