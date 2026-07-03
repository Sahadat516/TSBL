from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.payments.domain.value_objects import (
    PaymentGateway,
    PaymentMethodType,
    PayoutStatus,
    RefundReason,
    TransactionStatus,
)


class CreatePaymentRequest(BaseModel):
    order_id: UUID
    gateway: PaymentGateway
    metadata: dict | None = None


class ProcessPaymentRequest(BaseModel):
    payment_id: UUID
    gateway_payment_id: str = Field(min_length=1, max_length=255)
    gateway_transaction_id: str = Field(min_length=1, max_length=255)
    gateway_response: dict | None = None


class RefundRequest(BaseModel):
    payment_id: UUID
    amount: Decimal = Field(gt=0)
    reason: RefundReason
    reason_detail: str | None = Field(default=None, max_length=1000)


class PayoutRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(min_length=1, max_length=50)
    payment_details: dict | None = None
    note: str | None = Field(default=None, max_length=500)


class SavePaymentMethodRequest(BaseModel):
    gateway: PaymentGateway
    method_type: PaymentMethodType
    last_four: str | None = Field(default=None, min_length=4, max_length=4)
    expiry_month: int | None = Field(default=None, ge=1, le=12)
    expiry_year: int | None = Field(default=None, ge=2024)
    cardholder_name: str | None = Field(default=None, max_length=100)
    billing_address: dict | None = None
    gateway_method_id: str | None = Field(default=None, max_length=255)
    is_default: bool = False
    metadata: dict | None = None


class PaymentMethodResponse(BaseModel):
    id: UUID
    user_id: UUID
    gateway: PaymentGateway
    method_type: PaymentMethodType
    last_four: str | None = None
    expiry_month: int | None = None
    expiry_year: int | None = None
    cardholder_name: str | None = None
    billing_address: dict | None = None
    is_default: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionLogResponse(BaseModel):
    id: UUID
    gateway: PaymentGateway
    event_type: str
    request_data: dict | None = None
    response_data: dict | None = None
    status_code: int | None = None
    is_success: bool
    error_message: str | None = None
    duration_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RefundResponse(BaseModel):
    id: UUID
    payment_id: UUID
    order_id: UUID
    amount: Decimal
    currency: str
    reason: RefundReason
    reason_detail: str | None = None
    status: TransactionStatus
    gateway_refund_id: str | None = None
    processed_by: UUID | None = None
    processed_at: datetime | None = None
    failure_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    buyer_id: UUID
    seller_id: UUID
    amount: Decimal
    currency: str
    gateway: PaymentGateway
    gateway_payment_id: str | None = None
    gateway_transaction_id: str | None = None
    status: TransactionStatus
    gateway_fee: Decimal = Decimal("0.00")
    net_amount: Decimal
    paid_at: datetime | None = None
    failure_reason: str | None = None
    refunds: list[RefundResponse] = []
    transaction_logs: list[TransactionLogResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PayoutResponse(BaseModel):
    id: UUID
    seller_id: UUID
    amount: Decimal
    currency: str
    status: PayoutStatus
    payment_method: str
    payment_details: dict | None = None
    gateway_payout_id: str | None = None
    fee_amount: Decimal = Decimal("0.00")
    net_amount: Decimal
    note: str | None = None
    completed_at: datetime | None = None
    failure_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PayoutListResponse(BaseModel):
    items: list[PayoutResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
