from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.payments.domain.value_objects import (
    PaymentGateway,
    PaymentMethodType,
    PayoutStatus,
    RefundReason,
    TransactionStatus,
)
from app.modules.payments.schemas.payment_schema import (
    CreatePaymentRequest,
    PaymentMethodResponse,
    PaymentResponse,
    PayoutRequest,
    PayoutResponse,
    ProcessPaymentRequest,
    RefundRequest,
    RefundResponse,
    SavePaymentMethodRequest,
)


class TestCreatePaymentRequest:
    def test_valid(self):
        oid = uuid.uuid4()
        req = CreatePaymentRequest(order_id=oid, gateway=PaymentGateway.STRIPE)
        assert req.order_id == oid
        assert req.gateway == PaymentGateway.STRIPE

    def test_invalid_gateway(self):
        oid = uuid.uuid4()
        with pytest.raises(ValidationError):
            CreatePaymentRequest(order_id=oid, gateway="invalid_gateway")


class TestProcessPaymentRequest:
    def test_valid(self):
        pid = uuid.uuid4()
        req = ProcessPaymentRequest(
            payment_id=pid,
            gateway_payment_id="pi_123",
            gateway_transaction_id="txn_456",
        )
        assert req.payment_id == pid
        assert req.gateway_payment_id == "pi_123"

    def test_empty_ids_raises(self):
        with pytest.raises(ValidationError):
            ProcessPaymentRequest(payment_id=uuid.uuid4(), gateway_payment_id="", gateway_transaction_id="")


class TestRefundRequest:
    def test_valid(self):
        pid = uuid.uuid4()
        req = RefundRequest(
            payment_id=pid,
            amount=Decimal("50.00"),
            reason=RefundReason.CUSTOMER_REQUEST,
        )
        assert req.amount == Decimal("50.00")

    def test_zero_amount_raises(self):
        with pytest.raises(ValidationError):
            RefundRequest(
                payment_id=uuid.uuid4(),
                amount=Decimal("0"),
                reason=RefundReason.OTHER,
            )

    def test_negative_amount_raises(self):
        with pytest.raises(ValidationError):
            RefundRequest(
                payment_id=uuid.uuid4(),
                amount=Decimal("-10"),
                reason=RefundReason.OTHER,
            )


class TestPayoutRequest:
    def test_valid(self):
        req = PayoutRequest(
            amount=Decimal("100.00"),
            payment_method="bank_transfer",
        )
        assert req.amount == Decimal("100.00")
        assert req.payment_method == "bank_transfer"

    def test_empty_method_raises(self):
        with pytest.raises(ValidationError):
            PayoutRequest(amount=Decimal("100"), payment_method="")


class TestSavePaymentMethodRequest:
    def test_valid(self):
        req = SavePaymentMethodRequest(
            gateway=PaymentGateway.STRIPE,
            method_type=PaymentMethodType.CREDIT_CARD,
            last_four="4242",
            expiry_month=12,
            expiry_year=2028,
        )
        assert req.last_four == "4242"
        assert req.is_default is False

    def test_invalid_expiry_month(self):
        with pytest.raises(ValidationError):
            SavePaymentMethodRequest(
                gateway=PaymentGateway.STRIPE,
                method_type=PaymentMethodType.CREDIT_CARD,
                expiry_month=13,
                expiry_year=2028,
            )


class TestPaymentMethodResponse:
    def test_valid(self):
        uid = uuid.uuid4()
        now = datetime.now(timezone.utc)
        resp = PaymentMethodResponse(
            id=uid,
            user_id=uid,
            gateway=PaymentGateway.STRIPE,
            method_type=PaymentMethodType.CREDIT_CARD,
            is_default=True,
            is_verified=False,
            created_at=now,
        )
        assert resp.gateway == PaymentGateway.STRIPE
        assert resp.is_default is True

    def test_from_attributes(self):
        assert PaymentMethodResponse.model_config.get("from_attributes") is True


class TestRefundResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = RefundResponse(
            id=uuid.uuid4(),
            payment_id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            amount=Decimal("25.00"),
            currency="USD",
            reason=RefundReason.ORDER_CANCELLED,
            status=TransactionStatus.SUCCESS,
            processed_at=now,
            created_at=now,
        )
        assert resp.amount == Decimal("25.00")
        assert resp.reason == RefundReason.ORDER_CANCELLED

    def test_from_attributes(self):
        assert RefundResponse.model_config.get("from_attributes") is True


class TestPaymentResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = PaymentResponse(
            id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("99.99"),
            currency="USD",
            gateway=PaymentGateway.STRIPE,
            status=TransactionStatus.PENDING,
            net_amount=Decimal("97.00"),
            created_at=now,
            updated_at=now,
        )
        assert resp.amount == Decimal("99.99")
        assert resp.status == TransactionStatus.PENDING

    def test_default_gateway_fee(self):
        now = datetime.now(timezone.utc)
        resp = PaymentResponse(
            id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("99.99"),
            currency="USD",
            gateway=PaymentGateway.STRIPE,
            status=TransactionStatus.PENDING,
            net_amount=Decimal("97.00"),
            created_at=now,
            updated_at=now,
        )
        assert resp.gateway_fee == Decimal("0.00")

    def test_from_attributes(self):
        assert PaymentResponse.model_config.get("from_attributes") is True


class TestPayoutResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = PayoutResponse(
            id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("500.00"),
            currency="USD",
            status=PayoutStatus.PENDING,
            payment_method="bank_transfer",
            net_amount=Decimal("500.00"),
            created_at=now,
        )
        assert resp.status == PayoutStatus.PENDING
        assert resp.amount == Decimal("500.00")

    def test_from_attributes(self):
        assert PayoutResponse.model_config.get("from_attributes") is True
