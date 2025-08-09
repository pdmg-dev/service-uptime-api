# app/routers/services.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas
from ..database import get_db
from ..utils.aggregator import get_service_dashboard
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["services"])

@router.post("/", response_model=schemas.ServiceOut)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    try:
        db_service = models.Service(name=service.name, url=service.url)
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


@router.get("/", response_model=list[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()


@router.get("/{service_id}/status")
async def check_status(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    from ..utils.healthcheck import check_service

    status_str, response_time = await check_service(service.url)

    # Convert string to enum
    try:
        status_enum = models.ServiceState(status_str)
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid status: {status_str}")

    # Store in DB
    new_status = models.ServiceStatus(
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
        db.query(models.ServiceStatus)
        .filter(models.ServiceStatus.service_id == service_id)
        .order_by(models.ServiceStatus.checked_at.desc())
        .limit(10)
        .all()
    )


@router.get("/dashboard", response_model=list[schemas.ServiceDashboardOut])
def dashboard(db: Session = Depends(get_db)):
    return get_service_dashboard(db, hours=24)
