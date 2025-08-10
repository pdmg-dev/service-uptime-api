# app/models/service.py

import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ServiceState(str, enum.Enum):
    """Enum representing possible states of a monitored service."""

    up = "UP"
    down = "DOWN"
    slow = "SLOW"
    limited = "LIMITED"
    forbidden = "FORBIDDEN"
    unreachable = "UNREACHABLE"
    invalid_content = "INVALID_CONTENT"


class Service(Base):
    """ORM model representing a monitored service."""

    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    keyword = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="services")
    statuses = relationship(
        "ServiceStatus",
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ServiceStatus(Base):
    """ORM model representing the status check result of a service."""

    __tablename__ = "service_status"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(Enum(ServiceState), nullable=False)
    response_time = Column(Float, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    service = relationship("Service", back_populates="statuses", passive_deletes=True)
