# tests/test_security.py
from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify():
    password = "secure123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_create_access_token_contains_exp_and_sub():
    data = {"sub": "user123"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )
    assert "exp" in decoded
    assert decoded["sub"] == "user123"
