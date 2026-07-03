from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.admin.application.admin_service import AdminService
from app.modules.admin.schemas.admin_schema import (
    AdminDashboardResponse,
    AdminUserActionRequest,
    AuditLogListResponse,
    SystemConfigResponse,
    UpdateSystemConfigRequest,
)
from app.modules.auth.domain.entities import User

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_dashboard(
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> AdminDashboardResponse:
    return await service.get_dashboard()


@router.post("/users/suspend")
async def suspend_user(
    request: AdminUserActionRequest,
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> dict:
    return await service.suspend_user(request, admin.id)


@router.post("/users/ban")
async def ban_user(
    request: AdminUserActionRequest,
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> dict:
    return await service.ban_user(request, admin.id)


@router.post("/products/{product_id}/approve")
async def approve_product(
    product_id: str,
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> dict:
    return await service.approve_product(uuid.UUID(product_id), admin.id)


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> AuditLogListResponse:
    return await service.get_audit_logs(page=page, page_size=page_size)


@router.get("/config/{key}", response_model=SystemConfigResponse)
async def get_config(
    key: str,
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> SystemConfigResponse:
    return await service.get_config(key)


@router.patch("/config/{key}", response_model=SystemConfigResponse)
async def update_config(
    key: str,
    request: UpdateSystemConfigRequest,
    admin: User = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service),
) -> SystemConfigResponse:
    return await service.update_config(key, request, admin.id)
