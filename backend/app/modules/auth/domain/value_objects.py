from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class UserId:
    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Phone:
    value: str

    def __post_init__(self) -> None:
        pattern = r"^\+?[1-9]\d{1,14}$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid phone number: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PasswordHash:
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TokenHash:
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionId:
    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class DeviceInfo:
    ip_address: str | None = None
    user_agent: str | None = None
    device_id: str | None = None


@dataclass(frozen=True)
class MFAVerification:
    code: str
    backup_code: str | None = None


class Authn:
    """Namespace for authentication-related constants."""

    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 30
    RESET_TOKEN_EXPIRY_HOURS: int = 1
    SESSION_CLEANUP_DAYS: int = 90
    BACKUP_CODES_COUNT: int = 8
