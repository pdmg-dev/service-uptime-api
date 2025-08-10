# app/services/user.py


from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user import get_user_by_email, get_user_by_username, save_user
from app.schemas.auth import RegisterIn
from app.core.logging import logging

logger = logging.getLogger(__name__)


def register_user(data: RegisterIn, db: Session) -> User:
    if get_user_by_username(data.username, db):
        logger.warning(
            f"Registration failed: Username '{data.username}' already exists."
        )
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(data.email, db):
        logger.warning(f"Registration failed: Email '{data.email}' already exists.")
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(data.password)
    user = User(
        **data.model_dump(exclude="password"),
        hashed_password=hashed_password,
    )
    saved_user = save_user(user, db)
    logger.info(
        f"New user registered: username='{user.username}', email='{user.email}'"
    )
    return saved_user
