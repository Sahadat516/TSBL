from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(__import__("uuid").uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now())


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
