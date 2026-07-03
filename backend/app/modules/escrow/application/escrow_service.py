from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.escrow.domain.entities import Dispute, Escrow, Milestone
from app.modules.escrow.domain.value_objects import (
    DisputeReason,
    DisputeStatus,
    EscrowStatus,
    MilestoneStatus,
)
from app.modules.escrow.infrastructure.escrow_repository import (
    DisputeRepository,
    EscrowRepository,
    MilestoneRepository,
)
from app.modules.escrow.schemas.escrow_schema import (
    CreateEscrowRequest,
    DisputeResponse,
    EscrowListResponse,
    EscrowResponse,
    MilestoneResponse,
    RaiseDisputeRequest,
    ReleaseFundsRequest,
    ResolveDisputeRequest,
)
from app.modules.orders.domain.entities import Order


class EscrowService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.escrow_repo = EscrowRepository(db)
        self.milestone_repo = MilestoneRepository(db)
        self.dispute_repo = DisputeRepository(db)

    async def create_escrow(self, request: CreateEscrowRequest, buyer_id: uuid.UUID) -> EscrowResponse:
        result = await self.db.execute(
            select(Order).where(Order.id == request.order_id, Order.deleted_at.is_(None))
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.buyer_id != buyer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")

        existing = await self.escrow_repo.get_by_order_id(request.order_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Escrow already exists for this order")

        fee_amount = (order.total_amount * Decimal("0.025")).quantize(Decimal("0.01"))

        escrow = Escrow(
            id=uuid.uuid4(),
            order_id=request.order_id,
            buyer_id=buyer_id,
            seller_id=order.seller_id,
            total_amount=order.total_amount,
            fee_amount=fee_amount,
            currency=order.currency,
            status=EscrowStatus.PENDING_FUNDING,
            has_milestones=request.has_milestones,
            metadata=request.metadata,
        )
        await self.escrow_repo.create(escrow)

        total_milestone_amount = Decimal("0.00")
        if request.milestones:
            for m in request.milestones:
                milestone = Milestone(
                    id=uuid.uuid4(),
                    escrow_id=escrow.id,
                    title=m.title,
                    description=m.description,
                    amount=m.amount,
                    sort_order=m.sort_order,
                    due_date=m.due_date,
                )
                self.db.add(milestone)
                total_milestone_amount += m.amount

            if total_milestone_amount != order.total_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Milestone total ({total_milestone_amount}) must equal order total ({order.total_amount})",
                )

        await self.db.flush()

        AuditLogger.log(
            action="ESCROW_CREATED",
            actor_id=str(buyer_id),
            resource="escrow",
            resource_id=str(escrow.id),
            details={"order_id": str(request.order_id), "amount": str(order.total_amount)},
        )

        return await self._load_escrow_response(escrow.id)

    async def get_escrow(self, escrow_id: uuid.UUID, user_id: uuid.UUID) -> EscrowResponse:
        escrow = await self.escrow_repo.get_with_details(escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        if escrow.buyer_id != user_id and escrow.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your escrow")
        return await self._load_escrow_response(escrow.id)

    async def list_my_escrows(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> EscrowListResponse:
        items, total = await self.escrow_repo.list_by_user(user_id, page, page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return EscrowListResponse(
            items=[EscrowResponse.model_validate(e) for e in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def fund_escrow(self, escrow_id: uuid.UUID, user_id: uuid.UUID) -> EscrowResponse:
        escrow = await self.escrow_repo.get_with_details(escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        if escrow.buyer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only buyer can fund escrow")
        if escrow.status != EscrowStatus.PENDING_FUNDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow is not pending funding")

        escrow.status = EscrowStatus.FUNDED
        escrow.funded_at = datetime.now(timezone.utc)
        escrow.version += 1

        if escrow.has_milestones:
            escrow.status = EscrowStatus.IN_PROGRESS
        await self.db.flush()

        AuditLogger.log(
            action="ESCROW_FUNDED",
            actor_id=str(user_id),
            resource="escrow",
            resource_id=str(escrow.id),
        )

        return await self._load_escrow_response(escrow.id)

    async def release_funds(
        self, escrow_id: uuid.UUID, request: ReleaseFundsRequest, user_id: uuid.UUID
    ) -> EscrowResponse:
        escrow = await self.escrow_repo.get_with_details(escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        if escrow.buyer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only buyer can release funds")
        if escrow.status not in (EscrowStatus.FUNDED, EscrowStatus.IN_PROGRESS):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow is not in releasable status")

        release_amount = Decimal("0.00")

        if request.milestone_id and escrow.has_milestones:
            milestone = next(
                (m for m in escrow.milestones if m.id == request.milestone_id), None
            )
            if not milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
            if milestone.status != MilestoneStatus.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Milestone is not completed"
                )
            milestone.status = MilestoneStatus.APPROVED
            milestone.approved_at = datetime.now(timezone.utc)
            release_amount = milestone.amount
        elif request.amount:
            release_amount = request.amount
        else:
            release_amount = escrow.total_amount - escrow.released_amount - escrow.refunded_amount

        if release_amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Release amount must be positive")

        remaining = escrow.total_amount - escrow.released_amount - escrow.refunded_amount
        if release_amount > remaining:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Release amount exceeds remaining funds")

        escrow.released_amount += release_amount
        escrow.version += 1

        if escrow.released_amount >= escrow.total_amount - escrow.refunded_amount:
            escrow.status = EscrowStatus.RELEASED
            escrow.released_at = datetime.now(timezone.utc)

        await self.db.flush()

        AuditLogger.log(
            action="ESCROW_RELEASED",
            actor_id=str(user_id),
            resource="escrow",
            resource_id=str(escrow.id),
            details={"amount": str(release_amount)},
        )

        return await self._load_escrow_response(escrow.id)

    async def cancel_escrow(self, escrow_id: uuid.UUID, user_id: uuid.UUID, reason: str) -> EscrowResponse:
        escrow = await self.escrow_repo.get_with_details(escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        if escrow.buyer_id != user_id and escrow.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your escrow")
        if escrow.status in (EscrowStatus.RELEASED, EscrowStatus.REFUNDED, EscrowStatus.CANCELLED):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow cannot be cancelled")

        escrow.status = EscrowStatus.CANCELLED
        escrow.cancelled_at = datetime.now(timezone.utc)
        escrow.cancellation_reason = reason
        escrow.version += 1
        await self.db.flush()

        AuditLogger.log(
            action="ESCROW_CANCELLED",
            actor_id=str(user_id),
            resource="escrow",
            resource_id=str(escrow.id),
            details={"reason": reason},
        )

        return await self._load_escrow_response(escrow.id)

    async def raise_dispute(
        self, escrow_id: uuid.UUID, request: RaiseDisputeRequest, user_id: uuid.UUID
    ) -> DisputeResponse:
        escrow = await self.escrow_repo.get_with_details(escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        if escrow.buyer_id != user_id and escrow.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your escrow")
        if escrow.status in (EscrowStatus.RELEASED, EscrowStatus.REFUNDED, EscrowStatus.CANCELLED):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot dispute a closed escrow")
        if escrow.dispute:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dispute already exists")

        escrow.status = EscrowStatus.DISPUTED
        escrow.version += 1

        dispute = Dispute(
            id=uuid.uuid4(),
            escrow_id=escrow_id,
            raised_by=user_id,
            reason=request.reason,
            description=request.description,
            status=DisputeStatus.OPEN,
            evidence=request.evidence,
        )
        await self.dispute_repo.create(dispute)
        await self.db.flush()

        AuditLogger.log(
            action="ESCROW_DISPUTE_RAISED",
            actor_id=str(user_id),
            resource="dispute",
            resource_id=str(dispute.id),
            details={"reason": request.reason.value},
        )

        return DisputeResponse.model_validate(dispute)

    async def resolve_dispute(
        self, dispute_id: uuid.UUID, request: ResolveDisputeRequest, admin_id: uuid.UUID
    ) -> DisputeResponse:
        dispute = await self.dispute_repo.get(dispute_id)
        if not dispute:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")
        if dispute.status == DisputeStatus.CLOSED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dispute already closed")

        escrow = await self.escrow_repo.get_with_details(dispute.escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")

        dispute.status = request.resolution
        dispute.resolution_note = request.note
        dispute.resolved_by = admin_id
        dispute.resolved_at = datetime.now(timezone.utc)
        dispute.version += 1

        if request.refund_percentage is not None:
            refund_amount = (escrow.total_amount * request.refund_percentage / Decimal("100")).quantize(Decimal("0.01"))
            escrow.refunded_amount = refund_amount
            escrow.released_amount = escrow.total_amount - refund_amount - escrow.fee_amount

        escrow.status = EscrowStatus.RELEASED if escrow.released_amount > 0 else EscrowStatus.REFUNDED
        escrow.released_at = datetime.now(timezone.utc)
        escrow.version += 1
        await self.db.flush()

        AuditLogger.log(
            action="DISPUTE_RESOLVED",
            actor_id=str(admin_id),
            resource="dispute",
            resource_id=str(dispute.id),
            details={"resolution": request.resolution.value},
        )

        return DisputeResponse.model_validate(dispute)

    async def complete_milestone(
        self, milestone_id: uuid.UUID, user_id: uuid.UUID
    ) -> MilestoneResponse:
        milestone = await self.milestone_repo.get(milestone_id)
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        escrow = await self.escrow_repo.get(milestone.escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        if escrow.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only seller can mark milestone complete")
        if milestone.status != MilestoneStatus.IN_PROGRESS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Milestone is not in progress")

        milestone.status = MilestoneStatus.COMPLETED
        milestone.completed_at = datetime.now(timezone.utc)
        milestone.version += 1
        await self.db.flush()

        return MilestoneResponse.model_validate(milestone)

    async def _load_escrow_response(self, escrow_id: uuid.UUID) -> EscrowResponse:
        escrow = await self.escrow_repo.get_with_details(escrow_id)
        if not escrow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
        return EscrowResponse.model_validate(escrow)
