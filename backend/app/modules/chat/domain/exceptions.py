from __future__ import annotations

from app.exceptions.base import AppException


class ChatDomainError(AppException):
    code: str = "chat_domain_error"
    detail: str = "Chat domain error"


class ConversationNotFoundError(ChatDomainError):
    status_code: int = 404
    code: str = "conversation_not_found"
    detail: str = "Conversation not found"


class MessageNotFoundError(ChatDomainError):
    status_code: int = 404
    code: str = "message_not_found"
    detail: str = "Message not found"


class ChatAccessDeniedError(ChatDomainError):
    status_code: int = 403
    code: str = "chat_access_denied"
    detail: str = "Access to this conversation is denied"
