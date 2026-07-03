from __future__ import annotations

from enum import StrEnum


class TicketStatus(StrEnum):
    OPEN = "open"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(StrEnum):
    ORDER_ISSUE = "order_issue"
    PAYMENT_ISSUE = "payment_issue"
    PRODUCT_ISSUE = "product_issue"
    ACCOUNT_ISSUE = "account_issue"
    TECHNICAL_ISSUE = "technical_issue"
    SELLER_SUPPORT = "seller_support"
    BUYER_SUPPORT = "buyer_support"
    DISPUTE = "dispute"
    FEEDBACK = "feedback"
    OTHER = "other"
