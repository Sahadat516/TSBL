from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.notifications.application.notification_service import NotificationService
from app.modules.notifications.schemas.notification_schema import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationResponse,
    UpdateNotificationPreferenceRequest,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    return await service.list_notifications(current_user.id, page=page, page_size=page_size)


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    return await service.get_unread_count(current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    return await service.mark_as_read(uuid.UUID(notification_id), current_user.id)


@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    return await service.mark_all_as_read(current_user.id)


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationPreferenceResponse:
    return await service.get_preferences(current_user.id)


@router.patch("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    request: UpdateNotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationPreferenceResponse:
    return await service.update_preferences(request, current_user.id)
