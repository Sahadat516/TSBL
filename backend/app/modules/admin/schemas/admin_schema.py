from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.admin.domain.value_objects import AuditAction, SystemConfigType


class AuditLogResponse(BaseModel):
    id: UUID
    admin_id: UUID
    action: AuditAction
    resource_type: str
    resource_id: str | None = None
    details: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SystemConfigResponse(BaseModel):
    id: UUID
    key: str
    value: dict
    config_type: SystemConfigType
    description: str | None = None
    is_public: bool
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateSystemConfigRequest(BaseModel):
    value: dict
    description: str | None = None
    is_public: bool | None = None


class AdminUserActionRequest(BaseModel):
    user_id: UUID
    reason: str = Field(min_length=1, max_length=500)


class AdminDashboardResponse(BaseModel):
    total_users: int = 0
    total_sellers: int = 0
    total_products: int = 0
    total_orders: int = 0
    pending_products: int = 0
    open_disputes: int = 0
    pending_payouts: int = 0
    open_tickets: int = 0
    total_revenue: str = "0.00"
    recent_actions: list[AuditLogResponse] = []
