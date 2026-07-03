from __future__ import annotations

from enum import StrEnum


class EscrowStatus(StrEnum):
    PENDING_FUNDING = "pending_funding"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class MilestoneStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    DISPUTED = "disputed"


class DisputeStatus(StrEnum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED_BUYER = "resolved_buyer"
    RESOLVED_SELLER = "resolved_seller"
    RESOLVED_SPLIT = "resolved_split"
    CLOSED = "closed"


class DisputeReason(StrEnum):
    ITEM_NOT_RECEIVED = "item_not_received"
    ITEM_NOT_AS_DESCRIBED = "item_not_as_described"
    QUALITY_ISSUE = "quality_issue"
    DELIVERY_DELAY = "delivery_delay"
    MILESTONE_NOT_MET = "milestone_not_met"
    OTHER = "other"
