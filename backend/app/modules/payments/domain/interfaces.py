from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from decimal import Decimal

from app.modules.payments.domain.entities import Payment, PaymentMethod, Payout, Refund, TransactionLog


class PaymentRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Payment | None: ...

    @abstractmethod
    async def get_by_order_id(self, order_id: uuid.UUID) -> Payment | None: ...

    @abstractmethod
    async def list_by_buyer(
        self, buyer_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Payment], int]: ...

    @abstractmethod
    async def create(self, entity: Payment) -> Payment: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class PaymentMethodRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> PaymentMethod | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID) -> list[PaymentMethod]: ...

    @abstractmethod
    async def create(self, entity: PaymentMethod) -> PaymentMethod: ...

    @abstractmethod
    async def soft_delete(self, entity_id: uuid.UUID) -> None: ...


class PayoutRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Payout | None: ...

    @abstractmethod
    async def list_by_seller(
        self, seller_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Payout], int]: ...

    @abstractmethod
    async def create(self, entity: Payout) -> Payout: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class RefundRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Refund | None: ...

    @abstractmethod
    async def list_by_payment(self, payment_id: uuid.UUID) -> list[Refund]: ...

    @abstractmethod
    async def create(self, entity: Refund) -> Refund: ...


class TransactionLogRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, entity: TransactionLog) -> TransactionLog: ...

    @abstractmethod
    async def list_by_payment(self, payment_id: uuid.UUID) -> list[TransactionLog]: ...
