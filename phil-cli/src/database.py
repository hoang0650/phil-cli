import sqlite3
import secrets
from datetime import datetime

DB_PATH = "/workspace/phil_auth.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Khởi tạo bảng API Keys nếu chưa có"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT DEFAULT 'user',
            plan_type TEXT DEFAULT 'free',
            is_paid BOOLEAN DEFAULT 0,
            limits_daily INTEGER DEFAULT 10, -- Limit số request/ngày
            last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Bảng API Keys (Giữ nguyên)
    c.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(owner) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def sync_external_user(username, role, plan_type, is_paid):
    """
    Hàm này được gọi khi Webhook từ Node Server bắn sang.
    Nó sẽ Update nếu user tồn tại, hoặc Insert nếu chưa có.
    """
    # Logic tính Limit dựa trên Plan (Business Logic)
    limits = 10 # Default Free
    if plan_type == 'pro': limits = 100
    if plan_type == 'enterprise': limits = 1000
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Sử dụng UPSERT (Insert or Replace)
    try:
        c.execute('''
            INSERT INTO users (username, role, plan_type, is_paid, limits_daily, last_synced)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(username) DO UPDATE SET
                role=excluded.role,
                plan_type=excluded.plan_type,
                is_paid=excluded.is_paid,
                limits_daily=excluded.limits_daily,
                last_synced=CURRENT_TIMESTAMP
        ''', (username, role, plan_type, is_paid, limits))
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error] Sync failed: {e}")
        return False
    finally:
        conn.close()

def get_user_info(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return user

def create_key(owner: str, role: str = "user") -> str:
    """Tạo API Key mới (Admin mới tạo được)"""
    new_key = f"pk_{secrets.token_urlsafe(32)}" # Prefix pk_ (Phil Key) cho chuyên nghiệp
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO api_keys (key, owner, role) VALUES (?, ?, ?)", 
                  (new_key, owner, role))
        conn.commit()
        return new_key
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        conn.close()

def get_key_info(key: str):
    """Kiểm tra thông tin Key"""
    conn = get_db_connection()
    c = conn.cursor()
    row = c.execute("SELECT * FROM api_keys WHERE key = ?", (key,)).fetchone()
    conn.close()
    return dict(row) if row else None

def revoke_key(key: str):
    """Vô hiệu hóa Key"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE api_keys SET is_active = 0 WHERE key = ?", (key,))
    conn.commit()
    conn.close()

def list_all_keys():
    """Liệt kê toàn bộ key (Chỉ Admin xem)"""
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute("SELECT key, owner, role, is_active, created_at FROM api_keys").fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- BOOTSTRAP ROOT ADMIN ---
def ensure_root_admin():
    """Đảm bảo luôn có ít nhất 1 Key Admin khi khởi chạy"""
    conn = get_db_connection()
    admin = conn.execute("SELECT * FROM api_keys WHERE role='admin'").fetchone()
    if not admin:
        print(">>> KHỞI TẠO HỆ THỐNG LẦN ĐẦU: ĐANG TẠO ROOT ADMIN KEY...")
        root_key = create_key("root_admin", "admin")
        print(f"\n{'='*60}")
        print(f"⚠️  ROOT ADMIN KEY: {root_key}")
        print(f"⚠️  Hãy lưu key này lại! Dùng nó để tạo các key khác.")
        print(f"{'='*60}\n")
    conn.close()