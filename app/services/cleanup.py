# app/services/cleanup.py
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import logging
from app.models.service import ServiceStatus

logger = logging.getLogger(__name__)


def cleanup_old_statuses(days: int = 30):
    """Delete old ServiceStatus rows beyond retention period."""
    db: Session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Fetch records to delete
        old_statuses = (
            db.query(ServiceStatus)
            .filter(ServiceStatus.checked_at < cutoff)
            .all()
        )
        deleted_count = len(old_statuses)

        # Delete each record explicitly
        for status in old_statuses:
            db.delete(status)

        db.commit()

        if deleted_count:
            logger.info(
                f"[Cleanup] Deleted {deleted_count} old service status records."
            )
        else:
            logger.info("[Cleanup] No old service status records found.")
    except Exception:
        db.rollback()
        logger.exception("[Cleanup] Failed to delete old statuses.")
    finally:
        db.close()
