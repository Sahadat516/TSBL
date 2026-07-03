from __future__ import annotations

from app.exceptions.base import AppException


class SupportDomainError(AppException):
    code: str = "support_domain_error"
    detail: str = "Support domain error"


class TicketNotFoundError(SupportDomainError):
    status_code: int = 404
    code: str = "ticket_not_found"
    detail: str = "Ticket not found"


class TicketAccessDeniedError(SupportDomainError):
    status_code: int = 403
    code: str = "ticket_access_denied"
    detail: str = "Access to this ticket is denied"


class TicketAlreadyClosedError(SupportDomainError):
    status_code: int = 400
    code: str = "ticket_already_closed"
    detail: str = "Ticket is already closed"
