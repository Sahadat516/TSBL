from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.user.domain.entities import (
    BuyerProfile,
    SellerProfile,
    UserPreference,
    UserProfile,
    UserSettings,
)


class UserProfileRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None: ...

    @abstractmethod
    async def get_or_create(self, user_id: uuid.UUID) -> UserProfile: ...

    @abstractmethod
    async def create(self, entity: UserProfile) -> UserProfile: ...

    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> UserProfile | None: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...

    @abstractmethod
    async def soft_delete(self, entity_id: uuid.UUID) -> None: ...


class BuyerProfileRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> BuyerProfile | None: ...

    @abstractmethod
    async def get_or_create(self, user_id: uuid.UUID) -> BuyerProfile: ...

    @abstractmethod
    async def create(self, entity: BuyerProfile) -> BuyerProfile: ...


class SellerProfileRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> SellerProfile | None: ...

    @abstractmethod
    async def find_by_store_slug(self, slug: str) -> SellerProfile | None: ...

    @abstractmethod
    async def create(self, entity: SellerProfile) -> SellerProfile: ...


class UserSettingsRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None: ...

    @abstractmethod
    async def get_or_create(self, user_id: uuid.UUID) -> UserSettings: ...

    @abstractmethod
    async def create(self, entity: UserSettings) -> UserSettings: ...


class UserPreferenceRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> UserPreference | None: ...

    @abstractmethod
    async def get_or_create(self, user_id: uuid.UUID) -> UserPreference: ...

    @abstractmethod
    async def create(self, entity: UserPreference) -> UserPreference: ...
