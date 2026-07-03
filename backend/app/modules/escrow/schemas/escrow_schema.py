from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.escrow.domain.value_objects import DisputeReason, DisputeStatus, EscrowStatus, MilestoneStatus


class MilestoneRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    amount: Decimal = Field(gt=0)
    sort_order: int = 0
    due_date: datetime | None = None


class CreateEscrowRequest(BaseModel):
    order_id: UUID
    has_milestones: bool = False
    milestones: list[MilestoneRequest] = Field(default_factory=list, max_length=20)
    metadata: dict | None = None


class MilestoneResponse(BaseModel):
    id: UUID
    escrow_id: UUID
    title: str
    description: str | None = None
    amount: Decimal
    status: MilestoneStatus
    sort_order: int
    due_date: datetime | None = None
    completed_at: datetime | None = None
    approved_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeResponse(BaseModel):
    id: UUID
    escrow_id: UUID
    raised_by: UUID
    reason: DisputeReason
    description: str | None = None
    status: DisputeStatus
    resolution_note: str | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    evidence: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EscrowResponse(BaseModel):
    id: UUID
    order_id: UUID
    buyer_id: UUID
    seller_id: UUID
    total_amount: Decimal
    released_amount: Decimal = Decimal("0.00")
    refunded_amount: Decimal = Decimal("0.00")
    fee_amount: Decimal = Decimal("0.00")
    currency: str
    status: EscrowStatus
    has_milestones: bool
    funded_at: datetime | None = None
    released_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    milestones: list[MilestoneResponse] = []
    dispute: DisputeResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EscrowListResponse(BaseModel):
    items: list[EscrowResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReleaseFundsRequest(BaseModel):
    milestone_id: UUID | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    note: str | None = Field(default=None, max_length=500)


class RaiseDisputeRequest(BaseModel):
    reason: DisputeReason
    description: str | None = Field(default=None, max_length=2000)
    evidence: dict | None = None


class ResolveDisputeRequest(BaseModel):
    resolution: DisputeStatus = Field(...)
    note: str = Field(min_length=1, max_length=2000)
    refund_percentage: Decimal | None = Field(default=None, ge=0, le=100)
