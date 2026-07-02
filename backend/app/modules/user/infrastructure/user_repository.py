from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.base_repository import BaseRepository
from app.modules.user.domain.entities import BuyerProfile, SellerProfile, UserPreference, UserProfile, UserSettings


class UserProfileRepository(BaseRepository[UserProfile]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id, UserProfile.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID, created_by: uuid.UUID | None = None) -> UserProfile:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            profile = UserProfile(id=uuid.uuid4(), user_id=user_id, created_by=created_by or user_id)
            self.db.add(profile)
            await self.db.flush()
        return profile


class BuyerProfileRepository(BaseRepository[BuyerProfile]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, BuyerProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> BuyerProfile | None:
        result = await self.db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == user_id, BuyerProfile.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID, created_by: uuid.UUID | None = None) -> BuyerProfile:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            profile = BuyerProfile(id=uuid.uuid4(), user_id=user_id, created_by=created_by or user_id)
            self.db.add(profile)
            await self.db.flush()
        return profile


class SellerProfileRepository(BaseRepository[SellerProfile]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, SellerProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> SellerProfile | None:
        result = await self.db.execute(
            select(SellerProfile).where(SellerProfile.user_id == user_id, SellerProfile.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_by_store_slug(self, slug: str) -> SellerProfile | None:
        result = await self.db.execute(
            select(SellerProfile).where(SellerProfile.store_slug == slug, SellerProfile.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()


class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserSettings)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None:
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id, UserSettings.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID, created_by: uuid.UUID | None = None) -> UserSettings:
        settings = await self.get_by_user_id(user_id)
        if not settings:
            settings = UserSettings(id=uuid.uuid4(), user_id=user_id, created_by=created_by or user_id)
            self.db.add(settings)
            await self.db.flush()
        return settings


class UserPreferenceRepository(BaseRepository[UserPreference]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserPreference)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserPreference | None:
        result = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user_id, UserPreference.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID, created_by: uuid.UUID | None = None) -> UserPreference:
        prefs = await self.get_by_user_id(user_id)
        if not prefs:
            prefs = UserPreference(id=uuid.uuid4(), user_id=user_id, created_by=created_by or user_id)
            self.db.add(prefs)
            await self.db.flush()
        return prefs
