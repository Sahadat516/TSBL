from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.common.enums import DeliveryMethod, DeliveryStatus, OrderStatus, PaymentStatus


class OrderItemRequest(BaseModel):
    product_id: UUID
    variant_id: UUID | None = None
    quantity: int = Field(default=1, ge=1, le=100)


class OrderCreateRequest(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1, max_length=50)
    buyer_note: str | None = Field(default=None, max_length=1000)
    metadata: dict | None = None


class CancelOrderRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class ConfirmDeliveryRequest(BaseModel):
    pass


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    variant_id: UUID | None
    product_name: str
    variant_name: str | None
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_price: Decimal
    delivery_method: DeliveryMethod
    delivery_status: DeliveryStatus
    is_digital: bool

    model_config = {"from_attributes": True}


class StatusHistoryResponse(BaseModel):
    id: UUID
    from_status: str | None
    to_status: str
    changed_by: UUID | None
    reason: str | None
    is_automated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    buyer_id: UUID
    seller_id: UUID
    status: OrderStatus
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    payment_status: PaymentStatus
    is_disputed: bool
    buyer_note: str | None
    seller_note: str | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    completed_at: datetime | None
    items: list[OrderItemResponse] = []
    status_history: list[StatusHistoryResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OrderTimelineResponse(BaseModel):
    current_status: OrderStatus
    timeline: list[StatusHistoryResponse]
