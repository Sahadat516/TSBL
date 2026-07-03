from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.support.domain.value_objects import TicketCategory, TicketPriority, TicketStatus


class CreateTicketRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    order_id: UUID | None = None
    metadata: dict | None = None


class AddTicketMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    is_internal: bool = False
    attachments: dict | None = None


class TicketMessageResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    user_id: UUID
    content: str
    is_internal: bool
    is_system_message: bool
    attachments: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketResponse(BaseModel):
    id: UUID
    ticket_number: str
    user_id: UUID
    assigned_to: UUID | None = None
    subject: str
    description: str | None = None
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    order_id: UUID | None = None
    is_resolved: bool
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    messages: list[TicketMessageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UpdateTicketRequest(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to: UUID | None = None
