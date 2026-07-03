from __future__ import annotations

import pytest

from app.modules.wallet.domain.value_objects import TransactionDirection, TransactionType, WalletStatus


class TestTransactionType:
    def test_values(self):
        assert TransactionType.DEPOSIT == "deposit"
        assert TransactionType.WITHDRAWAL == "withdrawal"
        assert TransactionType.PAYMENT == "payment"
        assert TransactionType.REFUND == "refund"
        assert TransactionType.AFFILIATE_REWARD == "affiliate_reward"


class TestTransactionDirection:
    def test_values(self):
        assert TransactionDirection.CREDIT == "credit"
        assert TransactionDirection.DEBIT == "debit"


class TestWalletStatus:
    def test_values(self):
        assert WalletStatus.ACTIVE == "active"
        assert WalletStatus.FROZEN == "frozen"
        assert WalletStatus.CLOSED == "closed"
