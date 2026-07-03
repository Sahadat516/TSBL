from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.affiliate.domain.value_objects import AffiliateLevel, CommissionStatus, ReferralStatus


class AffiliateProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    referral_code: str
    referred_by: UUID | None = None
    level: AffiliateLevel
    commission_rate: float
    total_earned: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    total_referrals: int = 0
    total_conversions: int = 0
    conversion_rate: float = 0.0
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferralResponse(BaseModel):
    id: UUID
    affiliate_id: UUID
    referred_user_id: UUID | None = None
    status: ReferralStatus
    referral_code_used: str
    ip_address: str | None = None
    source: str | None = None
    converted_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommissionResponse(BaseModel):
    id: UUID
    affiliate_id: UUID
    referral_id: UUID | None = None
    order_id: UUID | None = None
    amount: Decimal
    commission_type: str
    rate: float
    status: CommissionStatus
    paid_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommissionListResponse(BaseModel):
    items: list[CommissionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReferralListResponse(BaseModel):
    items: list[ReferralResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TrackReferralClickRequest(BaseModel):
    referral_code: str = Field(min_length=1, max_length=20)
    ip_address: str | None = None
    user_agent: str | None = None
    source: str | None = Field(default=None, max_length=50)
    metadata: dict | None = None
