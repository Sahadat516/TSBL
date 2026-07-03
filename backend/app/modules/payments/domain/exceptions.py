from __future__ import annotations

from app.exceptions.base import AppException


class PaymentDomainError(AppException):
    code: str = "payment_domain_error"
    detail: str = "Payment domain error"


class PaymentNotFoundError(PaymentDomainError):
    status_code: int = 404
    code: str = "payment_not_found"
    detail: str = "Payment not found"


class PaymentMethodNotFoundError(PaymentDomainError):
    status_code: int = 404
    code: str = "payment_method_not_found"
    detail: str = "Payment method not found"


class PayoutNotFoundError(PaymentDomainError):
    status_code: int = 404
    code: str = "payout_not_found"
    detail: str = "Payout not found"


class RefundNotFoundError(PaymentDomainError):
    status_code: int = 404
    code: str = "refund_not_found"
    detail: str = "Refund not found"


class PaymentAlreadyProcessedError(PaymentDomainError):
    status_code: int = 409
    code: str = "payment_already_processed"
    detail: str = "Payment has already been processed"


class InsufficientBalanceError(PaymentDomainError):
    status_code: int = 400
    code: str = "insufficient_balance"
    detail: str = "Insufficient balance"


class RefundAmountExceedsError(PaymentDomainError):
    status_code: int = 400
    code: str = "refund_amount_exceeds"
    detail: str = "Refund amount exceeds payment amount"


class PaymentGatewayError(PaymentDomainError):
    status_code: int = 502
    code: str = "payment_gateway_error"
    detail: str = "Payment gateway error"


class PayoutAccessDeniedError(PaymentDomainError):
    status_code: int = 403
    code: str = "payout_access_denied"
    detail: str = "Access to this payout is denied"
