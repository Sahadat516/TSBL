from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class EmailMessage:
    to: str
    subject: str
    body: str
    html_body: str | None = None
    cc: list[str] | None = None
    bcc: list[str] | None = None


class EmailSender(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> None: ...


class MFACodeGenerator(ABC):
    @abstractmethod
    def generate_secret(self) -> str: ...

    @abstractmethod
    def generate_qr_code_url(self, secret: str, email: str, issuer: str) -> str: ...

    @abstractmethod
    def verify_code(self, secret: str, code: str) -> bool: ...

    @abstractmethod
    def generate_backup_codes(self, count: int = 8) -> list[str]: ...


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, event_name: str, payload: dict[str, Any]) -> None: ...


class RateLimiter(ABC):
    @abstractmethod
    async def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool: ...

    @abstractmethod
    async def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int: ...

    @abstractmethod
    async def reset(self, key: str) -> None: ...
