from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.base_repository import BaseRepository
from app.modules.affiliate.domain.entities import AffiliateProfile, Commission, Referral


class AffiliateProfileRepository(BaseRepository[AffiliateProfile]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, AffiliateProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> AffiliateProfile | None:
        result = await self.db.execute(
            select(AffiliateProfile).where(
                AffiliateProfile.user_id == user_id, AffiliateProfile.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, code: str) -> AffiliateProfile | None:
        result = await self.db.execute(
            select(AffiliateProfile).where(
                AffiliateProfile.referral_code == code,
                AffiliateProfile.is_active.is_(True),
                AffiliateProfile.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> AffiliateProfile:
        profile = await self.get_by_user_id(user_id)
        if profile:
            return profile

        import random, string
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while await self.get_by_referral_code(code):
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

        profile = AffiliateProfile(
            id=uuid.uuid4(),
            user_id=user_id,
            referral_code=code,
        )
        self.db.add(profile)
        await self.db.flush()
        return profile


class ReferralRepository(BaseRepository[Referral]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Referral)

    async def list_by_affiliate(self, affiliate_id: uuid.UUID) -> list[Referral]:
        result = await self.db.execute(
            select(Referral)
            .where(Referral.affiliate_id == affiliate_id, Referral.deleted_at.is_(None))
            .order_by(Referral.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_affiliate(self, affiliate_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(Referral.id)).where(
                Referral.affiliate_id == affiliate_id, Referral.deleted_at.is_(None)
            )
        )
        return result.scalar() or 0


class CommissionRepository(BaseRepository[Commission]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Commission)

    async def list_by_affiliate(self, affiliate_id: uuid.UUID) -> list[Commission]:
        result = await self.db.execute(
            select(Commission)
            .where(Commission.affiliate_id == affiliate_id, Commission.deleted_at.is_(None))
            .order_by(Commission.created_at.desc())
        )
        return list(result.scalars().all())

    async def total_earned(self, affiliate_id: uuid.UUID) -> Decimal:
        from decimal import Decimal
        result = await self.db.execute(
            select(func.coalesce(func.sum(Commission.amount), 0)).where(
                Commission.affiliate_id == affiliate_id,
                Commission.status.in_(["approved", "paid"]),
                Commission.deleted_at.is_(None),
            )
        )
        return result.scalar() or Decimal("0.00")
