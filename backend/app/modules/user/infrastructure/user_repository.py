from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.base_repository import BaseRepository
from app.common.enums import UserStatus
from app.modules.auth.domain.entities import User
from app.modules.user.domain.entities import (
    Address,
    FavoriteSeller,
    SellerProfile,
    UserDevice,
    UserPreference,
    UserProfile,
    UserStat,
    WishlistItem,
)


class UserProfileRepository(BaseRepository[UserProfile]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> UserProfile:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            profile = UserProfile(id=uuid.uuid4(), user_id=user_id)
            self.db.add(profile)
            await self.db.flush()
        return profile


class AddressRepository(BaseRepository[Address]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Address)

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Address]:
        result = await self.db.execute(
            select(Address).where(
                Address.user_id == user_id,
                Address.deleted_at.is_(None),
            ).order_by(Address.is_default.desc(), Address.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_default(self, user_id: uuid.UUID) -> Address | None:
        result = await self.db.execute(
            select(Address).where(
                Address.user_id == user_id,
                Address.is_default.is_(True),
                Address.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def unset_defaults(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            Address.__table__.update().where(
                Address.user_id == user_id,
                Address.is_default.is_(True),
            ).values(is_default=False)
        )
        await self.db.flush()


class SellerProfileRepository(BaseRepository[SellerProfile]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, SellerProfile)

    async def get_by_user_id(self, user_id: uuid.UUID) -> SellerProfile | None:
        result = await self.db.execute(
            select(SellerProfile).where(
                SellerProfile.user_id == user_id,
                SellerProfile.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def find_by_store_slug(self, slug: str) -> SellerProfile | None:
        result = await self.db.execute(
            select(SellerProfile).where(
                SellerProfile.store_slug == slug,
                SellerProfile.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def search_sellers(
        self,
        query: str | None = None,
        sort_by: str = "rating",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SellerProfile], int]:
        q = select(SellerProfile).where(SellerProfile.deleted_at.is_(None))

        if query:
            pattern = f"%{query}%"
            q = q.where(
                or_(
                    SellerProfile.store_name.ilike(pattern),
                    SellerProfile.store_slug.ilike(pattern),
                    SellerProfile.store_description.ilike(pattern),
                )
            )

        count_result = await self.db.execute(select(func.count()).select_from(q.subquery()))
        total = count_result.scalar() or 0
        if total == 0:
            return [], 0

        sort_column = getattr(SellerProfile, sort_by, SellerProfile.rating)
        order_fn = sort_column.desc() if sort_order == "desc" else sort_column.asc()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            q.order_by(order_fn).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def increment_sales(self, seller_id: uuid.UUID, amount: int = 1) -> None:
        profile = await self.get_by_user_id(seller_id)
        if profile:
            profile.total_sales += amount
            await self.db.flush()

    async def increment_products(self, seller_id: uuid.UUID, amount: int = 1) -> None:
        profile = await self.get_by_user_id(seller_id)
        if profile:
            profile.total_products += amount
            await self.db.flush()


class UserPreferenceRepository(BaseRepository[UserPreference]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserPreference)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserPreference | None:
        result = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> UserPreference:
        prefs = await self.get_by_user_id(user_id)
        if not prefs:
            prefs = UserPreference(id=uuid.uuid4(), user_id=user_id)
            self.db.add(prefs)
            await self.db.flush()
        return prefs


class UserDeviceRepository(BaseRepository[UserDevice]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserDevice)

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[UserDevice]:
        result = await self.db.execute(
            select(UserDevice).where(
                UserDevice.user_id == user_id,
                UserDevice.deleted_at.is_(None),
            ).order_by(UserDevice.last_used_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def get_by_device_id(self, user_id: uuid.UUID, device_id: str) -> UserDevice | None:
        result = await self.db.execute(
            select(UserDevice).where(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id,
                UserDevice.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def set_trusted(self, device_id: uuid.UUID, trusted: bool = True) -> None:
        device = await self.get(device_id)
        if device:
            device.is_trusted = trusted
            await self.db.flush()

    async def unset_current(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            UserDevice.__table__.update().where(
                UserDevice.user_id == user_id,
                UserDevice.is_current.is_(True),
            ).values(is_current=False)
        )
        await self.db.flush()


class UserStatRepository(BaseRepository[UserStat]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserStat)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserStat | None:
        result = await self.db.execute(
            select(UserStat).where(UserStat.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> UserStat:
        stats = await self.get_by_user_id(user_id)
        if not stats:
            stats = UserStat(id=uuid.uuid4(), user_id=user_id)
            self.db.add(stats)
            await self.db.flush()
        return stats

    async def add_order(self, user_id: uuid.UUID, amount: Decimal = 0) -> None:
        stats = await self.get_or_create(user_id)
        stats.total_orders += 1
        stats.total_purchases += 1
        stats.total_spent += amount
        stats.last_purchase_at = datetime.now(timezone.utc)
        await self.db.flush()


class WishlistRepository(BaseRepository[WishlistItem]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, WishlistItem)

    async def get_by_user(self, user_id: uuid.UUID, page: int = 1, page_size: int = 20) -> tuple[list[WishlistItem], int]:
        q = select(WishlistItem).where(WishlistItem.user_id == user_id)
        count_result = await self.db.execute(select(func.count()).select_from(q.subquery()))
        total = count_result.scalar() or 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            q.order_by(WishlistItem.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def find(self, user_id: uuid.UUID, product_id: uuid.UUID) -> WishlistItem | None:
        result = await self.db.execute(
            select(WishlistItem).where(
                WishlistItem.user_id == user_id,
                WishlistItem.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()


class FavoriteSellerRepository(BaseRepository[FavoriteSeller]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, FavoriteSeller)

    async def get_by_user(self, user_id: uuid.UUID) -> list[FavoriteSeller]:
        result = await self.db.execute(
            select(FavoriteSeller).where(FavoriteSeller.user_id == user_id)
            .order_by(FavoriteSeller.created_at.desc())
        )
        return list(result.scalars().all())

    async def find(self, user_id: uuid.UUID, seller_id: uuid.UUID) -> FavoriteSeller | None:
        result = await self.db.execute(
            select(FavoriteSeller).where(
                FavoriteSeller.user_id == user_id,
                FavoriteSeller.seller_id == seller_id,
            )
        )
        return result.scalar_one_or_none()


class UserSearchRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search_users(
        self,
        query: str,
        role: str | None = None,
        status: UserStatus | None = None,
        is_verified: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        q = select(User).where(
            User.deleted_at.is_(None),
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
            ),
        )

        if role:
            q = q.where(User.role == role)
        if status:
            q = q.where(User.status == status)
        if is_verified is not None:
            q = q.where(User.is_verified == is_verified)

        count_result = await self.db.execute(select(func.count()).select_from(q.subquery()))
        total = count_result.scalar() or 0
        if total == 0:
            return [], 0

        sort_column = getattr(User, sort_by, User.created_at)
        order_fn = sort_column.desc() if sort_order == "desc" else sort_column.asc()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            q.order_by(order_fn).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def search_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.username == username,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def search_sellers(
        self,
        query: str,
        sort_by: str = "rating",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SellerProfile], int]:
        return await SellerProfileRepository(self.db).search_sellers(query, sort_by, sort_order, page, page_size)
