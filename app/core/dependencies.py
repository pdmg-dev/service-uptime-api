# app/core/dependencies.py
"""Core dependencies for authentication, authorization, and database access."""

from typing import Generator

from fastapi import Depends, HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import oauth2_scheme
from app.models.user import User


def get_db() -> Generator[Session, None, None]:
    """Provides a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Extracts and validates the current user from the JWT token."""
    # Define a generic credentials error to reuse
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode JWT token using secret key and algorithm
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        # Token has expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except JWTError:
        # Token is invalid or malformed
        raise credentials_exception

    # Query user from DB using email
    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensures the current user has admin privileges."""
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user  # Return user if admin
