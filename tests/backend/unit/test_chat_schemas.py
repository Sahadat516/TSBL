from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.chat.domain.value_objects import ConversationStatus, MessageType
from app.modules.chat.schemas.chat_schema import (
    ConversationResponse,
    MarkAsReadRequest,
    MessageResponse,
    SendMessageRequest,
)


class TestSendMessageRequest:
    def test_valid(self):
        req = SendMessageRequest(
            content="Hello",
            message_type=MessageType.TEXT,
        )
        assert req.content == "Hello"
        assert req.message_type == MessageType.TEXT

    def test_empty_content_raises(self):
        with pytest.raises(ValidationError):
            SendMessageRequest(content="", message_type=MessageType.TEXT)


class TestMarkAsReadRequest:
    def test_valid(self):
        req = MarkAsReadRequest(conversation_id=uuid.uuid4(), message_ids=[uuid.uuid4()])
        assert req.conversation_id
        assert len(req.message_ids) == 1


class TestConversationResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = ConversationResponse(
            id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            status=ConversationStatus.ACTIVE,
            last_message_at=now,
            created_at=now,
        )
        assert resp.status == ConversationStatus.ACTIVE

    def test_from_attributes(self):
        assert ConversationResponse.model_config.get("from_attributes") is True


class TestMessageResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = MessageResponse(
            id=uuid.uuid4(),
            conversation_id=uuid.uuid4(),
            sender_id=uuid.uuid4(),
            content="Hello",
            message_type=MessageType.TEXT,
            is_read=False,
            created_at=now,
        )
        assert resp.content == "Hello"
        assert resp.is_read is False

    def test_from_attributes(self):
        assert MessageResponse.model_config.get("from_attributes") is True
