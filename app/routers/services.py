# app/routers/services.py

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.service import ServiceCreate, ServiceOut
from app.core.dependencies import get_db
from app.services.checker import check_service
from app.models.service import Service, ServiceState, ServiceStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/", response_model=ServiceOut)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    try:
        db_service = Service(name=service.name, url=str(service.url), is_active=True)
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service
    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate service URL attempted: {service.url}")
        raise HTTPException(status_code=400, detail="Service URL already exists")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating serviec: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Interna server error")


@router.get("/", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/{service_id}/status")
async def check_status(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    status_str, response_time = await check_service(service.url)

    # Convert string to enum
    try:
        status_enum = ServiceState(status_str)
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid status: {status_str}")

    # Store in DB
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
def get_status_history(service_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ServiceStatus)
        .filter(ServiceStatus.service_id == service_id)
        .order_by(ServiceStatus.checked_at.desc())
        .limit(10)
        .all()
    )