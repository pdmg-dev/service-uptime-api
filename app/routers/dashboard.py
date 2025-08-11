# app/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.dashboard import get_services_with_latest_status

router = APIRouter(prefix="/status", tags=["Public"])


@router.get("/dashboard")
def dashboard_status(db: Session = Depends(get_db)):
    rows = get_services_with_latest_status(db)
    return [
        {
            "id": service.id,
            "name": service.name,
            "url": service.url,
            "status": status.status,
            "response_time": status.response_time,
            "checked_at": status.checked_at
        }
        for service, status in rows
    ]

