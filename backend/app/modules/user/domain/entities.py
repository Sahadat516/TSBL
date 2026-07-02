from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    social_links: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="profile")


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    preferred_categories: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    price_range_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_range_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    purchase_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    interests: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    total_purchases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    last_purchase_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="buyer_profile")

    __table_args__ = (
        CheckConstraint("price_range_min >= 0", name="ck_buyer_price_min"),
        CheckConstraint("price_range_max >= 0", name="ck_buyer_price_max"),
        CheckConstraint("total_purchases >= 0", name="ck_buyer_total_purchases"),
        CheckConstraint("total_spent >= 0", name="ck_buyer_total_spent"),
    )


class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    store_name: Mapped[str] = mapped_column(String(200), nullable=False)
    store_slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    store_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    store_banner_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    store_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    store_status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_sales: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_products: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_registration_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    social_links: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    policies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="seller_profile")

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_seller_rating"),
        CheckConstraint("total_sales >= 0", name="ck_seller_total_sales"),
        CheckConstraint("total_products >= 0", name="ck_seller_total_products"),
        CheckConstraint("total_reviews >= 0", name="ck_seller_total_reviews"),
        CheckConstraint("response_time_hours >= 0", name="ck_seller_response_time"),
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    login_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    purchase_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="settings")

    __table_args__ = (
        CheckConstraint("session_timeout_minutes >= 1 AND session_timeout_minutes <= 1440", name="ck_settings_session_timeout"),
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    theme: Mapped[str] = mapped_column(String(20), default="light", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    date_format: Mapped[str] = mapped_column(String(20), default="YYYY-MM-DD", nullable=False)
    time_format: Mapped[str] = mapped_column(String(10), default="24h", nullable=False)
    items_per_page: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    profile_visibility: Mapped[str] = mapped_column(String(20), default="public", nullable=False)
    activity_visibility: Mapped[str] = mapped_column(String(20), default="public", nullable=False)
    show_online_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="preferences")

    __table_args__ = (
        CheckConstraint("items_per_page >= 5 AND items_per_page <= 100", name="ck_pref_items_per_page"),
    )
