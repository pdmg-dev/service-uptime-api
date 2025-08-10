# app/api/routes/health.py
from fastapi import APIRouter
from app.services import scheduler
import time
from app.core.config import settings

router = APIRouter()

@router.get("/health", summary="Scheduler Health Status")
async def health_check():
    now = time.time()
    last_run = scheduler.last_scheduler_run

    if last_run is None:
        return {"status": "starting", "last_scheduler_run": None}

    seconds_since_last = now - last_run
    healthy = seconds_since_last < (settings.poll_interval_seconds * 2)

    return {
        "status": "healthy" if healthy else "unhealthy",
        "last_scheduler_run": last_run,
        "seconds_since_last_run": round(seconds_since_last, 2)
    }
