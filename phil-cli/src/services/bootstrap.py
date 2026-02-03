import os
from sqlalchemy.orm import Session
from src.database.models import User
from src.services.auth import AuthService

def create_initial_superuser(db: Session):
    """
    Kiểm tra xem hệ thống đã có Admin chưa.
    Nếu chưa -> Tạo user 'admin' với mật khẩu mặc định (hoặc từ ENV).
    """
    # 1. Kiểm tra xem có user admin nào chưa
    admin_user = db.query(User).filter(User.role == "admin").first()
    
    if admin_user:
        print("[BOOTSTRAP] Admin user already exists. Skipping.")
        return

    # 2. Lấy thông tin từ biến môi trường (hoặc dùng mặc định)
    # Bạn có thể set trong docker-compose.yml: FIRST_SUPERUSER=admin, FIRST_SUPERUSER_PASSWORD=...
    admin_username = os.getenv("FIRST_SUPERUSER")
    admin_password = os.getenv("FIRST_SUPERUSER_PASSWORD")
    
    print(f"--- [BOOTSTRAP] CREATING SUPERUSER ---")
    print(f"Username: {admin_username}")
    print(f"Password: {admin_password}")
    print(f"--------------------------------------")

    # 3. Tạo User
    new_admin = User(
        username=admin_username,
        hashed_password=AuthService.get_password_hash(admin_password),
        role="admin",
        plan_type="enterprise",
        is_active=True,
        email="admin@phil.ai"
    )
    
    db.add(new_admin)
    db.commit()
    print("[BOOTSTRAP] Superuser created successfully!")