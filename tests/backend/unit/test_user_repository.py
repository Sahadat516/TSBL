from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.user.infrastructure.user_repository import (
    BuyerProfileRepository,
    SellerProfileRepository,
    UserPreferenceRepository,
    UserProfileRepository,
    UserSettingsRepository,
)


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


class TestUserProfileRepository:
    async def test_get_by_user_id_returns_none_when_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = UserProfileRepository(mock_db)
        result = await repo.get_by_user_id(uuid.uuid4())
        assert result is None

    async def test_get_or_create_creates_if_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = UserProfileRepository(mock_db)
        result = await repo.get_or_create(uuid.uuid4())
        assert mock_db.add.called
        assert mock_db.flush.called


class TestBuyerProfileRepository:
    async def test_get_by_user_id_returns_none_when_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = BuyerProfileRepository(mock_db)
        result = await repo.get_by_user_id(uuid.uuid4())
        assert result is None

    async def test_get_or_create_creates_if_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = BuyerProfileRepository(mock_db)
        result = await repo.get_or_create(uuid.uuid4())
        assert mock_db.add.called


class TestSellerProfileRepository:
    async def test_get_by_user_id_returns_none_when_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = SellerProfileRepository(mock_db)
        result = await repo.get_by_user_id(uuid.uuid4())
        assert result is None

    async def test_find_by_store_slug_returns_none_when_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = SellerProfileRepository(mock_db)
        result = await repo.find_by_store_slug("test-store")
        assert result is None


class TestUserSettingsRepository:
    async def test_get_by_user_id_returns_none_when_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = UserSettingsRepository(mock_db)
        result = await repo.get_by_user_id(uuid.uuid4())
        assert result is None

    async def test_get_or_create_creates_if_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = UserSettingsRepository(mock_db)
        result = await repo.get_or_create(uuid.uuid4())
        assert mock_db.add.called


class TestUserPreferenceRepository:
    async def test_get_by_user_id_returns_none_when_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = UserPreferenceRepository(mock_db)
        result = await repo.get_by_user_id(uuid.uuid4())
        assert result is None

    async def test_get_or_create_creates_if_missing(self, mock_db):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        repo = UserPreferenceRepository(mock_db)
        result = await repo.get_or_create(uuid.uuid4())
        assert mock_db.add.called
