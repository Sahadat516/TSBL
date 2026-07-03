from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.wallet.domain.value_objects import TransactionDirection, TransactionType, WalletStatus
from app.modules.wallet.schemas.wallet_schema import (
    DepositRequest,
    TransactionResponse,
    WalletAdjustmentRequest,
    WalletResponse,
    WithdrawalRequest,
)


class TestDepositRequest:
    def test_valid(self):
        req = DepositRequest(
            amount=Decimal("100.00"),
            gateway="stripe",
            gateway_transaction_id="txn_123",
        )
        assert req.amount == Decimal("100.00")
        assert req.gateway == "stripe"

    def test_zero_amount_raises(self):
        with pytest.raises(ValidationError):
            DepositRequest(amount=Decimal("0"), gateway="stripe", gateway_transaction_id="txn_1")

    def test_negative_amount_raises(self):
        with pytest.raises(ValidationError):
            DepositRequest(amount=Decimal("-50"), gateway="stripe", gateway_transaction_id="txn_1")


class TestWithdrawalRequest:
    def test_valid(self):
        req = WithdrawalRequest(amount=Decimal("50.00"))
        assert req.amount == Decimal("50.00")

    def test_zero_amount_raises(self):
        with pytest.raises(ValidationError):
            WithdrawalRequest(amount=Decimal("0"))


class TestWalletAdjustmentRequest:
    def test_valid_credit(self):
        req = WalletAdjustmentRequest(
            amount=Decimal("100"),
            direction=TransactionDirection.CREDIT,
            description="Bonus",
            reason="Promotion",
        )
        assert req.direction == TransactionDirection.CREDIT

    def test_valid_debit(self):
        req = WalletAdjustmentRequest(
            amount=Decimal("50"),
            direction=TransactionDirection.DEBIT,
            description="Fee",
            reason="Service fee",
        )
        assert req.direction == TransactionDirection.DEBIT

    def test_empty_description_raises(self):
        with pytest.raises(ValidationError):
            WalletAdjustmentRequest(
                amount=Decimal("10"),
                direction=TransactionDirection.CREDIT,
                description="",
                reason="Test",
            )


class TestWalletResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = WalletResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            balance=Decimal("1000.00"),
            currency="USD",
            status=WalletStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        assert resp.balance == Decimal("1000.00")
        assert resp.status == WalletStatus.ACTIVE

    def test_defaults(self):
        now = datetime.now(timezone.utc)
        resp = WalletResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            balance=Decimal("0"),
            currency="USD",
            status=WalletStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        assert resp.frozen_amount == Decimal("0.00")

    def test_from_attributes(self):
        assert WalletResponse.model_config.get("from_attributes") is True


class TestTransactionResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = TransactionResponse(
            id=uuid.uuid4(),
            wallet_id=uuid.uuid4(),
            transaction_type=TransactionType.DEPOSIT,
            direction=TransactionDirection.CREDIT,
            amount=Decimal("100.00"),
            balance_before=Decimal("0.00"),
            balance_after=Decimal("100.00"),
            currency="USD",
            created_at=now,
        )
        assert resp.transaction_type == TransactionType.DEPOSIT
        assert resp.direction == TransactionDirection.CREDIT

    def test_from_attributes(self):
        assert TransactionResponse.model_config.get("from_attributes") is True
