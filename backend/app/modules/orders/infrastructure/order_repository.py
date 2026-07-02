from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.base_repository import BaseRepository
from app.common.enums import OrderStatus
from app.modules.orders.domain.entities import Order, OrderItem, OrderStatusHistory


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Order)

    async def find_by_order_number(self, order_number: str) -> Order | None:
        result = await self.db.execute(
            select(Order).where(
                Order.order_number == order_number,
                Order.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_with_items(self, order_id: uuid.UUID) -> Order | None:
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id, Order.deleted_at.is_(None))
            .options(
                selectinload(Order.items),
                selectinload(Order.status_history),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(
        self,
        buyer_id: uuid.UUID,
        status: OrderStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        query = select(Order).where(
            Order.buyer_id == buyer_id,
            Order.deleted_at.is_(None),
        )
        return await self._list_orders(query, status, search, sort_by, sort_order, page, page_size)

    async def list_by_seller(
        self,
        seller_id: uuid.UUID,
        status: OrderStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        query = select(Order).where(
            Order.seller_id == seller_id,
            Order.deleted_at.is_(None),
        )
        return await self._list_orders(query, status, search, sort_by, sort_order, page, page_size)

    async def _list_orders(
        self,
        query,
        status: OrderStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        if status:
            query = query.where(Order.status == status)

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Order.order_number.ilike(pattern),
                    Order.buyer_note.ilike(pattern),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        if total == 0:
            return [], 0

        sort_column = getattr(Order, sort_by, Order.created_at)
        order_fn = sort_column.desc() if sort_order == "desc" else sort_column.asc()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(order_fn)
            .offset(offset)
            .limit(page_size)
            .options(selectinload(Order.items), selectinload(Order.status_history))
        )
        orders = list(result.unique().scalars().all())
        return orders, total

    async def add_status_history(
        self,
        order_id: uuid.UUID,
        from_status: str | None,
        to_status: str,
        changed_by: uuid.UUID | None = None,
        reason: str | None = None,
        is_automated: bool = False,
    ) -> OrderStatusHistory:
        history = OrderStatusHistory(
            id=uuid.uuid4(),
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason,
            is_automated=is_automated,
        )
        self.db.add(history)
        await self.db.flush()
        return history

    async def get_next_order_number(self) -> str:
        result = await self.db.execute(
            select(func.count(Order.id))
        )
        count = result.scalar() or 0
        return f"TSBL-{count + 1:06d}"
