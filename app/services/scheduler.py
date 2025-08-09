# app/utils/scheduler.py

import asyncio
from app.core.logging import logging
from app.core.database import SessionLocal
from app.models.service import Service, ServiceStatus
from app.services.checker import check_service
from app.core.config import settings

logger = logging.getLogger(__name__)


async def check_and_store(service: Service):
    try:
        status, response_time = await check_service(service.url)
        with SessionLocal() as db:
            new_status = ServiceStatus(
                service_id=service.id,
                status=status,
                response_time=response_time,
            )
            db.add(new_status)
            db.commit()
        rt_display = f"{response_time:.2f}" if response_time else "N/A"
        logger.info(f"Checked {service.name} → {status} ({rt_display} ms)")
    except Exception as e:
        logger.error(f"[Check Error] {service.name}: {e}")


async def poll_services():
    while True:
        services = []
        logger.info("[Scheduler] Checking services...")
        try:
            with SessionLocal() as db:
                services = db.query(Service).filter(Service.is_active.is_(True)).all()
        except Exception as e:
            logger.error(f"[Scheduler Error] {e}")
        if services:
            await asyncio.gather(*(check_and_store(s) for s in services))
        else:
            logger.info("[Scheduler] No active services to check.")
        await asyncio.sleep(settings.poll_interval_seconds)
