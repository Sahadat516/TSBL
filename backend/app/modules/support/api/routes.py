from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.support.application.ticket_service import TicketService
from app.modules.support.schemas.ticket_schema import (
    AddTicketMessageRequest,
    CreateTicketRequest,
    TicketListResponse,
    TicketMessageResponse,
    TicketResponse,
    UpdateTicketRequest,
)

router = APIRouter(prefix="/support", tags=["Support"])


def get_ticket_service(db: AsyncSession = Depends(get_db)) -> TicketService:
    return TicketService(db)


@router.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    request: CreateTicketRequest,
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    return await service.create_ticket(request, current_user.id)


@router.get("/tickets", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> TicketListResponse:
    return await service.list_my_tickets(current_user.id, page=page, page_size=page_size)


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    return await service.get_ticket(uuid.UUID(ticket_id), current_user.id)


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageResponse, status_code=201)
async def add_message(
    ticket_id: str,
    request: AddTicketMessageRequest,
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> TicketMessageResponse:
    return await service.add_message(uuid.UUID(ticket_id), request, current_user.id)


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    request: UpdateTicketRequest,
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    return await service.update_ticket(uuid.UUID(ticket_id), request, current_user.id)
