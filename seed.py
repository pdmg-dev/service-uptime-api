"""
Seeder script for populating test users and services into the Service Uptime API.
Each user gets a different mix of service states.
"""

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

# --- Define 3 seeded users ---
SEED_USERS = [
    RegisterIn(username="alice", email="alice@example.com", password="alicepass123"),
    RegisterIn(username="bob", email="bob@example.com", password="bobpass123"),
    RegisterIn(username="carol", email="carol@example.com", password="carolpass123"),
]

# --- Assign different service scenarios to each user ---
USER_SERVICES = {
    "alice@example.com": [
        # Mostly healthy
        ServiceIn(name="Google", url="https://www.google.com", keyword="Google"),
        ServiceIn(name="GitHub", url="https://github.com", keyword="GitHub"),
    ],
    "bob@example.com": [
        # Slow + redirect + forbidden
        ServiceIn(name="Slow API", url="https://deelay.me/3000/https://example.com"),
        ServiceIn(name="Redirect Test", url="https://httpbingo.org/status/302"),
        ServiceIn(name="Forbidden Test", url="https://httpbingo.org/status/403"),
    ],
    "carol@example.com": [
        # Rate limit, invalid content, unreachable
        ServiceIn(name="Rate Limit Test", url="https://httpbingo.org/status/429"),
        ServiceIn(
            name="Invalid Content",
            url="https://example.com",
            keyword="nonexistent-keyword",
        ),
        ServiceIn(name="Unreachable", url="https://nonexistent.domain.fake"),
    ],
}


def seed() -> None:
    """Create three demo users each with different service states."""
    db = SessionLocal()
    try:
        for user_in in SEED_USERS:
            user = db.query(User).filter(User.email == user_in.email).first()
            if not user:
                user = register_user(user_in, db)
                logger.info("Created seed user: %s", user.username)
            else:
                logger.info("Seed user already exists: %s", user.username)

            for service in USER_SERVICES[user_in.email]:
                try:
                    register_service_url(service, user.id, db)
                    logger.info("Seeded %s for %s", service.name, user.username)
                except Exception as exc:
                    logger.warning("Skipped %s for %s: %s", service.name, user.username, exc)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
