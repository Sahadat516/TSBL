from __future__ import annotations

from enum import StrEnum


class CommissionStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class CommissionType(StrEnum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class ReferralStatus(StrEnum):
    CLICKED = "clicked"
    SIGNED_UP = "signed_up"
    FIRST_PURCHASE = "first_purchase"
    QUALIFIED = "qualified"
    EXPIRED = "expired"


class AffiliateLevel(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
