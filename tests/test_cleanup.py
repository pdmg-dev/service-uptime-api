from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from app.models.service import Service, ServiceState, ServiceStatus
from app.services.cleanup import cleanup_old_statuses


@pytest.fixture
def seed_old_status(db: Session):
    # Create a dummy service
    service = Service(name="Test", url="https://example.com", user_id=1)
    db.add(service)
    db.commit()

    # Add old and recent statuses
    old_time = datetime.now(timezone.utc) - timedelta(days=31)
    recent_time = datetime.now(timezone.utc) - timedelta(days=5)

    db.add_all(
        [
            ServiceStatus(
                service_id=service.id,
                status=ServiceState.UP,
                response_time=123,
                checked_at=old_time,
            ),
            ServiceStatus(
                service_id=service.id,
                status=ServiceState.UP,
                response_time=456,
                checked_at=recent_time,
            ),
        ]
    )
    db.commit()
    return service.id


def test_cleanup_removes_old_statuses(db: Session, seed_old_status):
    # Confirm both statuses exist before cleanup
    initial_count = db.query(ServiceStatus).count()
    assert initial_count == 2

    # Run cleanup
    cleanup_old_statuses(days=30)

    db.expire_all()  # Clear cached state
    remaining = db.query(ServiceStatus).all()
    # Only the recent one should remain
    remaining = db.query(ServiceStatus).all()
    assert len(remaining) == 1
    assert remaining[0].response_time == 456
