from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.escrow.domain.entities import Dispute, Escrow, Milestone


class EscrowRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Escrow | None: ...

    @abstractmethod
    async def get_by_order_id(self, order_id: uuid.UUID) -> Escrow | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Escrow], int]: ...

    @abstractmethod
    async def create(self, entity: Escrow) -> Escrow: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class MilestoneRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Milestone | None: ...

    @abstractmethod
    async def list_by_escrow(self, escrow_id: uuid.UUID) -> list[Milestone]: ...

    @abstractmethod
    async def create(self, entity: Milestone) -> Milestone: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class DisputeRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Dispute | None: ...

    @abstractmethod
    async def get_by_escrow_id(self, escrow_id: uuid.UUID) -> Dispute | None: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Dispute], int]: ...

    @abstractmethod
    async def create(self, entity: Dispute) -> Dispute: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...
