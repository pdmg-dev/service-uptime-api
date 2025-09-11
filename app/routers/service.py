# app/routers/service.py

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.service import (
    ServiceIn,
    ServiceOut,
    ServiceStatusOut,
    ServiceUpdate,
)
from app.services.service import (
    check_service_status as check_status,
)
from app.services.service import (
    delete_service,
    get_service_status_history,
    list_services,
    register_service_url,
    update_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=ServiceOut)
def register_service(
    data: ServiceIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceOut:
    registered_service = register_service_url(data, current_user.id, db)
    return ServiceOut.model_validate(registered_service)


@router.get("/", response_model=list[ServiceOut])
def view_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceOut]:
    return list_services(current_user.id, db)


@router.patch("/{service_id}/", response_model=ServiceOut)
def update_service_details(
    data: ServiceUpdate,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_service = update_service(data, service_id, db)
    return ServiceOut.model_validate(updated_service)


@router.delete("/{service_id}/")
def delete_active_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_service(service_id, db)


@router.get("/{service_id}/status", response_model=ServiceStatusOut)
async def check_service_status(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceStatusOut:
    service_status = await check_status(service_id, db)
    return ServiceStatusOut.model_validate(service_status)


@router.get(
    "/{service_id}/status/history", response_model=list[ServiceStatusOut]
)
def view_service_status_history(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceStatusOut]:
    return get_service_status_history(service_id, db)
