# app/routers/services.py

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.service import Service, ServiceState, ServiceStatus
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceOut
from app.services.checker import check_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=ServiceOut)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceOut:
    """Creates a new service entry for the authenticated user."""
    try:
        db_service = Service(
            name=service.name,
            url=str(service.url),
            is_active=True,
            user_id=current_user.id,
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service
    except IntegrityError:
        db.rollback()
        logger.warning("Duplicate service URL attempted: %s", service.url)
        raise HTTPException(status_code=400, detail="Service URL already exists")
    except Exception:
        db.rollback()
        logger.exception("Error creating service")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=list[ServiceOut])
def list_services(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ServiceOut]:
    """Lists all services owned by the authenticated user."""
    return db.query(Service).filter(Service.user_id == current_user.id).all()


@router.get("/{service_id}/status")
async def check_status(service_id: int, db: Session = Depends(get_db)) -> dict:
    """Checks the current status of a specific service by ID."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Perform async status check
    status_str, response_time = await check_service(service.url)

    # Validate status string against enum
    try:
        status_enum = ServiceState(status_str)
    except ValueError:
        logger.error("Invalid status returned by checker: %s", status_str)
        raise HTTPException(status_code=500, detail=f"Invalid status: {status_str}")

    # Persist status result
    new_status = ServiceStatus(
        service_id=service.id,
        status=status_enum,
        response_time=response_time,
    )
    db.add(new_status)
    db.commit()

    return {
        "service": service.name,
        "status": status_enum.value,
        "response_time_ms": response_time,
    }


@router.get("/{service_id}/status/history")
def get_status_history(
    service_id: int, db: Session = Depends(get_db)
) -> list[ServiceStatus]:
    """Retrieves the 10 most recent status checks for a given service."""
    return (
        db.query(ServiceStatus)
        .filter(ServiceStatus.service_id == service_id)
        .order_by(ServiceStatus.checked_at.desc())
        .limit(10)
        .all()
    )
