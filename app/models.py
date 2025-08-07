# app/models.py

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Enum
from sqlalchemy.sql import func

from .database import Base
import enum


class ServiceState(str, enum.Enum):
    up = "up"
    down = "down"


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ServiceStatus(Base):
    __tablename__ = "service_status"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(Enum(ServiceState), nullable=False)
    response_time = Column(Float, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
