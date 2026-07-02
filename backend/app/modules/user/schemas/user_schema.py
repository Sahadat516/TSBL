from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    biography: str | None = Field(default=None, max_length=2000)
    date_of_birth: datetime | None = None
    gender: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    website_url: str | None = Field(default=None, max_length=500)
    social_links: dict | None = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    display_name: str | None
    biography: str | None
    avatar_url: str | None
    avatar_thumbnail_url: str | None
    cover_image_url: str | None
    date_of_birth: datetime | None
    gender: str | None
    country: str | None
    state: str | None
    city: str | None
    postal_code: str | None
    website_url: str | None
    social_links: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AvatarUploadResponse(BaseModel):
    avatar_url: str
    avatar_thumbnail_url: str | None = None


class AddressCreateRequest(BaseModel):
    label: str = Field(default="Home", max_length=50)
    recipient_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    street_address: str = Field(min_length=1, max_length=255)
    street_address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool = False
    is_billing: bool = False
    is_shipping: bool = True
    address_type: str = Field(default="shipping", max_length=20)


class AddressUpdateRequest(BaseModel):
    label: str | None = Field(default=None, max_length=50)
    recipient_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    street_address: str | None = Field(default=None, min_length=1, max_length=255)
    street_address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool | None = None
    is_billing: bool | None = None
    is_shipping: bool | None = None
    address_type: str | None = Field(default=None, max_length=20)


class AddressResponse(BaseModel):
    id: UUID
    user_id: UUID
    label: str
    recipient_name: str
    phone: str
    street_address: str
    street_address_line2: str | None
    city: str
    state: str | None
    postal_code: str
    country: str
    latitude: float | None
    longitude: float | None
    is_default: bool
    is_billing: bool
    is_shipping: bool
    address_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AddressListResponse(BaseModel):
    items: list[AddressResponse]
    total: int


class SellerProfileCreateRequest(BaseModel):
    store_name: str = Field(min_length=2, max_length=200)
    store_slug: str = Field(min_length=2, max_length=200)
    store_description: str | None = Field(default=None, max_length=5000)
    business_type: str | None = Field(default=None, max_length=100)
    business_registration_number: str | None = Field(default=None, max_length=100)
    business_address: str | None = Field(default=None, max_length=1000)
    tax_id: str | None = Field(default=None, max_length=100)
    social_links: dict | None = None
    policies: dict | None = None


class SellerProfileUpdateRequest(BaseModel):
    store_name: str | None = Field(default=None, min_length=2, max_length=200)
    store_description: str | None = Field(default=None, max_length=5000)
    business_type: str | None = Field(default=None, max_length=100)
    business_registration_number: str | None = Field(default=None, max_length=100)
    business_address: str | None = Field(default=None, max_length=1000)
    tax_id: str | None = Field(default=None, max_length=100)
    social_links: dict | None = None
    policies: dict | None = None


class SellerProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    store_name: str
    store_slug: str
    store_logo_url: str | None
    store_banner_url: str | None
    store_description: str | None
    store_status: str
    is_verified: bool
    verified_at: datetime | None
    rating: float
    total_sales: int
    total_products: int
    total_reviews: int
    response_time_hours: float | None
    business_type: str | None
    business_registration_number: str | None
    business_address: str | None
    tax_id: str | None
    social_links: dict | None
    policies: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicSellerProfileResponse(BaseModel):
    user_id: UUID
    username: str
    store_name: str
    store_slug: str
    store_logo_url: str | None
    store_banner_url: str | None
    store_description: str | None
    store_status: str
    is_verified: bool
    rating: float
    total_sales: int
    total_products: int
    total_reviews: int
    response_time_hours: float | None
    policies: dict | None
    member_since: datetime | None

    model_config = {"from_attributes": True}


class PublicUserProfileResponse(BaseModel):
    user_id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    biography: str | None
    country: str | None
    member_since: datetime | None
    is_seller: bool = False
    seller_profile: PublicSellerProfileResponse | None = None

    model_config = {"from_attributes": True}


class UserPreferenceResponse(BaseModel):
    theme: str
    language: str
    timezone: str
    currency: str
    date_format: str
    time_format: str
    items_per_page: int
    enable_push_notifications: bool
    enable_email_notifications: bool
    enable_sms_notifications: bool
    enable_marketing_emails: bool
    enable_order_updates: bool
    enable_wallet_alerts: bool
    enable_security_alerts: bool
    enable_newsletter: bool
    profile_visibility: str
    activity_visibility: str
    show_online_status: bool
    allow_messages_from: str

    model_config = {"from_attributes": True}


class UserPreferenceUpdateRequest(BaseModel):
    theme: str | None = Field(default=None, max_length=20)
    language: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, max_length=3)
    date_format: str | None = Field(default=None, max_length=20)
    time_format: str | None = Field(default=None, max_length=10)
    items_per_page: int | None = Field(default=None, ge=5, le=100)
    enable_push_notifications: bool | None = None
    enable_email_notifications: bool | None = None
    enable_sms_notifications: bool | None = None
    enable_marketing_emails: bool | None = None
    enable_order_updates: bool | None = None
    enable_wallet_alerts: bool | None = None
    enable_security_alerts: bool | None = None
    enable_newsletter: bool | None = None
    profile_visibility: str | None = Field(default=None, max_length=20)
    activity_visibility: str | None = Field(default=None, max_length=20)
    show_online_status: bool | None = None
    allow_messages_from: str | None = Field(default=None, max_length=20)


class NotificationSettingResponse(BaseModel):
    email: bool
    sms: bool
    push: bool
    in_app: bool
    marketing: bool
    security_alerts: bool
    order_updates: bool
    wallet_alerts: bool
    newsletter: bool

    model_config = {"from_attributes": True}


class DeviceResponse(BaseModel):
    id: UUID
    device_id: str
    device_name: str | None
    device_type: str | None
    os: str | None
    browser: str | None
    ip_address: str | None
    location: str | None
    is_trusted: bool
    is_current: bool
    last_used_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse]
    total: int


class UserSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    role: str | None = None
    status: str | None = None
    is_verified: bool | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class UserSearchResponse(BaseModel):
    items: list[PublicUserProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SellerSearchResponse(BaseModel):
    items: list[PublicSellerProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WishlistItemResponse(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WishlistAddRequest(BaseModel):
    product_id: UUID
    notes: str | None = Field(default=None, max_length=500)


class FavoriteSellerResponse(BaseModel):
    id: UUID
    seller_id: UUID
    store_name: str | None = None
    store_slug: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardProfileResponse(BaseModel):
    id: UUID
    email: str
    username: str
    phone: str | None
    role: str
    status: str
    is_verified: bool
    profile: ProfileResponse | None
    seller_profile: SellerProfileResponse | None
    preferences: UserPreferenceResponse | None
    stats: dict | None
    created_at: datetime


class UpdateAccountInfoRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    username: str | None = Field(default=None, min_length=3, max_length=50)


class PrivacySettingsResponse(BaseModel):
    profile_visibility: str
    activity_visibility: str
    show_online_status: bool
    allow_messages_from: str


class PrivacySettingsUpdateRequest(BaseModel):
    profile_visibility: str | None = Field(default=None, max_length=20)
    activity_visibility: str | None = Field(default=None, max_length=20)
    show_online_status: bool | None = None
    allow_messages_from: str | None = Field(default=None, max_length=20)
