# app/schemas.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, EmailStr


class ServiceCreate(BaseModel):
    name: str
    url: HttpUrl


class ServiceOut(BaseModel):
    id: int
    name: str
    url: str

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


class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    username: str
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer" 
