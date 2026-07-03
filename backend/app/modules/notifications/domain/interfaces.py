from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.notifications.domain.entities import Notification, NotificationPreference


class NotificationRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Notification | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Notification], int]: ...

    @abstractmethod
    async def create(self, entity: Notification) -> Notification: ...


class NotificationPreferenceRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> NotificationPreference | None: ...

    @abstractmethod
    async def get_or_create(self, user_id: uuid.UUID) -> NotificationPreference: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...
