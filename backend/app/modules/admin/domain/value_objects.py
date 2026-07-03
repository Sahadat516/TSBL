from __future__ import annotations

from enum import StrEnum


class AuditAction(StrEnum):
    USER_CREATED = "user_created"
    USER_SUSPENDED = "user_suspended"
    USER_BANNED = "user_banned"
    USER_DELETED = "user_deleted"
    PRODUCT_APPROVED = "product_approved"
    PRODUCT_REJECTED = "product_rejected"
    PRODUCT_FEATURED = "product_featured"
    ORDER_REFUNDED = "order_refunded"
    DISPUTE_RESOLVED = "dispute_resolved"
    PAYOUT_PROCESSED = "payout_processed"
    SETTINGS_CHANGED = "settings_changed"
    ROLE_MODIFIED = "role_modified"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"


class SystemConfigType(StrEnum):
    GENERAL = "general"
    PAYMENT = "payment"
    COMMISSION = "commission"
    MARKETPLACE = "marketplace"
    SECURITY = "security"
    EMAIL = "email"
    FEATURES = "features"
