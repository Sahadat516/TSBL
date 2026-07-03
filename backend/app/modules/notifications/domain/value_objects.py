from __future__ import annotations

from enum import StrEnum


class NotificationType(StrEnum):
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_REFUNDED = "payment_refunded"
    PAYOUT_PROCESSED = "payout_processed"
    NEW_MESSAGE = "new_message"
    NEW_REVIEW = "new_review"
    REVIEW_REPLY = "review_reply"
    DISPUTE_RAISED = "dispute_raised"
    DISPUTE_RESOLVED = "dispute_resolved"
    PRODUCT_APPROVED = "product_approved"
    PRODUCT_REJECTED = "product_rejected"
    WELCOME = "welcome"
    ACCOUNT_VERIFIED = "account_verified"
    SECURITY_ALERT = "security_alert"
    AFFILIATE_COMMISSION = "affiliate_commission"
    PROMOTIONAL = "promotional"
    SYSTEM = "system"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
