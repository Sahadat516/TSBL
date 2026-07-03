from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.escrow.domain.value_objects import DisputeStatus, EscrowStatus, MilestoneStatus
from app.modules.escrow.schemas.escrow_schema import (
    CreateEscrowRequest,
    DisputeResponse,
    EscrowResponse,
    FundEscrowRequest,
    MilestoneCompletionRequest,
    MilestoneResponse,
    RaiseDisputeRequest,
    ReleaseMilestoneRequest,
    ResolveDisputeRequest,
)


class TestCreateEscrowRequest:
    def test_valid(self):
        req = CreateEscrowRequest(
            order_id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("500.00"),
        )
        assert req.amount == Decimal("500.00")
        assert len(req.milestones) == 0

    def test_with_milestones(self):
        req = CreateEscrowRequest(
            order_id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("500.00"),
            milestones=["Milestone 1", "Milestone 2"],
        )
        assert len(req.milestones) == 2


class TestFundEscrowRequest:
    def test_valid(self):
        req = FundEscrowRequest(escrow_id=uuid.uuid4(), gateway_transaction_id="txn_123")
        assert req.gateway_transaction_id == "txn_123"


class TestReleaseMilestoneRequest:
    def test_valid(self):
        req = ReleaseMilestoneRequest(milestone_id=uuid.uuid4())
        assert req.milestone_id


class TestMilestoneCompletionRequest:
    def test_valid(self):
        req = MilestoneCompletionRequest(milestone_id=uuid.uuid4())
        assert req.milestone_id


class TestRaiseDisputeRequest:
    def test_valid(self):
        req = RaiseDisputeRequest(reason="Item not as described")
        assert req.reason == "Item not as described"

    def test_empty_reason_raises(self):
        with pytest.raises(ValidationError):
            RaiseDisputeRequest(reason="")


class TestResolveDisputeRequest:
    def test_valid(self):
        req = ResolveDisputeRequest(
            buyer_percentage=Decimal("60"),
            seller_percentage=Decimal("40"),
        )
        assert req.buyer_percentage == Decimal("60")

    def test_invalid_percentage(self):
        with pytest.raises(ValidationError):
            ResolveDisputeRequest(buyer_percentage=Decimal("110"), seller_percentage=Decimal("-10"))


class TestEscrowResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = EscrowResponse(
            id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("500.00"),
            currency="USD",
            status=EscrowStatus.HELD,
            created_at=now,
            updated_at=now,
        )
        assert resp.amount == Decimal("500.00")
        assert resp.status == EscrowStatus.HELD

    def test_defaults(self):
        now = datetime.now(timezone.utc)
        resp = EscrowResponse(
            id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            buyer_id=uuid.uuid4(),
            seller_id=uuid.uuid4(),
            amount=Decimal("500.00"),
            currency="USD",
            status=EscrowStatus.AWAITING_FUNDS,
            created_at=now,
            updated_at=now,
        )
        assert resp.milestones == []
        assert resp.disputes == []

    def test_from_attributes(self):
        assert EscrowResponse.model_config.get("from_attributes") is True


class TestMilestoneResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = MilestoneResponse(
            id=uuid.uuid4(),
            escrow_id=uuid.uuid4(),
            title="Initial payment",
            status=MilestoneStatus.PENDING,
            created_at=now,
        )
        assert resp.title == "Initial payment"
        assert resp.status == MilestoneStatus.PENDING

    def test_from_attributes(self):
        assert MilestoneResponse.model_config.get("from_attributes") is True


class TestDisputeResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = DisputeResponse(
            id=uuid.uuid4(),
            escrow_id=uuid.uuid4(),
            raised_by_id=uuid.uuid4(),
            reason="Item damaged",
            status=DisputeStatus.OPEN,
            created_at=now,
        )
        assert resp.status == DisputeStatus.OPEN
        assert resp.reason == "Item damaged"

    def test_from_attributes(self):
        assert DisputeResponse.model_config.get("from_attributes") is True
