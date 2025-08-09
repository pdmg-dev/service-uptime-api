# app/services/dashboard.py

from datetime import datetime, timedelta, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.service import Service, ServiceStatus


def get_service_dashboard(db: Session, hours: int = 24, user_id: int | None = None):
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = db.query(Service)
    if user_id:
        query = query.filter(Service.user_id == user_id)
    services = query.all()

    result = []
    for service in services:
        entries = (
            db.query(ServiceStatus)
            .filter(
                ServiceStatus.service_id == service.id,
                ServiceStatus.checked_at >= time_threshold,
            )
            .order_by(desc(ServiceStatus.checked_at))
            .all()
        )
        total = len(entries)
        up_count = sum(1 for e in entries if e.status == "UP")
        avg_response = (
            sum(e.response_time for e in entries if e.response_time is not None) / total
            if total > 0
            else None
        )

        result.append(
            {
                "id": service.id,
                "name": service.name,
                "url": service.url,
                "last_checked_at": entries[0].checked_at if entries else None,
                "last_status": entries[0].status if entries else None,
                "uptime_percent": round((up_count / total) * 100, 2)
                if total > 0
                else 0.0,
                "average_response_time_ms": round(avg_response, 2)
                if avg_response
                else None,
            }
        )
    return result
