import requests
import time
from .config import load_config

def send_chat(message, project_zip_path=None):
    config = load_config()
    api_key = config.get("api_key")
    base_url = config.get("server_url")

    if not api_key:
        return {"error": "Bạn chưa đăng nhập. Hãy chạy 'phil login <your_key>'"}

    headers = {"x-api-key": api_key}
    
    try:
        # Nếu có gửi file project
        if project_zip_path:
            with open(project_zip_path, 'rb') as f:
                files = {'file': ('project.zip', f, 'application/zip')}
                data = {'user_input': message}
                # Giả sử endpoint upload & chat
                resp = requests.post(f"{base_url}/v1/chat-with-project", headers=headers, data=data, files=files)
        else:
            # Chat thường
            payload = {"user_input": message}
            resp = requests.post(f"{base_url}/v1/chat", headers=headers, json=payload)
            
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            return {"error": "API Key không hợp lệ hoặc hết hạn."}
        else:
            return {"error": f"Lỗi Server: {resp.status_code} - {resp.text}"}
            
    except Exception as e:
        return {"error": f"Không thể kết nối Server: {str(e)}"}