from __future__ import annotations

from app.modules.escrow.domain.exceptions import (
    DisputeNotFoundError,
    EscrowAccessDeniedError,
    EscrowDomainError,
    EscrowFundsNotClearedError,
    EscrowNotFoundError,
    EscrowStatusConflictError,
    MilestoneNotFoundError,
    MilestoneStatusConflictError,
)


class TestEscrowExceptions:
    def test_hierarchy(self):
        assert issubclass(EscrowNotFoundError, EscrowDomainError)
        assert issubclass(DisputeNotFoundError, EscrowDomainError)

    def test_status_codes(self):
        assert EscrowNotFoundError.status_code == 404
        assert EscrowAccessDeniedError.status_code == 403
        assert EscrowFundsNotClearedError.status_code == 400
        assert EscrowStatusConflictError.status_code == 409

    def test_error_codes(self):
        assert EscrowNotFoundError.code == "escrow_not_found"
        assert EscrowStatusConflictError.code == "escrow_status_conflict"
        assert MilestoneNotFoundError.code == "milestone_not_found"
        assert MilestoneStatusConflictError.code == "milestone_status_conflict"
