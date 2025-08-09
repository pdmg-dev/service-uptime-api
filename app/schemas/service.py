# app/schemas/service.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class ServiceCreate(BaseModel):
    name: str
    url: HttpUrl


class ServiceOut(BaseModel):
    id: int
    name: str
    url: str
    is_active: bool
    user_id: int

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
