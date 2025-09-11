# app/repositories/user.py

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_username(username: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def save_user(user: User, db: Session) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
