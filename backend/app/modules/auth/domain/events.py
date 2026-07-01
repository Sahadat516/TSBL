import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserRegistered(DomainEvent):
    user_id: str
    email: str
    username: str


@dataclass
class UserLoggedIn(DomainEvent):
    user_id: str
    ip_address: str


@dataclass
class UserLoggedOut(DomainEvent):
    user_id: str


@dataclass
class PasswordReset(DomainEvent):
    user_id: str


@dataclass
class EmailVerified(DomainEvent):
    user_id: str
    email: str
