from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.chat.domain.entities import Message
from app.modules.chat.domain.value_objects import ParticipantRole
from app.modules.chat.infrastructure.chat_repository import ConversationRepository, MessageRepository
from app.modules.chat.schemas.chat_schema import (
    ConversationListResponse,
    ConversationResponse,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.msg_repo = MessageRepository(db)

    async def send_message(self, request: SendMessageRequest, sender_id: uuid.UUID) -> MessageResponse:
        if request.conversation_id:
            conv = await self.conv_repo.get(request.conversation_id)
            if not conv:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        elif request.receiver_id:
            buyer_id = min(sender_id, request.receiver_id)
            seller_id = max(sender_id, request.receiver_id)
            conv = await self.conv_repo.get_or_create(buyer_id, seller_id)

            actual_buyer_id = min(sender_id, request.receiver_id)
            if sender_id == actual_buyer_id:
                sender_role = ParticipantRole.BUYER
            else:
                sender_role = ParticipantRole.SELLER
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide conversation_id or receiver_id")

        if conv.buyer_id != sender_id and conv.seller_id != sender_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")

        sender_role = ParticipantRole.BUYER if sender_id == conv.buyer_id else ParticipantRole.SELLER

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conv.id,
            sender_id=sender_id,
            sender_role=sender_role,
            message_type=request.message_type,
            content=request.content,
            media_url=request.media_url,
            media_thumbnail_url=request.media_thumbnail_url,
            media_mime_type=request.media_mime_type,
            media_size=request.media_size,
            reply_to_id=request.reply_to_id,
            metadata=request.metadata,
        )
        await self.msg_repo.create(message)

        conv.last_message_at = datetime.now(timezone.utc)
        conv.last_message_preview = (request.content or "")[:200]
        if sender_role == ParticipantRole.BUYER:
            conv.unread_count_seller += 1
        else:
            conv.unread_count_buyer += 1
        conv.version += 1
        await self.db.flush()

        return MessageResponse.model_validate(message)

    async def list_conversations(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> ConversationListResponse:
        items, total = await self.conv_repo.list_by_user(user_id, page, page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return ConversationListResponse(
            items=[ConversationResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> ConversationResponse:
        conv = await self.conv_repo.get(conversation_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        if conv.buyer_id != user_id and conv.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")
        return ConversationResponse.model_validate(conv)

    async def get_messages(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID, page: int = 1, page_size: int = 50
    ) -> MessageListResponse:
        conv = await self.conv_repo.get(conversation_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        if conv.buyer_id != user_id and conv.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")

        # Mark messages as read
        await self.msg_repo.mark_as_read(conversation_id, user_id)
        if user_id == conv.buyer_id:
            conv.unread_count_buyer = 0
        else:
            conv.unread_count_seller = 0
        conv.version += 1
        await self.db.flush()

        items, total = await self.msg_repo.list_by_conversation(conversation_id, page, page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return MessageListResponse(
            items=[MessageResponse.model_validate(m) for m in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def archive_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> ConversationResponse:
        conv = await self.conv_repo.get(conversation_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        if conv.buyer_id != user_id and conv.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")
        conv.status = "archived"
        conv.version += 1
        await self.db.flush()
        return ConversationResponse.model_validate(conv)
