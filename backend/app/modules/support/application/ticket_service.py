from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.support.domain.entities import Ticket, TicketMessage
from app.modules.support.domain.value_objects import TicketStatus
from app.modules.support.infrastructure.ticket_repository import TicketMessageRepository, TicketRepository
from app.modules.support.schemas.ticket_schema import (
    AddTicketMessageRequest,
    CreateTicketRequest,
    TicketListResponse,
    TicketMessageResponse,
    TicketResponse,
    UpdateTicketRequest,
)


class TicketService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.msg_repo = TicketMessageRepository(db)

    async def create_ticket(self, request: CreateTicketRequest, user_id: uuid.UUID) -> TicketResponse:
        ticket_number = await self.ticket_repo.get_next_ticket_number()
        ticket = Ticket(
            id=uuid.uuid4(),
            ticket_number=ticket_number,
            user_id=user_id,
            subject=request.subject,
            description=request.description,
            category=request.category,
            priority=request.priority,
            order_id=request.order_id,
            metadata=request.metadata,
        )
        await self.ticket_repo.create(ticket)

        if request.description:
            msg = TicketMessage(
                id=uuid.uuid4(),
                ticket_id=ticket.id,
                user_id=user_id,
                content=request.description,
                is_system_message=True,
            )
            self.db.add(msg)

        await self.db.flush()

        AuditLogger.log(
            action="TICKET_CREATED",
            actor_id=str(user_id),
            resource="ticket",
            resource_id=str(ticket.id),
            details={"category": request.category.value, "priority": request.priority.value},
        )

        return await self._load_ticket_response(ticket.id)

    async def get_ticket(self, ticket_id: uuid.UUID, user_id: uuid.UUID) -> TicketResponse:
        ticket = await self.ticket_repo.get_with_messages(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        if ticket.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your ticket")
        return await self._load_ticket_response(ticket.id)

    async def list_my_tickets(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> TicketListResponse:
        items, total = await self.ticket_repo.list_by_user(user_id, page, page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return TicketListResponse(
            items=[TicketResponse.model_validate(t) for t in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def add_message(
        self, ticket_id: uuid.UUID, request: AddTicketMessageRequest, user_id: uuid.UUID
    ) -> TicketMessageResponse:
        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        if ticket.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your ticket")
        if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket is closed")

        msg = TicketMessage(
            id=uuid.uuid4(),
            ticket_id=ticket_id,
            user_id=user_id,
            content=request.content,
            is_internal=request.is_internal,
            attachments=request.attachments,
        )
        await self.msg_repo.create(msg)

        ticket.status = TicketStatus.IN_PROGRESS
        ticket.version += 1
        await self.db.flush()

        return TicketMessageResponse.model_validate(msg)

    async def update_ticket(
        self, ticket_id: uuid.UUID, request: UpdateTicketRequest, user_id: uuid.UUID
    ) -> TicketResponse:
        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        if ticket.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your ticket")

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)

        if request.status == TicketStatus.RESOLVED:
            ticket.is_resolved = True
            ticket.resolved_at = datetime.now(timezone.utc)
        elif request.status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.now(timezone.utc)
            ticket.closed_by = user_id

        ticket.version += 1
        await self.db.flush()

        return await self._load_ticket_response(ticket.id)

    async def _load_ticket_response(self, ticket_id: uuid.UUID) -> TicketResponse:
        ticket = await self.ticket_repo.get_with_messages(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        return TicketResponse.model_validate(ticket)
