# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import (create_access_token, get_password_hash,
                               verify_password)
from app.models.user import User
from app.schemas.auth import RegisterIn, RegisterOut, TokenOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterOut)
def register(user_in: RegisterIn, db: Session = Depends(get_db)) -> RegisterOut:
    """Registers a new user if username and email are unique."""
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return RegisterOut(user.username, user.email)


@router.post("/login", response_model=TokenOut)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> TokenOut:
    """Authenticates a user and returns a JWT access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.email)})
    return TokenOut(access_token=access_token, token_type="bearer")
