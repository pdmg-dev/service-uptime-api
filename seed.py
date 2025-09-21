"""Seeder script for populating test services into the Service Uptime API."""

import logging

from app.core.database import Base, SessionLocal, engine
from app.models.user import User
from app.schemas.auth import RegisterIn
from app.schemas.service import ServiceIn
from app.services.service import register_service_url
from app.services.user import register_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

SEED_USER = RegisterIn(
    username="user",
    email="user@example.com",
    password="userpass123",
)

# Reliable endpoints to trigger each ServiceState
SERVICES_TO_SEED = [
    ServiceIn(name="Google", url="https://www.google.com", keyword="Google"),
    ServiceIn(name="GitHub", url="https://github.com", keyword="GitHub"),
    ServiceIn(name="Slow API", url="https://httpbin.org/delay/3"),
    ServiceIn(name="Redirect Test", url="https://httpbin.org/status/302"),
    ServiceIn(name="Forbidden Test", url="https://httpbin.org/status/403"),
    ServiceIn(name="Rate Limit Test", url="https://httpbin.org/status/429"),
    ServiceIn(
        name="Invalid Content",
        url="https://example.com",
        keyword="nonexistent-keyword",
    ),
    ServiceIn(name="Unreachable", url="https://nonexistent.domain.fake"),
]


def seed() -> None:
    """Create a demo user and a variety of services to exercise all states."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == SEED_USER.email).first()
        if not user:
            user = register_user(SEED_USER, db)
            logger.info("Created seed user: %s", user.username)
        else:
            logger.info("Seed user already exists: %s", user.username)

        for service in SERVICES_TO_SEED:
            try:
                register_service_url(service, user.id, db)
                logger.info("Seeded service: %s", service.name)
            except Exception as exc:
                logger.warning("Skipped %s: %s", service.name, exc)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
