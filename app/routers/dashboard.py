# app/routers/dashboard.py
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.dashboard import (
    get_services_with_latest_status as latest_service_statuses,
)

router = APIRouter(prefix="/status", tags=["Public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/api")
def dashboard_api(db: Session = Depends(get_db)):
    """Return latest status for each service as JSON."""
    services = latest_service_statuses(db)
    return [
        {
            "id": s.id,
            "name": s.name,
            "url": s.url,
            "status": st.status.value,
            "response_time": st.response_time,
            "checked_at": st.checked_at,
        }
        for s, st in services
    ]


# ---------- HTML Dashboard ----------
@router.get("/dashboard")
def show_dashboard(request: Request, db: Session = Depends(get_db)):
    """Render HTML dashboard with latest service statuses."""
    services = latest_service_statuses(db)
    rows = [
        {
            "name": s.name,
            "status": st.status.value,
            "response_time": st.response_time,
            "checked_at": st.checked_at,
            "status_color": color_map(st.status.value),
        }
        for s, st in services
    ]
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "services": rows},
    )


def color_map(status: str) -> str:
    """Map status values to Bulma color tags."""
    return {
        "UP": "success",
        "SLOW": "warning",
        "LIMITED": "warning",
        "REDIRECT": "info",
        "FORBIDDEN": "danger",
        "DOWN": "danger",
        "UNREACHABLE": "dark",
        "INVALID_CONTENT": "danger",
        "ERROR": "danger",
    }.get(status, "light")
