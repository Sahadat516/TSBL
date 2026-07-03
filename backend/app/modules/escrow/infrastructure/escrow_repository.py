from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.escrow.domain.entities import Dispute, Escrow, Milestone


class EscrowRepository(BaseRepository[Escrow]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Escrow)

    async def get_by_order_id(self, order_id: uuid.UUID) -> Escrow | None:
        result = await self.db.execute(
            select(Escrow)
            .where(Escrow.order_id == order_id, Escrow.deleted_at.is_(None))
            .options(selectinload(Escrow.milestones), selectinload(Escrow.dispute))
        )
        return result.scalar_one_or_none()

    async def get_with_details(self, escrow_id: uuid.UUID) -> Escrow | None:
        result = await self.db.execute(
            select(Escrow)
            .where(Escrow.id == escrow_id, Escrow.deleted_at.is_(None))
            .options(selectinload(Escrow.milestones), selectinload(Escrow.dispute))
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Escrow], int]:
        query = select(Escrow).where(
            ((Escrow.buyer_id == user_id) | (Escrow.seller_id == user_id)),
            Escrow.deleted_at.is_(None),
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Escrow.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(selectinload(Escrow.milestones), selectinload(Escrow.dispute))
        )
        items = list(result.unique().scalars().all())
        return items, total


class MilestoneRepository(BaseRepository[Milestone]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Milestone)

    async def list_by_escrow(self, escrow_id: uuid.UUID) -> list[Milestone]:
        result = await self.db.execute(
            select(Milestone)
            .where(Milestone.escrow_id == escrow_id, Milestone.deleted_at.is_(None))
            .order_by(Milestone.sort_order)
        )
        return list(result.scalars().all())


class DisputeRepository(BaseRepository[Dispute]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Dispute)

    async def get_by_escrow_id(self, escrow_id: uuid.UUID) -> Dispute | None:
        result = await self.db.execute(
            select(Dispute).where(
                Dispute.escrow_id == escrow_id, Dispute.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Dispute], int]:
        query = select(Dispute).where(
            Dispute.raised_by == user_id, Dispute.deleted_at.is_(None)
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Dispute.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total
