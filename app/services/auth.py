# app/services/auth.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user import get_user_by_username
from app.core.logging import logging

logger = logging.getLogger(__name__)


def authenticate_user(username: str, password: str, db: Session) -> User:
    user = get_user_by_username(username, db)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed for username='{username}'")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info(f"User authenticated: username='{username}'")
    return user


def login_for_access_token(username: str, password: str, db: Session) -> str:
    user = authenticate_user(username, password, db)
    token = create_access_token(data={"sub": (user.email)})
    logger.info(f"Access token issued for user='{user.username}'")
    return token
