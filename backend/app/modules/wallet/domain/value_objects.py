from __future__ import annotations

from enum import StrEnum


class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    PAYOUT = "payout"
    ESCROW_RELEASE = "escrow_release"
    COMMISSION = "commission"
    AFFILIATE_REWARD = "affiliate_reward"
    ADJUSTMENT = "adjustment"


class TransactionDirection(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


class WalletStatus(StrEnum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"
    SUSPENDED = "suspended"
