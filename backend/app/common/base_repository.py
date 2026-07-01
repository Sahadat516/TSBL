from typing import Generic, TypeVar

from sqlalchemy import select, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model_class: type[T]):
        self.db = db
        self.model_class = model_class

    async def create(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def get(self, entity_id) -> T | None:
        result = await self.db.execute(
            select(self.model_class).where(
                self.model_class.id == entity_id,
                self.model_class.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(self.model_class)
            .where(self.model_class.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(self, entity_id, values: dict):
        stmt = (
            sa_update(self.model_class)
            .where(self.model_class.id == entity_id)
            .values(**values)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def soft_delete(self, entity_id):
        stmt = (
            sa_update(self.model_class)
            .where(self.model_class.id == entity_id)
            .values(deleted_at=__import__("datetime").datetime.now())
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def hard_delete(self, entity_id):
        stmt = sa_delete(self.model_class).where(self.model_class.id == entity_id)
        await self.db.execute(stmt)
        await self.db.flush()
