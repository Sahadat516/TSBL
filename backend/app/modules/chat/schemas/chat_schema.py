from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.chat.domain.value_objects import ConversationStatus, MessageType, ParticipantRole


class SendMessageRequest(BaseModel):
    conversation_id: UUID | None = None
    receiver_id: UUID | None = None
    content: str | None = Field(default=None, max_length=5000)
    message_type: MessageType = MessageType.TEXT
    media_url: str | None = Field(default=None, max_length=500)
    media_thumbnail_url: str | None = Field(default=None, max_length=500)
    media_mime_type: str | None = Field(default=None, max_length=50)
    media_size: int | None = Field(default=None, ge=1)
    reply_to_id: UUID | None = None
    metadata: dict | None = None


class ConversationResponse(BaseModel):
    id: UUID
    buyer_id: UUID
    seller_id: UUID
    order_id: UUID | None = None
    product_id: UUID | None = None
    title: str | None = None
    status: ConversationStatus
    last_message_at: datetime | None = None
    last_message_preview: str | None = None
    unread_count_buyer: int = 0
    unread_count_seller: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    sender_role: ParticipantRole
    message_type: MessageType
    content: str | None = None
    media_url: str | None = None
    media_thumbnail_url: str | None = None
    is_read: bool
    read_at: datetime | None = None
    is_edited: bool
    edited_at: datetime | None = None
    reply_to_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
