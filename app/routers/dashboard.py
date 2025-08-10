# app/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.service import ServiceDashboardOut
from app.services.dashboard import get_service_dashboard

router = APIRouter(prefix="/status", tags=["Public"])


@router.get("/dashboard", response_model=list[ServiceDashboardOut])
def dashboard(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceDashboardOut]:
    """Returns a dashboard summary of service statuses for the current user."""
    return get_service_dashboard(db, hours=hours, user_id=current_user.id)
