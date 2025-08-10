# app/utils/scheduler.py

import asyncio
import time

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import logging
from app.models.service import Service, ServiceStatus
from app.services.checker import check_service
from collections import defaultdict

logger = logging.getLogger(__name__)


async def store_result(service: Service, status: str, response_time: float | None):
    """Persist the result of a service check to the database."""
    db = SessionLocal()
    try:
        new_status = ServiceStatus(
            service_id=service.id,
            status=status,
            response_time=response_time,
        )
        db.add(new_status)
        db.commit()
        rt_display = f"{response_time:.2f}" if response_time else "N/A"
        logger.info(f"Checked {service.name} → {status} ({rt_display} ms)")
    except Exception:
        db.rollback()
        logger.exception("Failed to persist status for %s", service.name)
    finally:
        db.close()


async def poll_services():
    global last_scheduler_run
    while True:
        logger.info("[Scheduler] Checking services...")
        start = time.perf_counter()

        # Fetch active services
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

        # Group services by URL
        url_to_services = defaultdict(list)
        for service in services:
            url_to_services[service.url].append(service)

        # Check each unique URL once
        try:
            check_tasks = [
                check_service(
                    url,
                    keyword=url_to_services[url][0].keyword,  # assumes same keyword per URL
                    slow_threshold_ms=settings.slow_threshold_ms,
                )
                for url in url_to_services
            ]
            url_results = await asyncio.wait_for(
                asyncio.gather(*check_tasks, return_exceptions=True),
                timeout=settings.poll_timeout_seconds,
            )

            # Map results back to services
            success_count = 0
            failure_count = 0
            for url, result in zip(url_to_services.keys(), url_results):
                if isinstance(result, Exception):
                    logger.exception("[Check Error] %s: %s", url, result)
                    status, response_time = "ERROR", None
                else:
                    status, response_time = result

                for service in url_to_services[url]:
                    await store_result(service, status, response_time)
                    if status not in ("ERROR", None):
                        success_count += 1
                    else:
                        failure_count += 1

            elapsed = time.perf_counter() - start
            logger.info(
                f"[Scheduler] Checked {len(services)} services in {elapsed:.2f}s → {success_count} OK, {failure_count} Failed"
            )
            last_scheduler_run = time.time()

        except asyncio.TimeoutError:
            logger.warning("[Scheduler] Timeout while checking services.")

        await asyncio.sleep(settings.poll_interval_seconds)