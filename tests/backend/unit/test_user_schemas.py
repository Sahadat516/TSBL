from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.user.schemas.user_schema import (
    ProfileResponse,
    UpdateProfileRequest,
    UserDetailResponse,
    UserPreferenceResponse,
    UserPublicResponse,
    UserSettingsResponse,
)


class TestUpdateProfileRequest:
    def test_empty_payload(self):
        req = UpdateProfileRequest()
        data = req.model_dump(exclude_unset=True)
        assert data == {}

    def test_valid_payload(self):
        req = UpdateProfileRequest(display_name="John", biography="Hello")
        assert req.display_name == "John"
        assert req.biography == "Hello"

    def test_invalid_display_name_too_long(self):
        with pytest.raises(ValidationError):
            UpdateProfileRequest(display_name="a" * 101)

    def test_biography_too_long(self):
        with pytest.raises(ValidationError):
            UpdateProfileRequest(biography="a" * 2001)

    def test_gender_too_long(self):
        with pytest.raises(ValidationError):
            UpdateProfileRequest(gender="a" * 21)

    def test_partial_update(self):
        req = UpdateProfileRequest(display_name="Jane")
        data = req.model_dump(exclude_unset=True)
        assert "display_name" in data
        assert "biography" not in data


class TestProfileResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        uid = uuid.uuid4()
        resp = ProfileResponse(
            id=uid,
            user_id=uid,
            display_name="John",
            created_at=now,
            updated_at=now,
        )
        assert resp.display_name == "John"
        assert resp.biography is None

    def test_from_attributes_config(self):
        assert ProfileResponse.model_config.get("from_attributes") is True


class TestUserSettingsResponse:
    def test_valid_response(self):
        resp = UserSettingsResponse(
            login_notifications=True,
            purchase_notifications=False,
            marketing_opt_in=False,
            two_factor_required=True,
            session_timeout_minutes=30,
        )
        assert resp.login_notifications is True
        assert resp.session_timeout_minutes == 30

    def test_from_attributes_config(self):
        assert UserSettingsResponse.model_config.get("from_attributes") is True


class TestUserPreferenceResponse:
    def test_valid_response(self):
        resp = UserPreferenceResponse(
            theme="dark",
            language="en",
            timezone="UTC",
            currency="USD",
            date_format="YYYY-MM-DD",
            time_format="24h",
            items_per_page=20,
            profile_visibility="public",
            activity_visibility="public",
            show_online_status=True,
        )
        assert resp.theme == "dark"
        assert resp.language == "en"
        assert resp.items_per_page == 20

    def test_from_attributes_config(self):
        assert UserPreferenceResponse.model_config.get("from_attributes") is True


class TestUserPublicResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        uid = uuid.uuid4()
        resp = UserPublicResponse(
            id=uid,
            email="test@example.com",
            username="testuser",
            role="buyer",
            is_verified=True,
            created_at=now,
        )
        assert resp.email == "test@example.com"
        assert resp.role == "buyer"
        assert resp.display_name is None

    def test_defaults(self):
        now = datetime.now(timezone.utc)
        uid = uuid.uuid4()
        resp = UserPublicResponse(
            id=uid,
            email="test@example.com",
            username="testuser",
            role="buyer",
            is_verified=True,
            created_at=now,
        )
        assert resp.is_seller is False
        assert resp.is_buyer is False


class TestUserDetailResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        uid = uuid.uuid4()
        resp = UserDetailResponse(
            id=uid,
            email="test@example.com",
            username="testuser",
            role="buyer",
            status="active",
            is_verified=True,
            created_at=now,
            updated_at=now,
        )
        assert resp.email == "test@example.com"
        assert resp.profile is None
        assert resp.settings is None
        assert resp.preferences is None

    def test_from_attributes_config(self):
        assert UserDetailResponse.model_config.get("from_attributes") is True
