# app/models/service.py
"""SQLAlchemy models for monitored services and their status checks."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ServiceState(str, enum.Enum):
    """Possible states returned by a service health check."""

    UP = "UP"
    DOWN = "DOWN"
    SLOW = "SLOW"
    LIMITED = "LIMITED"
    FORBIDDEN = "FORBIDDEN"
    UNREACHABLE = "UNREACHABLE"
    INVALID_CONTENT = "INVALID_CONTENT"
    REDIRECT = "REDIRECT"
    ERROR = "ERROR"


class Service(Base):
    """A service (website/API) monitored for uptime and performance."""

    __tablename__ = "services"
    __table_args__ = (UniqueConstraint("url", "user_id", name="uniq_user_service"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="services")  # noqa: F821
    statuses: Mapped[list["ServiceStatus"]] = relationship(
        back_populates="service",
        cascade="all, delete",
        passive_deletes=True,
    )


class ServiceStatus(Base):
    """Result of a single status check for a service."""

    __tablename__ = "service_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ServiceState] = mapped_column(Enum(ServiceState), nullable=False)
    response_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service: Mapped[Service] = relationship(
        back_populates="statuses",
        passive_deletes=True,
    )
