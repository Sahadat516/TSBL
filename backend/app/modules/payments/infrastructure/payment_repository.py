from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.payments.domain.entities import Payment, PaymentMethod, Payout, Refund, TransactionLog


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Payment)

    async def get_by_order_id(self, order_id: uuid.UUID) -> Payment | None:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.order_id == order_id, Payment.deleted_at.is_(None))
            .options(selectinload(Payment.refunds), selectinload(Payment.transaction_logs))
        )
        return result.scalar_one_or_none()

    async def get_with_details(self, payment_id: uuid.UUID) -> Payment | None:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.id == payment_id, Payment.deleted_at.is_(None))
            .options(selectinload(Payment.refunds), selectinload(Payment.transaction_logs))
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(
        self, buyer_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Payment], int]:
        query = select(Payment).where(
            Payment.buyer_id == buyer_id, Payment.deleted_at.is_(None)
        )
        return await self._list_paginated(query, page, page_size)

    async def list_by_seller(
        self, seller_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Payment], int]:
        query = select(Payment).where(
            Payment.seller_id == seller_id, Payment.deleted_at.is_(None)
        )
        return await self._list_paginated(query, page, page_size)

    async def _list_paginated(self, query, page: int, page_size: int) -> tuple[list[Payment], int]:
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(selectinload(Payment.refunds), selectinload(Payment.transaction_logs))
        )
        items = list(result.unique().scalars().all())
        total_pages = max(1, (total + page_size - 1) // page_size)
        return items, total


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, PaymentMethod)

    async def list_by_user(self, user_id: uuid.UUID) -> list[PaymentMethod]:
        result = await self.db.execute(
            select(PaymentMethod)
            .where(PaymentMethod.user_id == user_id, PaymentMethod.deleted_at.is_(None))
            .order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc())
        )
        return list(result.scalars().all())

    async def unset_default(self, user_id: uuid.UUID) -> None:
        stmt = (
            PaymentMethod.__table__.update()
            .where(PaymentMethod.user_id == user_id, PaymentMethod.is_default.is_(True))
            .values(is_default=False)
        )
        await self.db.execute(stmt)


class PayoutRepository(BaseRepository[Payout]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Payout)

    async def list_by_seller(
        self, seller_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Payout], int]:
        query = select(Payout).where(
            Payout.seller_id == seller_id, Payout.deleted_at.is_(None)
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Payout.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total


class RefundRepository(BaseRepository[Refund]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Refund)

    async def list_by_payment(self, payment_id: uuid.UUID) -> list[Refund]:
        result = await self.db.execute(
            select(Refund).where(
                Refund.payment_id == payment_id, Refund.deleted_at.is_(None)
            ).order_by(Refund.created_at.desc())
        )
        return list(result.scalars().all())


class TransactionLogRepository(BaseRepository[TransactionLog]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, TransactionLog)

    async def list_by_payment(self, payment_id: uuid.UUID) -> list[TransactionLog]:
        result = await self.db.execute(
            select(TransactionLog).where(
                TransactionLog.payment_id == payment_id, TransactionLog.deleted_at.is_(None)
            ).order_by(TransactionLog.created_at.asc())
        )
        return list(result.scalars().all())
