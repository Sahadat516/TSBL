from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.support.domain.value_objects import (
    SupportTicketCategory,
    SupportTicketPriority,
    SupportTicketStatus,
)
from app.modules.support.schemas.support_schema import (
    AddTicketMessageRequest,
    CreateTicketRequest,
    TicketMessageResponse,
    TicketResponse,
    UpdateTicketStatusRequest,
)


class TestCreateTicketRequest:
    def test_valid(self):
        req = CreateTicketRequest(
            subject="Payment issue",
            description="My payment was deducted twice",
            category=SupportTicketCategory.PAYMENT_ISSUE,
            priority=SupportTicketPriority.HIGH,
        )
        assert req.subject == "Payment issue"
        assert req.category == SupportTicketCategory.PAYMENT_ISSUE

    def test_empty_subject_raises(self):
        with pytest.raises(ValidationError):
            CreateTicketRequest(
                subject="",
                description="Something wrong",
                category=SupportTicketCategory.OTHER,
            )


class TestUpdateTicketStatusRequest:
    def test_valid(self):
        req = UpdateTicketStatusRequest(status=SupportTicketStatus.CLOSED)
        assert req.status == SupportTicketStatus.CLOSED

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            UpdateTicketStatusRequest(status="unknown")


class TestAddTicketMessageRequest:
    def test_valid_internal(self):
        req = AddTicketMessageRequest(
            content="Investigating this issue",
            is_internal=True,
        )
        assert req.content == "Investigating this issue"
        assert req.is_internal is True

    def test_empty_content_raises(self):
        with pytest.raises(ValidationError):
            AddTicketMessageRequest(content="", is_internal=False)


class TestTicketResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = TicketResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            ticket_number="TKT-000001",
            subject="Payment issue",
            description="Double charge",
            category=SupportTicketCategory.PAYMENT_ISSUE,
            priority=SupportTicketPriority.HIGH,
            status=SupportTicketStatus.OPEN,
            created_at=now,
            updated_at=now,
        )
        assert resp.ticket_number == "TKT-000001"
        assert resp.status == SupportTicketStatus.OPEN

    def test_from_attributes(self):
        assert TicketResponse.model_config.get("from_attributes") is True


class TestTicketMessageResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = TicketMessageResponse(
            id=uuid.uuid4(),
            ticket_id=uuid.uuid4(),
            sender_id=uuid.uuid4(),
            content="Checking this ticket",
            is_internal=True,
            created_at=now,
        )
        assert resp.content == "Checking this ticket"
        assert resp.is_internal is True

    def test_from_attributes(self):
        assert TicketMessageResponse.model_config.get("from_attributes") is True
