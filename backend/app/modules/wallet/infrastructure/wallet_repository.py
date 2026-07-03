from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.wallet.domain.entities import Transaction, Wallet


class WalletRepository(BaseRepository[Wallet]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Wallet)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Wallet | None:
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id, Wallet.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> Wallet:
        wallet = await self.get_by_user_id(user_id)
        if not wallet:
            wallet = Wallet(id=uuid.uuid4(), user_id=user_id)
            self.db.add(wallet)
            await self.db.flush()
        return wallet


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Transaction)

    async def list_by_wallet(
        self, wallet_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Transaction], int]:
        query = select(Transaction).where(
            Transaction.wallet_id == wallet_id, Transaction.deleted_at.is_(None)
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Transaction.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_balance_snapshot(self, wallet_id: uuid.UUID, before_id: uuid.UUID) -> Decimal:
        result = await self.db.execute(
            select(Transaction.balance_before).where(
                Transaction.id == before_id,
                Transaction.wallet_id == wallet_id,
                Transaction.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        return row if row is not None else Decimal("0.00")
