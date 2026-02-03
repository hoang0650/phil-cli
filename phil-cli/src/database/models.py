from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from .session import Base

# 1. Bảng Users (Enterprise)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, nullable=True)
    role = Column(String, default="developer")
    organization_id = Column(String, index=True, nullable=True)
    plan_type = Column(String, default="free")
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 2. Bảng Audit Logs (Nhật ký kiểm toán)
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor_id = Column(String, index=True) 
    actor_role = Column(String)

    action = Column(String, index=True)
    resource_target = Column(String)
    
    metadata_info = Column(JSON, nullable=True) 
    
    # Khi nào?
    timestamp = Column(DateTime(timezone=True), server_default=func.now())