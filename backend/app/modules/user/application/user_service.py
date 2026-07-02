from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.auth.domain.entities import User
from app.modules.user.infrastructure.user_repository import (
    BuyerProfileRepository,
    SellerProfileRepository,
    UserPreferenceRepository,
    UserProfileRepository,
    UserSettingsRepository,
)
from app.modules.user.schemas.user_schema import (
    ProfileResponse,
    UpdateProfileRequest,
    UserDetailResponse,
    UserPreferenceResponse,
    UserPublicResponse,
    UserSettingsResponse,
)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = UserProfileRepository(db)
        self.seller_repo = SellerProfileRepository(db)
        self.buyer_repo = BuyerProfileRepository(db)
        self.settings_repo = UserSettingsRepository(db)
        self.pref_repo = UserPreferenceRepository(db)

    async def get_user(self, user_id: uuid.UUID) -> UserDetailResponse:
        user = await self._get_user_or_404(user_id)
        profile = await self.profile_repo.get_by_user_id(user_id)
        settings = await self.settings_repo.get_by_user_id(user_id)
        prefs = await self.pref_repo.get_by_user_id(user_id)

        return UserDetailResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            phone=user.phone,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            status=user.status.value if hasattr(user.status, "value") else str(user.status),
            is_verified=user.is_verified,
            profile_photo_url=user.profile_photo_url,
            locale=user.locale,
            timezone=user.timezone,
            profile=ProfileResponse.model_validate(profile) if profile else None,
            settings=UserSettingsResponse.model_validate(settings) if settings else None,
            preferences=UserPreferenceResponse.model_validate(prefs) if prefs else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def update_profile(self, user_id: uuid.UUID, request: UpdateProfileRequest) -> ProfileResponse:
        profile = await self.profile_repo.get_or_create(user_id, created_by=user_id)
        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            return ProfileResponse.model_validate(profile)

        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        profile.updated_by = user_id
        profile.version += 1
        await self.db.flush()

        AuditLogger.log(
            action="PROFILE_UPDATED",
            actor_id=str(user_id),
            resource="user_profile",
            resource_id=str(profile.id),
            details={"updated_fields": list(update_data.keys())},
        )

        return ProfileResponse.model_validate(profile)

    async def get_user_by_id(self, target_id: uuid.UUID) -> UserPublicResponse:
        user = await self._get_user_or_404(target_id)
        profile = await self.profile_repo.get_by_user_id(target_id)
        seller = await self.seller_repo.get_by_user_id(target_id)
        buyer = await self.buyer_repo.get_by_user_id(target_id)

        return UserPublicResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            display_name=profile.display_name if profile else None,
            avatar_url=profile.avatar_url if profile else user.profile_photo_url,
            biography=profile.biography if profile else None,
            country=profile.country if profile else None,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            is_verified=user.is_verified,
            created_at=user.created_at,
            is_seller=seller is not None,
            is_buyer=buyer is not None,
        )

    async def _get_user_or_404(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
