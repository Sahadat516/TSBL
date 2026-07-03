from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.notifications.domain.entities import Notification
from app.modules.notifications.infrastructure.notification_repository import (
    NotificationPreferenceRepository,
    NotificationRepository,
)
from app.modules.notifications.schemas.notification_schema import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationResponse,
    SendNotificationRequest,
    UpdateNotificationPreferenceRequest,
)


class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.notif_repo = NotificationRepository(db)
        self.pref_repo = NotificationPreferenceRepository(db)

    async def list_notifications(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> NotificationListResponse:
        items, total = await self.notif_repo.list_by_user(user_id, page, page_size)
        unread_count = await self.notif_repo.get_unread_count(user_id)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            unread_count=unread_count,
        )

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> NotificationResponse:
        notif = await self.notif_repo.get(notification_id)
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        if notif.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your notification")
        await self.notif_repo.mark_as_read(notification_id)
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        return NotificationResponse.model_validate(notif)

    async def mark_all_as_read(self, user_id: uuid.UUID) -> dict:
        await self.notif_repo.mark_all_as_read(user_id)
        return {"message": "All notifications marked as read"}

    async def get_unread_count(self, user_id: uuid.UUID) -> dict:
        count = await self.notif_repo.get_unread_count(user_id)
        return {"unread_count": count}

    async def get_preferences(self, user_id: uuid.UUID) -> NotificationPreferenceResponse:
        prefs = await self.pref_repo.get_or_create(user_id)
        return NotificationPreferenceResponse.model_validate(prefs)

    async def update_preferences(
        self, request: UpdateNotificationPreferenceRequest, user_id: uuid.UUID
    ) -> NotificationPreferenceResponse:
        prefs = await self.pref_repo.get_or_create(user_id)
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(prefs, field):
                setattr(prefs, field, value)
        prefs.version += 1
        await self.db.flush()
        return NotificationPreferenceResponse.model_validate(prefs)

    async def send_notification(
        self, request: SendNotificationRequest, sender_id: uuid.UUID
    ) -> NotificationResponse:
        notif = Notification(
            id=uuid.uuid4(),
            user_id=request.user_id,
            notification_type=request.notification_type,
            title=request.title,
            body=request.body,
            channel=request.channel,
            priority=request.priority,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            action_url=request.action_url,
            image_url=request.image_url,
            metadata=request.metadata,
        )
        await self.notif_repo.create(notif)

        AuditLogger.log(
            action="NOTIFICATION_SENT",
            actor_id=str(sender_id),
            resource="notification",
            resource_id=str(notif.id),
            details={"type": request.notification_type.value, "to": str(request.user_id)},
        )

        return NotificationResponse.model_validate(notif)
