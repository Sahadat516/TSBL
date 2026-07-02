from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_token_expired,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("testpassword")
        assert isinstance(hashed, str)
        assert hashed != "testpassword"

    def test_verify_password_correct(self):
        hashed = hash_password("correctpassword")
        assert verify_password("correctpassword", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        h1 = hash_password("password")
        h2 = hash_password("password")
        assert h1 != h2


class TestJWTToken:
    def test_create_access_token(self):
        token = create_access_token(subject="user-123")
        assert isinstance(token, str)
        payload = decode_token(token)
        assert payload.get("sub") == "user-123"
        assert payload.get("type") == "access"

    def test_create_access_token_with_extra_claims(self):
        token = create_access_token(subject="user-123", extra_claims={"role": "admin"})
        payload = decode_token(token)
        assert payload.get("role") == "admin"

    def test_create_refresh_token(self):
        token = create_refresh_token(subject="user-123")
        payload = decode_token(token)
        assert payload.get("type") == "refresh"
        assert payload.get("sub") == "user-123"

    def test_decode_invalid_token(self):
        payload = decode_token("invalid-token")
        assert payload == {}

    def test_token_expiry(self):
        payload = {"exp": (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()}
        assert is_token_expired(payload) is True

    def test_token_not_expired(self):
        payload = {"exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()}
        assert is_token_expired(payload) is False

    def test_token_no_expiry(self):
        assert is_token_expired({}) is True
