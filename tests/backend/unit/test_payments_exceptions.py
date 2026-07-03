from __future__ import annotations

from app.modules.payments.domain.exceptions import (
    InsufficientBalanceError,
    PaymentAlreadyProcessedError,
    PaymentDomainError,
    PaymentGatewayError,
    PaymentMethodNotFoundError,
    PaymentNotFoundError,
    PayoutAccessDeniedError,
    PayoutNotFoundError,
    RefundAmountExceedsError,
    RefundNotFoundError,
)


class TestPaymentExceptions:
    def test_hierarchy(self):
        assert issubclass(PaymentNotFoundError, PaymentDomainError)
        assert issubclass(PaymentGatewayError, PaymentDomainError)

    def test_status_codes(self):
        assert PaymentNotFoundError.status_code == 404
        assert PaymentAlreadyProcessedError.status_code == 409
        assert InsufficientBalanceError.status_code == 400
        assert PaymentGatewayError.status_code == 502
        assert PayoutAccessDeniedError.status_code == 403

    def test_error_codes(self):
        assert PaymentNotFoundError.code == "payment_not_found"
        assert PaymentMethodNotFoundError.code == "payment_method_not_found"
        assert RefundAmountExceedsError.code == "refund_amount_exceeds"
        assert PaymentGatewayError.code == "payment_gateway_error"

    def test_default_detail(self):
        assert "not found" in PaymentNotFoundError.detail.lower()
        assert "exceeds" in RefundAmountExceedsError.detail.lower()
