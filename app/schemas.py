from pydantic import BaseModel

class ServiceCreate(BaseModel):
    name: str
    url: str

class ServiceOut(BaseModel):
    id: int
    name: str
    url: str

    class Config:
        orm_mode = True