from sqlalchemy import select, func
from sqlalchemy.orm import aliased, Session
from app.models.service import Service, ServiceStatus

def get_services_with_latest_status(db: Session):
    # Subquery to find the latest check time per service
    latest_status_sq = (
        select(
            ServiceStatus.service_id,
            func.max(ServiceStatus.checked_at).label("latest_checked_at")
        )
        .group_by(ServiceStatus.service_id)
        .subquery()
    )

    # Alias to join the actual latest ServiceStatus rows
    ss_alias = aliased(ServiceStatus)

    query = (
        db.query(Service, ss_alias)
        .join(
            latest_status_sq,
            Service.id == latest_status_sq.c.service_id
        )
        .join(
            ss_alias,
            (ss_alias.service_id == latest_status_sq.c.service_id) &
            (ss_alias.checked_at == latest_status_sq.c.latest_checked_at)
        )
        .order_by(Service.name)
    )

    return query.all()
