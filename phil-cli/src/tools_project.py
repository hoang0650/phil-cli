import os
import zipfile
import shutil

# Đường dẫn gốc nơi chứa dữ liệu người dùng
BASE_WORKSPACE = "/workspace/users"

def get_user_project_path(user_id):
    """Lấy đường dẫn thư mục project của user"""
    return os.path.join(BASE_WORKSPACE, user_id, "project")

def handle_upload(uploaded_file, user_id):
    """
    Xử lý file người dùng upload (lưu và giải nén)
    Trả về: Cấu trúc thư mục (File Tree) để Agent hiểu
    """
    user_dir = os.path.join(BASE_WORKSPACE, user_id)
    project_dir = os.path.join(user_dir, "project")
    
    # 1. Reset thư mục project cũ (để tránh lẫn lộn)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir, exist_ok=True)

    # 2. Lưu file zip/file lẻ
    file_path = os.path.join(user_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 3. Nếu là ZIP -> Giải nén
    if uploaded_file.name.endswith(".zip"):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(project_dir)
            os.remove(file_path) # Xóa file zip gốc cho nhẹ
            return list_files_recursive(user_id)
        except Exception as e:
            return f"Error Unzipping: {e}"
    else:
        # Nếu là file lẻ -> Move vào folder project
        shutil.move(file_path, os.path.join(project_dir, uploaded_file.name))
        return f"- {uploaded_file.name}"

def list_files_recursive(user_id):
    """Tạo cây thư mục để Agent biết project có gì"""
    project_dir = get_user_project_path(user_id)
    file_tree = []
    
    for root, dirs, files in os.walk(project_dir):
        level = root.replace(project_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        file_tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            file_tree.append(f"{subindent}{f}")
            
    return "\n".join(file_tree)

def read_file_content(user_id, relative_path):
    """Agent đọc nội dung 1 file cụ thể"""
    try:
        full_path = os.path.join(get_user_project_path(user_id), relative_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def zip_project_for_download(user_id):
    """Đóng gói lại project sau khi AI sửa xong"""
    project_dir = get_user_project_path(user_id)
    output_zip = os.path.join(BASE_WORKSPACE, user_id, "modified_project")
    
    shutil.make_archive(output_zip, 'zip', project_dir)
    return f"{output_zip}.zip"