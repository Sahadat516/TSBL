from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.affiliate.domain.entities import Referral
from app.modules.affiliate.domain.value_objects import ReferralStatus
from app.modules.affiliate.infrastructure.affiliate_repository import (
    AffiliateProfileRepository,
    CommissionRepository,
    ReferralRepository,
)
from app.modules.affiliate.schemas.affiliate_schema import (
    AffiliateProfileResponse,
    CommissionListResponse,
    CommissionResponse,
    ReferralListResponse,
    ReferralResponse,
    TrackReferralClickRequest,
)


class AffiliateService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = AffiliateProfileRepository(db)
        self.referral_repo = ReferralRepository(db)
        self.commission_repo = CommissionRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> AffiliateProfileResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        return AffiliateProfileResponse.model_validate(profile)

    async def track_click(self, request: TrackReferralClickRequest, visitor_id: uuid.UUID | None = None) -> dict:
        referrer = await self.profile_repo.get_by_referral_code(request.referral_code)
        if not referrer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid referral code")
        if visitor_id and referrer.user_id == visitor_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot use own referral code")

        referral = Referral(
            id=uuid.uuid4(),
            affiliate_id=referrer.id,
            referred_user_id=visitor_id,
            status=ReferralStatus.CLICKED,
            referral_code_used=request.referral_code,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            source=request.source,
            metadata=request.metadata,
        )
        await self.referral_repo.create(referral)

        referrer.total_referrals += 1
        await self.db.flush()

        return {"message": "Referral tracked", "referral_id": str(referral.id)}

    async def get_referrals(self, user_id: uuid.UUID) -> ReferralListResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        referrals = await self.referral_repo.list_by_affiliate(profile.id)
        return ReferralListResponse(
            items=[ReferralResponse.model_validate(r) for r in referrals],
            total=len(referrals),
            page=1,
            page_size=len(referrals) or 1,
            total_pages=1,
        )

    async def get_commissions(self, user_id: uuid.UUID) -> CommissionListResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        commissions = await self.commission_repo.list_by_affiliate(profile.id)
        total_pages = max(1, (len(commissions) + 19) // 20)
        return CommissionListResponse(
            items=[CommissionResponse.model_validate(c) for c in commissions],
            total=len(commissions),
            page=1,
            page_size=20,
            total_pages=total_pages,
        )

    async def convert_referral(self, referral_id: uuid.UUID, user_id: uuid.UUID) -> None:
        referral = await self.referral_repo.get(referral_id)
        if not referral:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")

        referral.referred_user_id = user_id
        referral.status = ReferralStatus.SIGNED_UP
        referral.version += 1

        profile = await self.profile_repo.get(referral.affiliate_id)
        if profile:
            profile.total_conversions += 1
            if profile.total_referrals > 0:
                profile.conversion_rate = (profile.total_conversions / profile.total_referrals) * 100

        await self.db.flush()
