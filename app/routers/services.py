# app/routers/services.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas

router = APIRouter(prefix="/services", tags=["services"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.ServiceOut)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = models.Service(name=service.name, url=service.url)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.get("/", response_model=list[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()


@router.get("/{service_id}/status")
async def check_status(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    from ..utils.healthcheck import check_service

    status, response_time = await check_service(service.url)

    # Store in DB
    new_status = models.ServiceStatus(
        service_id=service.id, status=status, response_time=response_time
    )
    db.add(new_status)
    db.commit()

    return {
        "service": service.name,
        "status": status,
        "response_time_ms": response_time,
    }
