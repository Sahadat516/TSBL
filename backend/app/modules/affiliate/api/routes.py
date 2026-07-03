from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_optional_user, get_current_user
from app.modules.affiliate.application.affiliate_service import AffiliateService
from app.modules.affiliate.schemas.affiliate_schema import (
    AffiliateProfileResponse,
    CommissionListResponse,
    ReferralListResponse,
    TrackReferralClickRequest,
)
from app.modules.auth.domain.entities import User

router = APIRouter(prefix="/affiliate", tags=["Affiliate"])


def get_affiliate_service(db: AsyncSession = Depends(get_db)) -> AffiliateService:
    return AffiliateService(db)


@router.get("/profile", response_model=AffiliateProfileResponse)
async def get_affiliate_profile(
    current_user: User = Depends(get_current_user),
    service: AffiliateService = Depends(get_affiliate_service),
) -> AffiliateProfileResponse:
    return await service.get_profile(current_user.id)


@router.post("/track")
async def track_referral_click(
    request: TrackReferralClickRequest,
    current_user: User | None = Depends(get_optional_user),
    service: AffiliateService = Depends(get_affiliate_service),
) -> dict:
    visitor_id = current_user.id if current_user else None
    return await service.track_click(request, visitor_id)


@router.get("/referrals", response_model=ReferralListResponse)
async def get_referrals(
    current_user: User = Depends(get_current_user),
    service: AffiliateService = Depends(get_affiliate_service),
) -> ReferralListResponse:
    return await service.get_referrals(current_user.id)


@router.get("/commissions", response_model=CommissionListResponse)
async def get_commissions(
    current_user: User = Depends(get_current_user),
    service: AffiliateService = Depends(get_affiliate_service),
) -> CommissionListResponse:
    return await service.get_commissions(current_user.id)
