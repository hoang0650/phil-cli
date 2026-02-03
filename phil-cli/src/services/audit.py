from sqlalchemy.orm import Session
from src.database.models import AuditLog

def record_audit_log(
    db: Session, 
    actor: str, 
    role: str, 
    action: str, 
    target: str = None, 
    details: dict = None
):

    try:
        log_entry = AuditLog(
            actor_id=actor,
            actor_role=role,
            action=action,
            resource_target=target,
            metadata_info=details
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        print(f"[AUDIT] Recorded: {actor} -> {action}")
    except Exception as e:
        print(f"[AUDIT ERROR] Failed to record log: {e}")
        # Không raise error để tránh làm hỏng trải nghiệm user