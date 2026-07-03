from __future__ import annotations

from app.modules.support.domain.exceptions import (
    SupportDomainError,
    SupportTicketAlreadyClosedError,
    SupportTicketNotFoundError,
)


class TestSupportExceptions:
    def test_hierarchy(self):
        assert issubclass(SupportTicketNotFoundError, SupportDomainError)
        assert issubclass(SupportTicketAlreadyClosedError, SupportDomainError)

    def test_status_codes(self):
        assert SupportTicketNotFoundError.status_code == 404
        assert SupportTicketAlreadyClosedError.status_code == 400

    def test_error_codes(self):
        assert SupportTicketNotFoundError.code == "ticket_not_found"
        assert SupportTicketAlreadyClosedError.code == "ticket_already_closed"
