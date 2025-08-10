# app/routes/health.py
import time

from fastapi import APIRouter

from app.core.config import settings
from app.services import scheduler

router = APIRouter()


@router.get("/health", summary="Scheduler Health Status")
async def health_check() -> dict:
    """Returns the health status of the background scheduler."""
    now = time.time()
    last_run = scheduler.last_scheduler_run

    if last_run is None:
        # Scheduler hasn't run yet
        return {"status": "starting", "last_scheduler_run": None}

    seconds_since_last = now - last_run
    healthy = seconds_since_last < (settings.poll_interval_seconds * 2)

    return {
        "status": "healthy" if healthy else "unhealthy",
        "last_scheduler_run": last_run,
        "seconds_since_last_run": round(seconds_since_last, 2),
    }
