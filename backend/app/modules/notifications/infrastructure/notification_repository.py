from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.base_repository import BaseRepository
from app.modules.notifications.domain.entities import Notification, NotificationPreference


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Notification)

    async def list_by_user(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Notification], int]:
        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.deleted_at.is_(None),
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                Notification.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        stmt = (
            Notification.__table__.update()
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True, read_at=func.now())
        )
        await self.db.execute(stmt)

    async def mark_as_read(self, notification_id: uuid.UUID) -> None:
        stmt = (
            Notification.__table__.update()
            .where(Notification.id == notification_id)
            .values(is_read=True, read_at=func.now())
        )
        await self.db.execute(stmt)


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, NotificationPreference)

    async def get_by_user_id(self, user_id: uuid.UUID) -> NotificationPreference | None:
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> NotificationPreference:
        prefs = await self.get_by_user_id(user_id)
        if not prefs:
            prefs = NotificationPreference(id=uuid.uuid4(), user_id=user_id)
            self.db.add(prefs)
            await self.db.flush()
        return prefs
