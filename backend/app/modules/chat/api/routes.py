from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.chat.application.chat_service import ChatService
from app.modules.chat.schemas.chat_schema import (
    ConversationListResponse,
    ConversationResponse,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


@router.post("/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> MessageResponse:
    return await service.send_message(request, current_user.id)


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ConversationListResponse:
    return await service.list_conversations(current_user.id, page=page, page_size=page_size)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ConversationResponse:
    return await service.get_conversation(uuid.UUID(conversation_id), current_user.id)


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> MessageListResponse:
    return await service.get_messages(
        uuid.UUID(conversation_id), current_user.id, page=page, page_size=page_size
    )


@router.patch("/conversations/{conversation_id}/archive", response_model=ConversationResponse)
async def archive_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ConversationResponse:
    return await service.archive_conversation(uuid.UUID(conversation_id), current_user.id)
