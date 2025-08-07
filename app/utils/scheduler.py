# app/utils/scheduler.py

import asyncio
import logging
import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Service, ServiceStatus
from .healthcheck import check_service

load_dotenv()
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 60))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def poll_services():
    while True:
        logger.info("[Scheduler] Checking services...")
        try:
            db: Session = SessionLocal()
            services = db.query(Service).all()
            for service in services:
                status, response_time = await check_service(service.url)
                new_status = ServiceStatus(
                    service_id=service.id,
                    status=status,
                    response_time=response_time,
                )
                db.add(new_status)
                db.commit()
                logger.info(f"Checked {service.name} → {status} ({response_time} ms)")
        except Exception as e:
            logger.error(f"[Scheduler Error] {e}")
        finally:
            db.close()
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
