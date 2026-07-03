from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.support.domain.entities import Ticket, TicketMessage


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Ticket)

    async def get_with_messages(self, ticket_id: uuid.UUID) -> Ticket | None:
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.id == ticket_id, Ticket.deleted_at.is_(None))
            .options(selectinload(Ticket.messages))
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Ticket], int]:
        query = select(Ticket).where(
            Ticket.user_id == user_id, Ticket.deleted_at.is_(None)
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Ticket.updated_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(selectinload(Ticket.messages))
        )
        items = list(result.unique().scalars().all())
        return items, total

    async def list_all(
        self, page: int = 1, page_size: int = 20, status: str | None = None
    ) -> tuple[list[Ticket], int]:
        query = select(Ticket).where(Ticket.deleted_at.is_(None))
        if status:
            query = query.where(Ticket.status == status)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Ticket.updated_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(selectinload(Ticket.messages))
        )
        items = list(result.unique().scalars().all())
        return items, total

    async def get_next_ticket_number(self) -> str:
        result = await self.db.execute(
            select(func.count(Ticket.id)).where(Ticket.deleted_at.is_(None))
        )
        count = result.scalar() or 0
        return f"TKT-{count + 1:06d}"


class TicketMessageRepository(BaseRepository[TicketMessage]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, TicketMessage)

    async def list_by_ticket(self, ticket_id: uuid.UUID) -> list[TicketMessage]:
        result = await self.db.execute(
            select(TicketMessage)
            .where(TicketMessage.ticket_id == ticket_id, TicketMessage.deleted_at.is_(None))
            .order_by(TicketMessage.created_at.asc())
        )
        return list(result.scalars().all())
