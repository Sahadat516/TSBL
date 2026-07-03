from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from decimal import Decimal

from app.modules.wallet.domain.entities import Transaction, Wallet


class WalletRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Wallet | None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> Wallet | None: ...

    @abstractmethod
    async def create(self, entity: Wallet) -> Wallet: ...

    @abstractmethod
    async def update(self, entity_id: uuid.UUID, values: dict) -> None: ...


class TransactionRepositoryInterface(ABC):
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Transaction | None: ...

    @abstractmethod
    async def list_by_wallet(
        self, wallet_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Transaction], int]: ...

    @abstractmethod
    async def create(self, entity: Transaction) -> Transaction: ...

    @abstractmethod
    async def get_balance_snapshot(self, wallet_id: uuid.UUID, before: uuid.UUID) -> Decimal: ...
