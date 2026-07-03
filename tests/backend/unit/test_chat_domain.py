from __future__ import annotations

import pytest

from app.modules.chat.domain.value_objects import ConversationStatus, MessageType, ParticipantRole


class TestParticipantRole:
    def test_values(self):
        assert ParticipantRole.BUYER == "buyer"
        assert ParticipantRole.SELLER == "seller"
        assert ParticipantRole.ADMIN == "admin"


class TestConversationStatus:
    def test_values(self):
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.ARCHIVED == "archived"


class TestMessageType:
    def test_values(self):
        assert MessageType.TEXT == "text"
        assert MessageType.IMAGE == "image"
        assert MessageType.FILE == "file"
        assert MessageType.SYSTEM == "system"
