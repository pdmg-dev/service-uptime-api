import asyncio
import time
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import logging
from app.models.service import Service, ServiceStatus, ServiceState
from app.services.checker import check_service

logger = logging.getLogger(__name__)


async def store_results_batch(results: list[tuple[int, ServiceState, float | None]]):
    """Persist multiple service check results in one transaction."""
    def _store():
        db: Session = SessionLocal()
        try:
            for service_id, status, response_time in results:
                db.add(ServiceStatus(
                    service_id=service_id,
                    status=status,
                    response_time=response_time,
                ))
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to persist some statuses.")
        finally:
            db.close()

    await asyncio.to_thread(_store)


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

        try:
            # Run checks once per unique URL
            check_tasks = [
                check_service(
                    url,
                    keyword=url_to_services[url][0].keyword,
                    slow_threshold_ms=settings.slow_threshold_ms,
                )
                for url in url_to_services
            ]
            url_results = await asyncio.wait_for(
                asyncio.gather(*check_tasks, return_exceptions=True),
                timeout=settings.poll_timeout_seconds,
            )

            # Prepare batch results
            results_batch = []
            status_counter = Counter()

            for url, result in zip(url_to_services.keys(), url_results):
                if isinstance(result, Exception):
                    logger.exception("[Check Error] %s: %s", url, result)
                    status, response_time = ServiceState.ERROR, None
                else:
                    status, response_time = result

                status_counter[status] += len(url_to_services[url])
                for service in url_to_services[url]:
                    results_batch.append((service.id, status, response_time))

            # Store all results in one DB commit
            await store_results_batch(results_batch)

            elapsed = time.perf_counter() - start
            status_summary = ", ".join(
                f"{count} {status}" for status, count in status_counter.items()
            )
            logger.info(
                f"[Scheduler] Checked {len(services)} services in {elapsed:.2f}s → {status_summary}"
            )
            last_scheduler_run = time.time()

        except asyncio.TimeoutError:
            logger.warning("[Scheduler] Timeout while checking services.")

        await asyncio.sleep(settings.poll_interval_seconds)