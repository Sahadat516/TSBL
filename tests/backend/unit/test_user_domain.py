from __future__ import annotations

import uuid

import pytest

from app.modules.user.domain.value_objects import Bio, DisplayName, ProfileVisibility, StoreSlug, StoreStatus, UserId


class TestUserId:
    def test_creation(self):
        uid = uuid.uuid4()
        vo = UserId(uid)
        assert vo.value == uid
        assert str(vo) == str(uid)


class TestDisplayName:
    def test_valid_name(self):
        dn = DisplayName("John Doe")
        assert dn.value == "John Doe"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            DisplayName("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="100"):
            DisplayName("a" * 101)


class TestStoreSlug:
    def test_valid_slug(self):
        slug = StoreSlug("my-store")
        assert slug.value == "my-store"

    def test_empty_slug_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            StoreSlug("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="200"):
            StoreSlug("a" * 201)


class TestBio:
    def test_valid_bio(self):
        bio = Bio("A short bio")
        assert bio.value == "A short bio"

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="2000"):
            Bio("a" * 2001)

    def test_empty_bio(self):
        bio = Bio("")
        assert bio.value == ""


class TestProfileVisibility:
    def test_valid_values(self):
        assert ProfileVisibility.is_valid("public") is True
        assert ProfileVisibility.is_valid("private") is True
        assert ProfileVisibility.is_valid("contacts_only") is True

    def test_invalid_value(self):
        assert ProfileVisibility.is_valid("unknown") is False


class TestStoreStatus:
    def test_valid_values(self):
        assert StoreStatus.is_valid("active") is True
        assert StoreStatus.is_valid("inactive") is True
        assert StoreStatus.is_valid("suspended") is True
        assert StoreStatus.is_valid("closed") is True

    def test_invalid_value(self):
        assert StoreStatus.is_valid("unknown") is False
