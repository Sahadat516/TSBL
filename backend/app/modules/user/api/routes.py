from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.user.application.user_service import UserService
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

router = APIRouter(prefix="/users", tags=["User Management"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


# --- Dashboard ---

@router.get("/me/dashboard", response_model=DashboardProfileResponse)
async def dashboard(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> DashboardProfileResponse:
    return await service.get_dashboard(current_user.id)


# --- Profile ---

@router.get("/me/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> ProfileResponse:
    return await service.get_profile(current_user.id)


@router.patch("/me/profile", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> ProfileResponse:
    return await service.update_profile(current_user.id, request)


@router.post("/me/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    avatar_url: str,
    thumbnail_url: str | None = None,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> AvatarUploadResponse:
    return await service.update_avatar(current_user.id, avatar_url, thumbnail_url)


@router.delete("/me/avatar", status_code=204)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete_avatar(current_user.id)


@router.post("/me/cover-image", response_model=ProfileResponse)
async def upload_cover_image(
    cover_url: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> ProfileResponse:
    return await service.update_cover_image(current_user.id, cover_url)


@router.patch("/me/account", response_model=dict)
async def update_account_info(
    request: UpdateAccountInfoRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> dict:
    return await service.update_account_info(current_user.id, request)


@router.get("/me/privacy", response_model=PrivacySettingsResponse)
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> PrivacySettingsResponse:
    return await service.get_privacy_settings(current_user.id)


# --- Address Book ---

@router.get("/me/addresses", response_model=AddressListResponse)
async def list_addresses(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> AddressListResponse:
    return await service.list_addresses(current_user.id)


@router.post("/me/addresses", response_model=AddressResponse, status_code=201)
async def create_address(
    request: AddressCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> AddressResponse:
    return await service.create_address(current_user.id, request)


@router.put("/me/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    request: AddressUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> AddressResponse:
    return await service.update_address(current_user.id, uuid.UUID(address_id), request)


@router.delete("/me/addresses/{address_id}", status_code=204)
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete_address(current_user.id, uuid.UUID(address_id))


@router.put("/me/addresses/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> AddressResponse:
    return await service.set_default_address(current_user.id, uuid.UUID(address_id))


# --- Seller Profile ---

@router.post("/me/seller-profile", response_model=SellerProfileResponse, status_code=201)
async def create_seller_profile(
    request: SellerProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> SellerProfileResponse:
    return await service.create_seller_profile(current_user.id, request)


@router.get("/me/seller-profile", response_model=SellerProfileResponse)
async def get_seller_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> SellerProfileResponse:
    return await service.get_seller_profile(current_user.id)


@router.patch("/me/seller-profile", response_model=SellerProfileResponse)
async def update_seller_profile(
    request: SellerProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> SellerProfileResponse:
    return await service.update_seller_profile(current_user.id, request)


@router.post("/me/seller-profile/logo", response_model=SellerProfileResponse)
async def update_store_logo(
    logo_url: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> SellerProfileResponse:
    return await service.update_store_logo(current_user.id, logo_url)


@router.post("/me/seller-profile/banner", response_model=SellerProfileResponse)
async def update_store_banner(
    banner_url: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> SellerProfileResponse:
    return await service.update_store_banner(current_user.id, banner_url)


# --- Preferences ---

@router.get("/me/preferences", response_model=UserPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPreferenceResponse:
    return await service.get_preferences(current_user.id)


@router.patch("/me/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    request: UserPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPreferenceResponse:
    return await service.update_preferences(current_user.id, request)


@router.get("/me/notification-settings", response_model=NotificationSettingResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> NotificationSettingResponse:
    return await service.get_notification_settings(current_user.id)


# --- Devices ---

@router.get("/me/devices", response_model=DeviceListResponse)
async def list_devices(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> DeviceListResponse:
    return await service.list_devices(current_user.id)


@router.put("/me/devices/{device_id}/trust", response_model=DeviceResponse)
async def trust_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> DeviceResponse:
    return await service.trust_device(current_user.id, uuid.UUID(device_id))


@router.put("/me/devices/{device_id}/untrust", response_model=DeviceResponse)
async def untrust_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> DeviceResponse:
    return await service.untrust_device(current_user.id, uuid.UUID(device_id))


@router.delete("/me/devices/{device_id}", status_code=204)
async def remove_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.remove_device(current_user.id, uuid.UUID(device_id))


# --- Wishlist ---

@router.get("/me/wishlist", response_model=list[WishlistItemResponse])
async def list_wishlist(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[WishlistItemResponse]:
    return await service.list_wishlist(current_user.id, page, page_size)


@router.post("/me/wishlist", response_model=WishlistItemResponse, status_code=201)
async def add_to_wishlist(
    request: WishlistAddRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> WishlistItemResponse:
    return await service.add_to_wishlist(current_user.id, request)


@router.delete("/me/wishlist/{product_id}", status_code=204)
async def remove_from_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.remove_from_wishlist(current_user.id, uuid.UUID(product_id))


# --- Favorite Sellers ---

@router.get("/me/favorite-sellers", response_model=list[FavoriteSellerResponse])
async def list_favorite_sellers(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[FavoriteSellerResponse]:
    return await service.list_favorite_sellers(current_user.id)


@router.post("/me/favorite-sellers/{seller_id}", response_model=FavoriteSellerResponse, status_code=201)
async def add_favorite_seller(
    seller_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> FavoriteSellerResponse:
    return await service.add_favorite_seller(current_user.id, uuid.UUID(seller_id))


@router.delete("/me/favorite-sellers/{seller_id}", status_code=204)
async def remove_favorite_seller(
    seller_id: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.remove_favorite_seller(current_user.id, uuid.UUID(seller_id))


# --- Public Profiles ---

@router.get("/public/{username}", response_model=PublicUserProfileResponse)
async def get_public_profile(
    username: str,
    service: UserService = Depends(get_user_service),
) -> PublicUserProfileResponse:
    return await service.get_public_user_profile(username)


@router.get("/store/{store_slug}", response_model=PublicSellerProfileResponse)
async def get_public_store(
    store_slug: str,
    service: UserService = Depends(get_user_service),
) -> PublicSellerProfileResponse:
    return await service.get_public_seller_profile(store_slug)


# --- Search ---

@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    query: str = Query(min_length=1),
    role: str | None = Query(None),
    status: str | None = Query(None),
    is_verified: bool | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserSearchResponse:
    return await service.search_users(query, role, status, is_verified, sort_by, sort_order, page, page_size)


@router.get("/search/sellers", response_model=SellerSearchResponse)
async def search_sellers(
    query: str = Query(min_length=1),
    sort_by: str = Query("rating"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> SellerSearchResponse:
    return await service.search_sellers(query, sort_by, sort_order, page, page_size)
