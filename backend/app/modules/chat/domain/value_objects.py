from __future__ import annotations

from enum import StrEnum


class MessageType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    ORDER = "order"
    OFFER = "offer"
    SYSTEM = "system"


class ConversationStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class ParticipantRole(StrEnum):
    BUYER = "buyer"
    SELLER = "seller"
    SUPPORT = "support"
    ADMIN = "admin"
