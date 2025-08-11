# app/services/cleanup.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.service import ServiceStatus
from app.core.logging import logging

logger = logging.getLogger(__name__)

def cleanup_old_statuses(days: int = 30):
    """Delete old ServiceStatus rows beyond retention period."""
    db: Session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = (
            db.query(ServiceStatus)
            .filter(ServiceStatus.checked_at < cutoff)
            .delete(synchronize_session=False)
        )
        db.commit()
        if deleted:
            logger.info(f"[Cleanup] Deleted {deleted} old service status records.")
    except Exception:
        db.rollback()
        logger.exception("[Cleanup] Failed to delete old statuses.")
    finally:
        db.close()
