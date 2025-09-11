# app/schemas/service.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.models.service import ServiceState


class ServiceIn(BaseModel):
    name: str
    url: HttpUrl


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = True


class ServiceOut(BaseModel):
    id: int
    name: str
    url: str
    is_active: bool
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceStatusOut(BaseModel):
    id: int
    status: ServiceState
    response_time: Optional[float] = None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceDashboardOut(BaseModel):
    id: int
    name: str
    url: str
    last_checked_at: datetime | None
    last_status: str | None
    uptime_percent: float
    average_response_time_ms: float | None

    model_config = ConfigDict(from_attributes=True)
