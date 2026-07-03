from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.chat.domain.entities import Conversation, Message


class ConversationRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Conversation | None: ...

    @abstractmethod
    async def get_or_create(self, buyer_id: uuid.UUID, seller_id: uuid.UUID) -> Conversation: ...

    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID, page: int, page_size: int) -> tuple[list[Conversation], int]: ...

    @abstractmethod
    async def create(self, entity: Conversation) -> Conversation: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class MessageRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Message | None: ...

    @abstractmethod
    async def list_by_conversation(
        self, conversation_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Message], int]: ...

    @abstractmethod
    async def create(self, entity: Message) -> Message: ...

    @abstractmethod
    async def mark_as_read(self, message_ids: list[uuid.UUID]) -> None: ...
