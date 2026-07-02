from __future__ import annotations

from app.exceptions.base import AppException


class AuthDomainError(AppException):
    code: str = "auth_domain_error"
    detail: str = "Authentication domain error"


class InvalidCredentialsError(AuthDomainError):
    status_code: int = 401
    code: str = "invalid_credentials"
    detail: str = "Invalid email or password"


class AccountBannedError(AuthDomainError):
    status_code: int = 403
    code: str = "account_banned"
    detail: str = "Account is banned"


class AccountLockedError(AuthDomainError):
    status_code: int = 423
    code: str = "account_locked"
    detail: str = "Account is temporarily locked"


class EmailAlreadyRegisteredError(AuthDomainError):
    status_code: int = 409
    code: str = "email_already_registered"
    detail: str = "Email already registered"


class UsernameAlreadyTakenError(AuthDomainError):
    status_code: int = 409
    code: str = "username_already_taken"
    detail: str = "Username already taken"


class PasswordMismatchError(AuthDomainError):
    status_code: int = 422
    code: str = "password_mismatch"
    detail: str = "Passwords do not match"


class InvalidTokenError(AuthDomainError):
    status_code: int = 401
    code: str = "invalid_token"
    detail: str = "Invalid or expired token"


class TokenExpiredError(AuthDomainError):
    status_code: int = 401
    code: str = "token_expired"
    detail: str = "Token has expired"


class SessionNotFoundError(AuthDomainError):
    status_code: int = 404
    code: str = "session_not_found"
    detail: str = "Session not found"


class SessionNotOwnedError(AuthDomainError):
    status_code: int = 403
    code: str = "session_not_owned"
    detail: str = "Session does not belong to user"


class MFARequiredError(AuthDomainError):
    status_code: int = 428
    code: str = "mfa_required"
    detail: str = "Multi-factor authentication required"


class MFAVerificationFailedError(AuthDomainError):
    status_code: int = 422
    code: str = "mfa_verification_failed"
    detail: str = "MFA verification failed"


class MFAAlreadyEnabledError(AuthDomainError):
    status_code: int = 409
    code: str = "mfa_already_enabled"
    detail: str = "MFA is already enabled"


class EmailNotVerifiedError(AuthDomainError):
    status_code: int = 403
    code: str = "email_not_verified"
    detail: str = "Email not verified"


class InvalidResetTokenError(AuthDomainError):
    status_code: int = 400
    code: str = "invalid_reset_token"
    detail: str = "Invalid or expired reset token"


class WeakPasswordError(AuthDomainError):
    status_code: int = 422
    code: str = "weak_password"
    detail: str = "Password does not meet strength requirements"


class RateLimitExceededError(AuthDomainError):
    status_code: int = 429
    code: str = "rate_limit_exceeded"
    detail: str = "Too many requests. Please try again later"
