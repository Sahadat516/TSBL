from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class DisplayName:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Display name cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Display name must be 100 characters or fewer")


@dataclass(frozen=True)
class StoreSlug:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Store slug cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Store slug must be 200 characters or fewer")


@dataclass(frozen=True)
class Bio:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > 2000:
            raise ValueError("Biography must be 2000 characters or fewer")


class ProfileVisibility:
    PUBLIC = "public"
    PRIVATE = "private"
    CONTACTS_ONLY = "contacts_only"

    VALID_VALUES = {PUBLIC, PRIVATE, CONTACTS_ONLY}

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.VALID_VALUES


class StoreStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"

    VALID_VALUES = {ACTIVE, INACTIVE, SUSPENDED, CLOSED}

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.VALID_VALUES
