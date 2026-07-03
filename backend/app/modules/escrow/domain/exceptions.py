from __future__ import annotations

from app.exceptions.base import AppException


class EscrowDomainError(AppException):
    code: str = "escrow_domain_error"
    detail: str = "Escrow domain error"


class EscrowNotFoundError(EscrowDomainError):
    status_code: int = 404
    code: str = "escrow_not_found"
    detail: str = "Escrow not found"


class EscrowAlreadyFundedError(EscrowDomainError):
    status_code: int = 409
    code: str = "escrow_already_funded"
    detail: str = "Escrow has already been funded"


class EscrowInvalidStatusError(EscrowDomainError):
    status_code: int = 400
    code: str = "escrow_invalid_status"
    detail: str = "Escrow is not in the correct status for this action"


class MilestoneNotFoundError(EscrowDomainError):
    status_code: int = 404
    code: str = "milestone_not_found"
    detail: str = "Milestone not found"


class EscrowAccessDeniedError(EscrowDomainError):
    status_code: int = 403
    code: str = "escrow_access_denied"
    detail: str = "Access to this escrow is denied"
