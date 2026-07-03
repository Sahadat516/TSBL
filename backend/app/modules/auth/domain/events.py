from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(kw_only=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.event_name = self.__class__.__name__

    def to_payload(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at,
            **{k: v for k, v in self.__dict__.items() if k not in ("event_id", "event_name", "occurred_at")},
        }


@dataclass
class UserRegistered(DomainEvent):
    user_id: str
    email: str
    username: str


@dataclass
class UserLoggedIn(DomainEvent):
    user_id: str
    ip_address: str
    device_id: str | None = None


@dataclass
class UserLoggedOut(DomainEvent):
    user_id: str
    session_id: str


@dataclass
class PasswordChanged(DomainEvent):
    user_id: str


@dataclass
class PasswordResetRequested(DomainEvent):
    user_id: str
    email: str


@dataclass
class PasswordResetCompleted(DomainEvent):
    user_id: str


@dataclass
class EmailVerified(DomainEvent):
    user_id: str
    email: str


@dataclass
class EmailVerificationRequested(DomainEvent):
    user_id: str
    email: str


@dataclass
class MFAEnabled(DomainEvent):
    user_id: str
    mfa_type: str


@dataclass
class MFADisabled(DomainEvent):
    user_id: str


@dataclass
class MFAVerified(DomainEvent):
    user_id: str


@dataclass
class ProfileUpdated(DomainEvent):
    user_id: str
    changes: dict[str, Any]


@dataclass
class AccountLocked(DomainEvent):
    user_id: str
    reason: str


@dataclass
class AccountUnlocked(DomainEvent):
    user_id: str


@dataclass
class SessionRevoked(DomainEvent):
    user_id: str
    session_id: str


@dataclass
class AllSessionsRevoked(DomainEvent):
    user_id: str
    except_session_id: str | None = None


@dataclass
class RateLimitTriggered(DomainEvent):
    user_id: str | None
    ip_address: str
    endpoint: str
