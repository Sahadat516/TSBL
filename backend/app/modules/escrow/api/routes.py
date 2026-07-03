from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.modules.auth.domain.entities import User
from app.modules.escrow.application.escrow_service import EscrowService
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

router = APIRouter(prefix="/escrows", tags=["Escrow"])


def get_escrow_service(db: AsyncSession = Depends(get_db)) -> EscrowService:
    return EscrowService(db)


@router.post("", response_model=EscrowResponse, status_code=201)
async def create_escrow(
    request: CreateEscrowRequest,
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> EscrowResponse:
    return await service.create_escrow(request, current_user.id)


@router.get("", response_model=EscrowListResponse)
async def list_escrows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> EscrowListResponse:
    return await service.list_my_escrows(current_user.id, page=page, page_size=page_size)


@router.get("/{escrow_id}", response_model=EscrowResponse)
async def get_escrow(
    escrow_id: str,
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> EscrowResponse:
    return await service.get_escrow(uuid.UUID(escrow_id), current_user.id)


@router.post("/{escrow_id}/fund", response_model=EscrowResponse)
async def fund_escrow(
    escrow_id: str,
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> EscrowResponse:
    return await service.fund_escrow(uuid.UUID(escrow_id), current_user.id)


@router.post("/{escrow_id}/release", response_model=EscrowResponse)
async def release_funds(
    escrow_id: str,
    request: ReleaseFundsRequest,
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> EscrowResponse:
    return await service.release_funds(uuid.UUID(escrow_id), request, current_user.id)


@router.post("/{escrow_id}/cancel", response_model=EscrowResponse)
async def cancel_escrow(
    escrow_id: str,
    reason: str = Query(min_length=1, max_length=500),
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> EscrowResponse:
    return await service.cancel_escrow(uuid.UUID(escrow_id), current_user.id, reason)


@router.post("/{escrow_id}/dispute", response_model=DisputeResponse)
async def raise_dispute(
    escrow_id: str,
    request: RaiseDisputeRequest,
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> DisputeResponse:
    return await service.raise_dispute(uuid.UUID(escrow_id), request, current_user.id)


@router.post("/{escrow_id}/milestones/{milestone_id}/complete", response_model=MilestoneResponse)
async def complete_milestone(
    escrow_id: str,
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    service: EscrowService = Depends(get_escrow_service),
) -> MilestoneResponse:
    return await service.complete_milestone(uuid.UUID(milestone_id), current_user.id)


@router.post("/disputes/{dispute_id}/resolve", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: str,
    request: ResolveDisputeRequest,
    admin: User = Depends(get_current_admin),
    service: EscrowService = Depends(get_escrow_service),
) -> DisputeResponse:
    return await service.resolve_dispute(uuid.UUID(dispute_id), request, admin.id)
