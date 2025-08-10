# app/repositories/user.py

from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


def save_user(username: str, email: str, hashed_password: str, db: Session) -> User:
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
