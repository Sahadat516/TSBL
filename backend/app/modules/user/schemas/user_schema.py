from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    display_name: str | None = None
    biography: str | None = None
    avatar_url: str | None = None
    avatar_thumbnail_url: str | None = None
    cover_image_url: str | None = None
    date_of_birth: datetime | None = None
    gender: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    postal_code: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


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


class UserPublicResponse(BaseModel):
    id: UUID
    email: str
    username: str
    display_name: str | None = None
    avatar_url: str | None = None
    biography: str | None = None
    country: str | None = None
    role: str
    is_verified: bool
    created_at: datetime
    is_seller: bool = False
    is_buyer: bool = False
    seller_profile: dict | None = None
    buyer_profile: dict | None = None

    model_config = {"from_attributes": True}


class UserSettingsResponse(BaseModel):
    login_notifications: bool
    purchase_notifications: bool
    marketing_opt_in: bool
    two_factor_required: bool
    session_timeout_minutes: int

    model_config = {"from_attributes": True}


class UserPreferenceResponse(BaseModel):
    theme: str
    language: str
    timezone: str
    currency: str
    date_format: str
    time_format: str
    items_per_page: int
    profile_visibility: str
    activity_visibility: str
    show_online_status: bool

    model_config = {"from_attributes": True}


class UserDetailResponse(BaseModel):
    id: UUID
    email: str
    username: str
    phone: str | None = None
    role: str
    status: str
    is_verified: bool
    profile_photo_url: str | None = None
    locale: str = "en"
    timezone: str = "UTC"
    profile: ProfileResponse | None = None
    settings: UserSettingsResponse | None = None
    preferences: UserPreferenceResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
