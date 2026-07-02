from __future__ import annotations

from typing import Any


class AppException(Exception):
    status_code: int = 500
    code: str = "internal_error"
    detail: str = "An unexpected error occurred"
    headers: dict[str, str] | None = None

    def __init__(
        self,
        detail: str | None = None,
        code: str | None = None,
        headers: dict[str, str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        if detail:
            self.detail = detail
        if code:
            self.code = code
        if headers:
            self.headers = headers
        self.context = context or {}
        super().__init__(self.detail)


class BadRequestError(AppException):
    status_code: int = 400
    code: str = "bad_request"
    detail: str = "Bad request"


class ValidationError(AppException):
    status_code: int = 422
    code: str = "validation_error"
    detail: str = "Validation failed"


class AuthenticationError(AppException):
    status_code: int = 401
    code: str = "authentication_error"
    detail: str = "Authentication required"
    headers: dict[str, str] | None = {"WWW-Authenticate": "Bearer"}


class AuthorizationError(AppException):
    status_code: int = 403
    code: str = "authorization_error"
    detail: str = "Insufficient permissions"


class NotFoundError(AppException):
    status_code: int = 404
    code: str = "not_found"
    detail: str = "Resource not found"


class ConflictError(AppException):
    status_code: int = 409
    code: str = "conflict"
    detail: str = "Resource already exists"


class RateLimitError(AppException):
    status_code: int = 429
    code: str = "rate_limit_exceeded"
    detail: str = "Too many requests"


class BusinessRuleViolation(AppException):
    status_code: int = 422
    code: str = "business_rule_violation"
    detail: str = "Business rule violation"


class ExternalServiceError(AppException):
    status_code: int = 502
    code: str = "external_service_error"
    detail: str = "External service error"


class ServiceUnavailableError(AppException):
    status_code: int = 503
    code: str = "service_unavailable"
    detail: str = "Service temporarily unavailable"
