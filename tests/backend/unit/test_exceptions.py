from __future__ import annotations

import pytest

from app.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestAppExceptions:
    def test_bad_request_error(self):
        exc = BadRequestError(detail="Invalid input")
        assert exc.status_code == 400
        assert exc.code == "bad_request"
        assert exc.detail == "Invalid input"

    def test_authentication_error(self):
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert exc.code == "authentication_error"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_authorization_error(self):
        exc = AuthorizationError(detail="Insufficient role")
        assert exc.status_code == 403
        assert exc.detail == "Insufficient role"

    def test_not_found_error(self):
        exc = NotFoundError(detail="User not found")
        assert exc.status_code == 404
        assert exc.detail == "User not found"

    def test_conflict_error(self):
        exc = ConflictError(detail="Email already registered")
        assert exc.status_code == 409

    def test_validation_error_with_context(self):
        exc = ValidationError(detail="Invalid email", context={"field": "email"})
        assert exc.status_code == 422
        assert exc.context == {"field": "email"}

    def test_rate_limit_error(self):
        exc = RateLimitError()
        assert exc.status_code == 429

    def test_exception_chain(self):
        exc = BadRequestError()
        assert isinstance(exc, Exception)
