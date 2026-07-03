from __future__ import annotations

from enum import StrEnum


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class ReviewTargetType(StrEnum):
    PRODUCT = "product"
    SELLER = "seller"
    SERVICE = "service"


class VoteType(StrEnum):
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    REPORT = "report"
