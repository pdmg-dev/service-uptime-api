# app/repositories/service.py

from typing import Optional

from sqlalchemy.orm import Session

from app.models.service import Service, ServiceStatus


def get_service_by_url_and_user(
    url: str, user_id: int, db: Session
) -> Service | None:
    return (
        db.query(Service)
        .filter(Service.url == url, Service.user_id == user_id)
        .first()
    )


def get_services_by_user_id(
    user_id: int, db: Session
) -> Optional[list[Service]]:
    return db.query(Service).filter(Service.user_id == user_id).all()


def get_service_by_id(service_id: str, db: Session) -> Optional[Service]:
    return db.query(Service).filter(Service.id == service_id).first()


def get_status_history(service_id: int, db: Session):
    return (
        db.query(ServiceStatus)
        .filter(ServiceStatus.service_id == service_id)
        .order_by(ServiceStatus.checked_at.desc())
        .limit(10)
        .all()
    )


def save_service(service: Service, db: Session) -> Service:
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def save_status(service_status: ServiceStatus, db: Session) -> Service:
    db.add(service_status)
    db.commit()
    return service_status


def update(service: Service, db: Session) -> Service:
    db.commit()
    db.refresh(service)
    return service


def delete(service: Service, db: Session) -> None:
    db.delete(service)
    db.commit()
