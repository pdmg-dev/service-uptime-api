from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.service import Service, ServiceStatus


def get_services_with_latest_status(db: Session):
    # Subquery to find the latest check time per service
    # subquery to get max checked_at per service_id
    latest_time = (
        db.query(
            ServiceStatus.service_id,
            func.max(ServiceStatus.checked_at).label("latest_time"),
        )
        .group_by(ServiceStatus.service_id)
        .subquery()
    )

    # join ServiceStatus to that subquery to get the newest row for each service
    return (
        db.query(Service, ServiceStatus)
        .join(ServiceStatus, ServiceStatus.service_id == Service.id)
        .join(
            latest_time,
            (ServiceStatus.service_id == latest_time.c.service_id)
            & (ServiceStatus.checked_at == latest_time.c.latest_time),
        )
        .order_by(Service.name)
        .all()
    )
