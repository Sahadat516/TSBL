from __future__ import annotations

from app.modules.chat.domain.exceptions import (
    ChatDomainError,
    ConversationAccessDeniedError,
    ConversationArchivedError,
    ConversationNotFoundError,
    MessageNotFoundError,
)


class TestChatExceptions:
    def test_hierarchy(self):
        assert issubclass(ConversationNotFoundError, ChatDomainError)

    def test_status_codes(self):
        assert ConversationNotFoundError.status_code == 404
        assert ConversationAccessDeniedError.status_code == 403
        assert ConversationArchivedError.status_code == 400

    def test_error_codes(self):
        assert ConversationNotFoundError.code == "conversation_not_found"
        assert ConversationAccessDeniedError.code == "conversation_access_denied"
        assert ConversationArchivedError.code == "conversation_archived"
        assert MessageNotFoundError.code == "message_not_found"
