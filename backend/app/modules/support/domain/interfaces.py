from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.support.domain.entities import Ticket, TicketMessage


class TicketRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Ticket | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Ticket], int]: ...

    @abstractmethod
    async def create(self, entity: Ticket) -> Ticket: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class TicketMessageRepositoryInterface(ABC):
    @abstractmethod
    async def list_by_ticket(self, ticket_id: uuid.UUID) -> list[TicketMessage]: ...

    @abstractmethod
    async def create(self, entity: TicketMessage) -> TicketMessage: ...
