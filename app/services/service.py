# app/services/service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.service import Service, ServiceState, ServiceStatus
from app.repositories.service import (
    get_service_by_id,
    get_service_by_url_and_user,
    get_services_by_user_id,
    get_status_history,
    save_service,
    save_status,
    update,
    delete,
)
from app.schemas.service import ServiceIn, ServiceOut, ServiceUpdate
from app.services.checker import check_service


def register_service_url(data: ServiceIn, user_id: int, db: Session) -> Service:
    service = get_service_by_url_and_user(str(data.url), user_id, db)
    if service:
        raise HTTPException(status_code=400, detail="Service already regsitered")
    new_service = Service(name=data.name, url=str(data.url), user_id=user_id)
    saved_service = save_service(new_service, db)
    return saved_service


def list_services(user_id: int, db: Session) -> list[ServiceOut]:
    services = get_services_by_user_id(user_id, db)
    if not services:
        raise HTTPException(status_code=404, detail="No registered services")
    return services


def update_service(data: ServiceUpdate, service_id: int, db: Session) -> ServiceOut:
    service = get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(status_code=404, detail="Service not registered")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    updated_service = update(service, db)
    return updated_service


def delete_service(service_id: int, db: Session) -> None:
    service = get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(status_code=404, detail="Service not registered")
    return delete(service, db)


async def check_service_status(service_id: int, db: Session):
    service = get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(status_code=404, detail="Service not registered")
    status_str, response_time = await check_service(service.url)
    try:
        status_enum = ServiceState(status_str)
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid status: {status_str}")
    new_status = ServiceStatus(
        status=status_enum, response_time=response_time, service_id=service_id
    )
    saved_status = save_status(new_status, db)
    return saved_status


def get_service_status_history(service_id: int, db: Session):
    service = get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(status_code=404, detail="Service not registered")
    return get_status_history(service_id, db)
