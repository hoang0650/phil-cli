import subprocess
import os
import re

def write_to_project(user_id, relative_path, content):
    base_dir = f"/workspace/users/{user_id}/project"
    full_path = os.path.join(base_dir, relative_path)
    
    # Tạo thư mục cha nếu chưa có (VD: src/utils/...)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {relative_path}"
    except Exception as e:
        return f"Error writing file: {e}"

def execute_in_sandbox(code, lang="python", user_id="guest"):
    # 1. Sanitize user_id để tránh path traversal attack (VD: ../../root)
    safe_user_id = re.sub(r'[^a-zA-Z0-9_-]', '', str(user_id))
    if not safe_user_id: safe_user_id = "guest"

    # 2. Tạo đường dẫn workspace riêng: /workspace/users/user123/
    # Lưu ý: /workspace là shared volume giữa Controller và Sandbox container
    base_dir = f"/workspace/users/{safe_user_id}"
    os.makedirs(base_dir, exist_ok=True)

    # 3. Xác định tên file và trình thực thi
    is_python = (lang == "python")
    filename = "script.py" if is_python else "script.js"
    executable = "python3" if is_python else "node"
    
    file_path_host = f"{base_dir}/{filename}"      # Đường dẫn trên container Controller
    file_path_sandbox = f"/workspace/users/{safe_user_id}/{filename}" # Đường dẫn bên trong container Sandbox

    # 4. Ghi code vào file
    try:
        with open(file_path_host, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        return f"SYSTEM EXCEPTION (Write File): {str(e)}"

    # 5. Gọi lệnh docker exec sang container sandbox
    # Cấu trúc lệnh: docker exec ai_sandbox python3 /workspace/users/user123/script.py
    cmd = ["docker", "exec", "ai_sandbox", executable, file_path_sandbox]

    try:
        # Timeout 30s để tránh loop vô tận
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if res.returncode == 0:
            return f"OUTPUT:\n{res.stdout}"
        else:
            return f"ERROR:\n{res.stderr}"
            
    except subprocess.TimeoutExpired:
        return "ERROR: Execution timed out (30s limit)."
    except Exception as e:
        return f"SYSTEM EXCEPTION: {e}"