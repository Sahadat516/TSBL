from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.chat.domain.entities import Conversation, Message


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Conversation)

    async def find_existing(
        self, buyer_id: uuid.UUID, seller_id: uuid.UUID
    ) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(
                ((Conversation.buyer_id == buyer_id) & (Conversation.seller_id == seller_id))
                | ((Conversation.buyer_id == seller_id) & (Conversation.seller_id == buyer_id)),
                Conversation.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self, buyer_id: uuid.UUID, seller_id: uuid.UUID, title: str | None = None
    ) -> Conversation:
        existing = await self.find_existing(buyer_id, seller_id)
        if existing:
            return existing
        conv = Conversation(
            id=uuid.uuid4(),
            buyer_id=buyer_id,
            seller_id=seller_id,
            title=title,
        )
        self.db.add(conv)
        await self.db.flush()
        return conv

    async def list_by_user(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Conversation], int]:
        query = select(Conversation).where(
            or_(
                Conversation.buyer_id == user_id,
                Conversation.seller_id == user_id,
            ),
            Conversation.deleted_at.is_(None),
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Conversation.last_message_at.desc().nullslast())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total


class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Message)

    async def list_by_conversation(
        self, conversation_id: uuid.UUID, page: int = 1, page_size: int = 50
    ) -> tuple[list[Message], int]:
        query = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.deleted_at.is_(None),
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Message.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(reversed(result.scalars().all()))
        return items, total

    async def mark_as_read(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            Message.__table__.update()
            .where(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,
                Message.is_read.is_(False),
            )
            .values(is_read=True, read_at=func.now())
        )
        return result.rowcount

    async def get_unread_count(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,
                Message.is_read.is_(False),
                Message.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0
