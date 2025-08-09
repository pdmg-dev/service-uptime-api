# app/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.service import ServiceDashboardOut
from app.core.dependencies import get_db
from app.services.dashboard import get_service_dashboard

router = APIRouter(prefix="/status", tags=["Public"])

@router.get("/dashboard", response_model=list[ServiceDashboardOut])
def dashboard(db: Session = Depends(get_db)):
    return get_service_dashboard(db, hours=24)