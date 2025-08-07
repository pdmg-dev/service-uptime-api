# app/schemas.py

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    name: str
    url: str


class ServiceOut(BaseModel):
    id: int
    name: str
    url: str

    model_config = ConfigDict(from_attributes=True)
