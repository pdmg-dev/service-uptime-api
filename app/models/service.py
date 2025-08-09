# app/models/service.py

import enum

from sqlalchemy import (Boolean, Column, DateTime, Enum, Float, ForeignKey,
                        Integer, String)
from sqlalchemy.sql import func

from app.core.database import Base


class ServiceState(str, enum.Enum):
    up = "UP"
    down = "DOWN"
    slow = "SLOW"
    limited = "LIMITED"
    forbidden = "FORBIDDEN"
    unreachable = "UNREACHABLE"
    invalid_content = "INVALID_CONTENT"


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyword = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ServiceStatus(Base):
    __tablename__ = "service_status"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(Enum(ServiceState), nullable=False)
    response_time = Column(Float, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
