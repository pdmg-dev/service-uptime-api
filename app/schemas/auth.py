# app/schemas/auth.py

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegisterOut(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    username: str
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
