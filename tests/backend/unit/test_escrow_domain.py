from __future__ import annotations

import pytest

from app.modules.escrow.domain.value_objects import DisputeStatus, EscrowStatus, MilestoneStatus


class TestEscrowStatus:
    def test_values(self):
        assert EscrowStatus.HELD == "held"
        assert EscrowStatus.RELEASED == "released"
        assert EscrowStatus.CANCELLED == "cancelled"
        assert EscrowStatus.AWAITING_FUNDS == "awaiting_funds"


class TestMilestoneStatus:
    def test_values(self):
        assert MilestoneStatus.PENDING == "pending"
        assert MilestoneStatus.COMPLETED == "completed"
        assert MilestoneStatus.DISPUTED == "disputed"


class TestDisputeStatus:
    def test_values(self):
        assert DisputeStatus.OPEN == "open"
        assert DisputeStatus.RESOLVED == "resolved"
        assert DisputeStatus.ESCALATED == "escalated"
