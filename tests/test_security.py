from datetime import datetime, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_not_plaintext():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert hashed.startswith("$2b$")  # формат bcrypt


def test_hash_password_is_salted():
    assert hash_password("secret123") != hash_password("secret123")


def test_verify_password_correct():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("secret123")
    assert verify_password("wrong", hashed) is False


def test_access_token_contains_claims():
    token = create_access_token({"sub": "alice", "role": "employee"})
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == "alice"
    assert payload["role"] == "employee"
    assert "exp" in payload


def test_access_token_has_future_expiry():
    token = create_access_token({"sub": "alice"})
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_access_token_rejects_wrong_secret():
    token = create_access_token({"sub": "alice"})
    wrong_secret = "x" * 40  # достаточной длины, чтобы упасть именно на подписи
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(token, wrong_secret, algorithms=[settings.ALGORITHM])
