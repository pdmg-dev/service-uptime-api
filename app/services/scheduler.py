# app/utils/scheduler.py

import asyncio
import time

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import logging
from app.models.service import Service, ServiceStatus
from app.services.checker import check_service

logger = logging.getLogger(__name__)


async def check_and_store(service: Service) -> dict:
    try:
        status, response_time = await check_service(
            service.url,
            keyword=service.keyword,
            slow_threshold_ms=settings.slow_threshold_ms,
        )

        db = SessionLocal()
        try:
            new_status = ServiceStatus(
                service_id=service.id,
                status=status,
                response_time=response_time,
            )
            db.add(new_status)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to persist status for %s", service.name)
            return {"service": service.name, "status": "ERROR", "response_time": None}
        finally:
            db.close()

        rt_display = f"{response_time:.2f}" if response_time else "N/A"
        logger.info(f"Checked {service.name} → {status} ({rt_display} ms)")

        return {
            "service": service.name,
            "status": status,
            "response_time": response_time,
        }

    except Exception as e:
        logger.exception("[Check Error] %s: %s", service.name, e)
        return {
            "service": service.name,
            "status": "ERROR",
            "response_time": None,
            "error": str(e),
        }


async def poll_services():
    global last_scheduler_run
    while True:
        logger.info("[Scheduler] Checking services...")
        start = time.perf_counter()

        db = SessionLocal()
        try:
            services = db.query(Service).filter(Service.is_active.is_(True)).all()
        except Exception as e:
            logger.exception("[Scheduler Error] Failed to fetch services: %s", e)
            services = []
        finally:
            db.close()

        if not services:
            logger.info("[Scheduler] No active services to check.")
            await asyncio.sleep(settings.poll_interval_seconds)
            continue

        try:
            results = await asyncio.wait_for(
                asyncio.gather(
                    *(check_and_store(s) for s in services), return_exceptions=True
                ),
                timeout=settings.poll_timeout_seconds,
            )

            elapsed = time.perf_counter() - start
            success_count = sum(
                1
                for r in results
                if isinstance(r, dict) and r.get("status") not in ("ERROR", None)
            )
            failure_count = len(services) - success_count
            logger.info(
                f"[Scheduler] Checked {len(services)} services in {elapsed:.2f}s → {success_count} OK, {failure_count} Failed"
            )
            last_scheduler_run = time.time()
        except asyncio.TimeoutError:
            logger.warning("[Scheduler] Timeout while checking services.")

        await asyncio.sleep(settings.poll_interval_seconds)
