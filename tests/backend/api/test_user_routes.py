from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.modules.user.domain.entities import UserProfile
from app.modules.user.schemas.user_schema import ProfileResponse, UpdateProfileRequest, UserDetailResponse, UserPublicResponse
from app.modules.user.application.user_service import UserService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def user_service(mock_db):
    return UserService(mock_db)


@pytest.fixture
def sample_user_id():
    return uuid.uuid4()


@pytest.fixture
def sample_user_detail(sample_user_id):
    now = datetime.now(timezone.utc)
    return UserDetailResponse(
        id=sample_user_id,
        email="test@example.com",
        username="testuser",
        phone=None,
        role="buyer",
        status="active",
        is_verified=True,
        profile_photo_url=None,
        locale="en",
        timezone="UTC",
        profile=None,
        settings=None,
        preferences=None,
        created_at=now,
        updated_at=now,
    )


class TestUserService:
    @patch("app.modules.user.application.user_service.select")
    async def test_get_user_success(self, mock_select, user_service, sample_user_id, sample_user_detail):
        mock_user = AsyncMock()
        mock_user.id = sample_user_id
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.phone = None
        mock_user.role = "buyer"
        mock_user.status = "active"
        mock_user.is_verified = True
        mock_user.profile_photo_url = None
        mock_user.locale = "en"
        mock_user.timezone = "UTC"
        mock_user.created_at = sample_user_detail.created_at
        mock_user.updated_at = sample_user_detail.updated_at

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        user_service.db.execute.return_value = mock_result

        user_service.profile_repo.get_by_user_id = AsyncMock(return_value=None)
        user_service.settings_repo.get_by_user_id = AsyncMock(return_value=None)
        user_service.pref_repo.get_by_user_id = AsyncMock(return_value=None)

        result = await user_service.get_user(sample_user_id)
        assert result.email == "test@example.com"
        assert result.username == "testuser"

    @patch("app.modules.user.application.user_service.select")
    async def test_get_user_not_found(self, mock_select, user_service, sample_user_id):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        user_service.db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc:
            await user_service.get_user(sample_user_id)
        assert exc.value.status_code == 404

    async def test_update_profile_creates_if_missing(self, user_service, sample_user_id):
        now = datetime.now(timezone.utc)
        real_profile = UserProfile(
            id=uuid.uuid4(),
            user_id=sample_user_id,
            created_at=now,
            updated_at=now,
        )
        user_service.profile_repo.get_by_user_id = AsyncMock(return_value=None)
        user_service.profile_repo.get_or_create = AsyncMock(return_value=real_profile)

        request = UpdateProfileRequest(display_name="Updated Name")
        result = await user_service.update_profile(sample_user_id, request)
        assert result.display_name == "Updated Name"

    @patch("app.modules.user.application.user_service.select")
    async def test_get_user_by_id_success(self, mock_select, user_service, sample_user_id):
        mock_user = AsyncMock()
        mock_user.id = sample_user_id
        mock_user.email = "public@example.com"
        mock_user.username = "publicuser"
        mock_user.role = "seller"
        mock_user.is_verified = True
        mock_user.profile_photo_url = None
        mock_user.created_at = datetime.now(timezone.utc)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        user_service.db.execute.return_value = mock_result

        user_service.profile_repo.get_by_user_id = AsyncMock(return_value=None)
        user_service.seller_repo.get_by_user_id = AsyncMock(
            return_value=AsyncMock(id=uuid.uuid4(), user_id=sample_user_id)
        )
        user_service.buyer_repo.get_by_user_id = AsyncMock(return_value=None)

        result = await user_service.get_user_by_id(sample_user_id)
        assert result.username == "publicuser"
        assert result.is_seller is True
        assert result.is_buyer is False
