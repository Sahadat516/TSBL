from __future__ import annotations

from app.modules.support.domain.value_objects import SupportTicketCategory, SupportTicketPriority, SupportTicketStatus


class TestSupportTicketCategory:
    def test_values(self):
        assert SupportTicketCategory.ORDER_ISSUE == "order_issue"
        assert SupportTicketCategory.PAYMENT_ISSUE == "payment_issue"
        assert SupportTicketCategory.ACCOUNT_ISSUE == "account_issue"
        assert SupportTicketCategory.TECHNICAL_ISSUE == "technical_issue"
        assert SupportTicketCategory.OTHER == "other"


class TestSupportTicketPriority:
    def test_values(self):
        assert SupportTicketPriority.LOW == "low"
        assert SupportTicketPriority.MEDIUM == "medium"
        assert SupportTicketPriority.HIGH == "high"
        assert SupportTicketPriority.URGENT == "urgent"


class TestSupportTicketStatus:
    def test_values(self):
        assert SupportTicketStatus.OPEN == "open"
        assert SupportTicketStatus.IN_PROGRESS == "in_progress"
        assert SupportTicketStatus.RESOLVED == "resolved"
        assert SupportTicketStatus.CLOSED == "closed"
