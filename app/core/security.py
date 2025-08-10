# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from .config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    # Ensure 'exp' and 'sub' claims are present
    to_encode.update({"exp": expire, "sub": to_encode.get("sub")})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
