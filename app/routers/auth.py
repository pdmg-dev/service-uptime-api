# app/routers/auth.py

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.auth import RegisterIn, RegisterOut, TokenOut
from app.services.auth import login_for_access_token
from app.services.user import register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterOut)
def register(data: RegisterIn, db: Session = Depends(get_db)) -> RegisterOut:
    registered_user = register_user(data, db)
    return RegisterOut.model_validate(registered_user)


@router.post("/login", response_model=TokenOut)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenOut:
    access_token = login_for_access_token(form_data.username, form_data.password, db)
    return TokenOut(access_token=access_token, token_type="bearer")
