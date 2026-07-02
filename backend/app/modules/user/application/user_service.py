from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import UserRole, UserStatus
from app.core.logging import AuditLogger
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
from app.modules.user.infrastructure.user_repository import (
    AddressRepository,
    FavoriteSellerRepository,
    SellerProfileRepository,
    UserDeviceRepository,
    UserPreferenceRepository,
    UserProfileRepository,
    UserSearchRepository,
    UserStatRepository,
    WishlistRepository,
)
from app.modules.user.schemas.user_schema import (
    AddressCreateRequest,
    AddressListResponse,
    AddressResponse,
    AddressUpdateRequest,
    AvatarUploadResponse,
    DashboardProfileResponse,
    DeviceListResponse,
    DeviceResponse,
    FavoriteSellerResponse,
    NotificationSettingResponse,
    PrivacySettingsResponse,
    ProfileResponse,
    PublicSellerProfileResponse,
    PublicUserProfileResponse,
    SellerProfileCreateRequest,
    SellerProfileResponse,
    SellerProfileUpdateRequest,
    SellerSearchResponse,
    UpdateAccountInfoRequest,
    UpdateProfileRequest,
    UserPreferenceResponse,
    UserPreferenceUpdateRequest,
    UserSearchResponse,
    WishlistAddRequest,
    WishlistItemResponse,
)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = UserProfileRepository(db)
        self.address_repo = AddressRepository(db)
        self.seller_repo = SellerProfileRepository(db)
        self.pref_repo = UserPreferenceRepository(db)
        self.device_repo = UserDeviceRepository(db)
        self.stat_repo = UserStatRepository(db)
        self.wishlist_repo = WishlistRepository(db)
        self.fav_seller_repo = FavoriteSellerRepository(db)
        self.search_repo = UserSearchRepository(db)

    async def get_dashboard(self, user_id: uuid.UUID) -> DashboardProfileResponse:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        profile = await self.profile_repo.get_by_user_id(user_id)
        seller = await self.seller_repo.get_by_user_id(user_id)
        prefs = await self.pref_repo.get_by_user_id(user_id)
        stats = await self.stat_repo.get_by_user_id(user_id)
        return DashboardProfileResponse(
            id=user.id, email=user.email, username=user.username,
            phone=user.phone, role=user.role.value if hasattr(user.role, "value") else user.role,
            status=user.status.value if hasattr(user.status, "value") else user.status,
            is_verified=user.is_verified,
            profile=ProfileResponse.model_validate(profile) if profile else None,
            seller_profile=SellerProfileResponse.model_validate(seller) if seller else None,
            preferences=UserPreferenceResponse.model_validate(prefs) if prefs else None,
            stats=stats.metadata if stats else None,
            created_at=user.created_at,
        )

    async def update_profile(self, user_id: uuid.UUID, request: UpdateProfileRequest) -> ProfileResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        await self.db.flush()

        AuditLogger.log(
            action="PROFILE_UPDATED", actor_id=str(user_id),
            resource="user_profile", resource_id=str(profile.id),
            details={"updated_fields": list(update_data.keys())},
        )
        return ProfileResponse.model_validate(profile)

    async def get_profile(self, user_id: uuid.UUID) -> ProfileResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        return ProfileResponse.model_validate(profile)

    async def update_avatar(self, user_id: uuid.UUID, avatar_url: str, thumbnail_url: str | None = None) -> AvatarUploadResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        profile.avatar_url = avatar_url
        profile.avatar_thumbnail_url = thumbnail_url
        await self.db.flush()

        AuditLogger.log(
            action="AVATAR_UPDATED", actor_id=str(user_id),
            resource="user_profile", resource_id=str(profile.id),
        )
        return AvatarUploadResponse(avatar_url=avatar_url, avatar_thumbnail_url=thumbnail_url)

    async def delete_avatar(self, user_id: uuid.UUID) -> None:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile:
            profile.avatar_url = None
            profile.avatar_thumbnail_url = None
            await self.db.flush()

    async def update_cover_image(self, user_id: uuid.UUID, cover_url: str) -> ProfileResponse:
        profile = await self.profile_repo.get_or_create(user_id)
        profile.cover_image_url = cover_url
        await self.db.flush()
        return ProfileResponse.model_validate(profile)

    async def update_account_info(self, user_id: uuid.UUID, request: UpdateAccountInfoRequest) -> dict:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        update_data = request.model_dump(exclude_unset=True)
        if "username" in update_data:
            existing = await self.db.execute(
                select(User).where(User.username == update_data["username"], User.id != user_id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        await self.db.flush()

        AuditLogger.log(
            action="ACCOUNT_INFO_UPDATED", actor_id=str(user_id),
            resource="user", resource_id=str(user_id),
            details={"updated": list(update_data.keys())},
        )
        return {"updated": list(update_data.keys())}

    async def get_privacy_settings(self, user_id: uuid.UUID) -> PrivacySettingsResponse:
        prefs = await self.pref_repo.get_or_create(user_id)
        return PrivacySettingsResponse(
            profile_visibility=prefs.profile_visibility,
            activity_visibility=prefs.activity_visibility,
            show_online_status=prefs.show_online_status,
            allow_messages_from=prefs.allow_messages_from,
        )

    # --- Address Book ---

    async def list_addresses(self, user_id: uuid.UUID) -> AddressListResponse:
        addresses = await self.address_repo.get_by_user_id(user_id)
        items = [AddressResponse.model_validate(a) for a in addresses]
        return AddressListResponse(items=items, total=len(items))

    async def create_address(self, user_id: uuid.UUID, request: AddressCreateRequest) -> AddressResponse:
        if request.is_default:
            await self.address_repo.unset_defaults(user_id)

        address = Address(
            id=uuid.uuid4(), user_id=user_id,
            label=request.label, recipient_name=request.recipient_name,
            phone=request.phone, street_address=request.street_address,
            street_address_line2=request.street_address_line2,
            city=request.city, state=request.state,
            postal_code=request.postal_code, country=request.country,
            latitude=request.latitude, longitude=request.longitude,
            is_default=request.is_default, is_billing=request.is_billing,
            is_shipping=request.is_shipping, address_type=request.address_type,
        )
        await self.address_repo.create(address)
        return AddressResponse.model_validate(address)

    async def update_address(self, user_id: uuid.UUID, address_id: uuid.UUID, request: AddressUpdateRequest) -> AddressResponse:
        address = await self.address_repo.get(address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

        if request.is_default:
            await self.address_repo.unset_defaults(user_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(address, field):
                setattr(address, field, value)
        await self.db.flush()
        return AddressResponse.model_validate(address)

    async def delete_address(self, user_id: uuid.UUID, address_id: uuid.UUID) -> None:
        address = await self.address_repo.get(address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        await self.address_repo.soft_delete(address_id)

    async def set_default_address(self, user_id: uuid.UUID, address_id: uuid.UUID) -> AddressResponse:
        address = await self.address_repo.get(address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        await self.address_repo.unset_defaults(user_id)
        address.is_default = True
        await self.db.flush()
        return AddressResponse.model_validate(address)

    # --- Seller Profile ---

    async def create_seller_profile(self, user_id: uuid.UUID, request: SellerProfileCreateRequest) -> SellerProfileResponse:
        existing = await self.seller_repo.get_by_user_id(user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seller profile already exists")

        slug_exists = await self.seller_repo.find_by_store_slug(request.store_slug)
        if slug_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Store slug already taken")

        profile = SellerProfile(
            id=uuid.uuid4(), user_id=user_id,
            store_name=request.store_name, store_slug=request.store_slug,
            store_description=request.store_description,
            business_type=request.business_type,
            business_registration_number=request.business_registration_number,
            business_address=request.business_address, tax_id=request.tax_id,
            social_links=request.social_links, policies=request.policies,
        )
        await self.seller_repo.create(profile)

        user = await self.db.get(User, user_id)
        if user:
            user.role = UserRole.SELLER
            await self.db.flush()

        AuditLogger.log(
            action="SELLER_PROFILE_CREATED", actor_id=str(user_id),
            resource="seller_profile", resource_id=str(profile.id),
            details={"store_name": request.store_name, "store_slug": request.store_slug},
        )
        return SellerProfileResponse.model_validate(profile)

    async def get_seller_profile(self, user_id: uuid.UUID) -> SellerProfileResponse:
        profile = await self.seller_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
        return SellerProfileResponse.model_validate(profile)

    async def update_seller_profile(self, user_id: uuid.UUID, request: SellerProfileUpdateRequest) -> SellerProfileResponse:
        profile = await self.seller_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        await self.db.flush()

        AuditLogger.log(
            action="SELLER_PROFILE_UPDATED", actor_id=str(user_id),
            resource="seller_profile", resource_id=str(profile.id),
            details={"updated": list(update_data.keys())},
        )
        return SellerProfileResponse.model_validate(profile)

    async def update_store_logo(self, user_id: uuid.UUID, logo_url: str) -> SellerProfileResponse:
        profile = await self.seller_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
        profile.store_logo_url = logo_url
        await self.db.flush()
        return SellerProfileResponse.model_validate(profile)

    async def update_store_banner(self, user_id: uuid.UUID, banner_url: str) -> SellerProfileResponse:
        profile = await self.seller_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
        profile.store_banner_url = banner_url
        await self.db.flush()
        return SellerProfileResponse.model_validate(profile)

    async def get_public_seller_profile(self, store_slug: str) -> PublicSellerProfileResponse:
        profile = await self.seller_repo.find_by_store_slug(store_slug)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
        return PublicSellerProfileResponse(
            user_id=profile.user_id, username="",
            store_name=profile.store_name, store_slug=profile.store_slug,
            store_logo_url=profile.store_logo_url, store_banner_url=profile.store_banner_url,
            store_description=profile.store_description, store_status=profile.store_status,
            is_verified=profile.is_verified, rating=profile.rating,
            total_sales=profile.total_sales, total_products=profile.total_products,
            total_reviews=profile.total_reviews,
            response_time_hours=profile.response_time_hours,
            policies=profile.policies, member_since=profile.created_at,
        )

    async def get_public_user_profile(self, username: str) -> PublicUserProfileResponse:
        user = await self.search_repo.search_by_username(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        profile = await self.profile_repo.get_by_user_id(user.id)
        seller = await self.seller_repo.get_by_user_id(user.id)
        seller_resp = None
        if seller:
            seller_resp = await self.get_public_seller_profile(seller.store_slug)
        return PublicUserProfileResponse(
            user_id=user.id, username=user.username,
            display_name=profile.display_name if profile else None,
            avatar_url=profile.avatar_url if profile else user.profile_photo_url,
            biography=profile.biography if profile else None,
            country=profile.country if profile else None,
            member_since=user.created_at,
            is_seller=seller is not None,
            seller_profile=seller_resp,
        )

    # --- Preferences ---

    async def get_preferences(self, user_id: uuid.UUID) -> UserPreferenceResponse:
        prefs = await self.pref_repo.get_or_create(user_id)
        return UserPreferenceResponse.model_validate(prefs)

    async def update_preferences(self, user_id: uuid.UUID, request: UserPreferenceUpdateRequest) -> UserPreferenceResponse:
        prefs = await self.pref_repo.get_or_create(user_id)
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(prefs, field):
                setattr(prefs, field, value)
        await self.db.flush()
        return UserPreferenceResponse.model_validate(prefs)

    async def get_notification_settings(self, user_id: uuid.UUID) -> NotificationSettingResponse:
        prefs = await self.pref_repo.get_or_create(user_id)
        return NotificationSettingResponse(
            email=prefs.enable_email_notifications,
            sms=prefs.enable_sms_notifications,
            push=prefs.enable_push_notifications,
            in_app=True,
            marketing=prefs.enable_marketing_emails,
            security_alerts=prefs.enable_security_alerts,
            order_updates=prefs.enable_order_updates,
            wallet_alerts=prefs.enable_wallet_alerts,
            newsletter=prefs.enable_newsletter,
        )

    # --- Devices ---

    async def list_devices(self, user_id: uuid.UUID) -> DeviceListResponse:
        devices = await self.device_repo.get_by_user_id(user_id)
        items = [DeviceResponse.model_validate(d) for d in devices]
        return DeviceListResponse(items=items, total=len(items))

    async def trust_device(self, user_id: uuid.UUID, device_id: uuid.UUID) -> DeviceResponse:
        device = await self.device_repo.get(device_id)
        if not device or device.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        device.is_trusted = True
        await self.db.flush()
        return DeviceResponse.model_validate(device)

    async def untrust_device(self, user_id: uuid.UUID, device_id: uuid.UUID) -> DeviceResponse:
        device = await self.device_repo.get(device_id)
        if not device or device.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        device.is_trusted = False
        await self.db.flush()
        return DeviceResponse.model_validate(device)

    async def remove_device(self, user_id: uuid.UUID, device_id: uuid.UUID) -> None:
        device = await self.device_repo.get(device_id)
        if not device or device.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        await self.device_repo.soft_delete(device_id)

    # --- Wishlist ---

    async def list_wishlist(self, user_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[WishlistItemResponse]:
        items, total = await self.wishlist_repo.get_by_user(user_id, page, page_size)
        return [WishlistItemResponse.model_validate(i) for i in items]

    async def add_to_wishlist(self, user_id: uuid.UUID, request: WishlistAddRequest) -> WishlistItemResponse:
        existing = await self.wishlist_repo.find(user_id, request.product_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in wishlist")
        item = WishlistItem(
            id=uuid.uuid4(), user_id=user_id,
            product_id=request.product_id, notes=request.notes,
        )
        await self.wishlist_repo.create(item)

        stats = await self.stat_repo.get_or_create(user_id)
        stats.total_wishlist_items += 1
        await self.db.flush()

        return WishlistItemResponse.model_validate(item)

    async def remove_from_wishlist(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        item = await self.wishlist_repo.find(user_id, product_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in wishlist")
        await self.wishlist_repo.hard_delete(item.id)

        stats = await self.stat_repo.get_or_create(user_id)
        if stats.total_wishlist_items > 0:
            stats.total_wishlist_items -= 1
        await self.db.flush()

    # --- Favorite Sellers ---

    async def list_favorite_sellers(self, user_id: uuid.UUID) -> list[FavoriteSellerResponse]:
        items = await self.fav_seller_repo.get_by_user(user_id)
        result = []
        for fs in items:
            seller = await self.seller_repo.get_by_user_id(fs.seller_id)
            result.append(FavoriteSellerResponse(
                id=fs.id, seller_id=fs.seller_id,
                store_name=seller.store_name if seller else None,
                store_slug=seller.store_slug if seller else None,
                created_at=fs.created_at,
            ))
        return result

    async def add_favorite_seller(self, user_id: uuid.UUID, seller_id: uuid.UUID) -> FavoriteSellerResponse:
        if user_id == seller_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
        existing = await self.fav_seller_repo.find(user_id, seller_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already following")
        fs = FavoriteSeller(id=uuid.uuid4(), user_id=user_id, seller_id=seller_id)
        await self.fav_seller_repo.create(fs)

        stats = await self.stat_repo.get_or_create(user_id)
        stats.total_favorite_sellers += 1
        await self.db.flush()

        seller = await self.seller_repo.get_by_user_id(seller_id)
        return FavoriteSellerResponse(
            id=fs.id, seller_id=fs.seller_id,
            store_name=seller.store_name if seller else None,
            store_slug=seller.store_slug if seller else None,
            created_at=fs.created_at,
        )

    async def remove_favorite_seller(self, user_id: uuid.UUID, seller_id: uuid.UUID) -> None:
        fs = await self.fav_seller_repo.find(user_id, seller_id)
        if not fs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not following")
        await self.fav_seller_repo.hard_delete(fs.id)

        stats = await self.stat_repo.get_or_create(user_id)
        if stats.total_favorite_sellers > 0:
            stats.total_favorite_sellers -= 1
        await self.db.flush()

    # --- Search ---

    async def search_users(
        self, query: str, role: str | None = None,
        status: str | None = None, is_verified: bool | None = None,
        sort_by: str = "created_at", sort_order: str = "desc",
        page: int = 1, page_size: int = 20,
    ) -> UserSearchResponse:
        status_enum = UserStatus(status) if status else None
        users, total = await self.search_repo.search_users(
            query, role, status_enum, is_verified, sort_by, sort_order, page, page_size,
        )
        items = []
        for user in users:
            profile = await self.profile_repo.get_by_user_id(user.id)
            items.append(PublicUserProfileResponse(
                user_id=user.id, username=user.username,
                display_name=profile.display_name if profile else None,
                avatar_url=profile.avatar_url if profile else user.profile_photo_url,
                biography=profile.biography if profile else None,
                country=profile.country if profile else None,
                member_since=user.created_at, is_seller=False,
            ))
        total_pages = max(1, (total + page_size - 1) // page_size)
        return UserSearchResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)

    async def search_sellers(
        self, query: str, sort_by: str = "rating",
        sort_order: str = "desc", page: int = 1, page_size: int = 20,
    ) -> SellerSearchResponse:
        profiles, total = await self.seller_repo.search_sellers(query, sort_by, sort_order, page, page_size)
        items = []
        for p in profiles:
            items.append(PublicSellerProfileResponse(
                user_id=p.user_id, username="",
                store_name=p.store_name, store_slug=p.store_slug,
                store_logo_url=p.store_logo_url, store_banner_url=p.store_banner_url,
                store_description=p.store_description, store_status=p.store_status,
                is_verified=p.is_verified, rating=p.rating,
                total_sales=p.total_sales, total_products=p.total_products,
                total_reviews=p.total_reviews, response_time_hours=p.response_time_hours,
                policies=p.policies, member_since=p.created_at,
            ))
        total_pages = max(1, (total + page_size - 1) // page_size)
        return SellerSearchResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)
