from __future__ import annotations

import pytest

from app.modules.payments.domain.value_objects import (
    Currency,
    PaymentGateway,
    PaymentMethodType,
    PayoutStatus,
    RefundReason,
    TransactionStatus,
)


class TestPaymentGateway:
    def test_values(self):
        assert PaymentGateway.STRIPE == "stripe"
        assert PaymentGateway.PAYPAL == "paypal"
        assert PaymentGateway.BKASH == "bkash"

    def test_members(self):
        assert len(PaymentGateway) == 9


class TestTransactionStatus:
    def test_values(self):
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.SUCCESS == "success"
        assert TransactionStatus.FAILED == "failed"

    def test_refund_statuses(self):
        assert TransactionStatus.REFUNDED == "refunded"
        assert TransactionStatus.PARTIALLY_REFUNDED == "partially_refunded"


class TestPaymentMethodType:
    def test_values(self):
        assert PaymentMethodType.CREDIT_CARD == "credit_card"
        assert PaymentMethodType.DIGITAL_WALLET == "digital_wallet"


class TestPayoutStatus:
    def test_values(self):
        assert PayoutStatus.PENDING == "pending"
        assert PayoutStatus.COMPLETED == "completed"
        assert PayoutStatus.HOLD == "hold"


class TestRefundReason:
    def test_values(self):
        assert RefundReason.ORDER_CANCELLED == "order_cancelled"
        assert RefundReason.FRAUD_SUSPECTED == "fraud_suspected"


class TestCurrency:
    def test_values(self):
        assert Currency.USD == "USD"
        assert Currency.BDT == "BDT"
