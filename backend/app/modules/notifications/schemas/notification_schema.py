from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.notifications.domain.value_objects import NotificationChannel, NotificationPriority, NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    notification_type: NotificationType
    title: str
    body: str | None = None
    channel: NotificationChannel
    priority: NotificationPriority
    is_read: bool
    read_at: datetime | None = None
    is_delivered: bool
    delivered_at: datetime | None = None
    reference_type: str | None = None
    reference_id: UUID | None = None
    action_url: str | None = None
    image_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    unread_count: int = 0


class NotificationPreferenceResponse(BaseModel):
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    marketing_emails: bool
    order_updates: bool
    payment_updates: bool
    message_notifications: bool
    review_notifications: bool
    promotional_notifications: bool
    digest_frequency: str
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None

    model_config = {"from_attributes": True}


class UpdateNotificationPreferenceRequest(BaseModel):
    email_notifications: bool | None = None
    sms_notifications: bool | None = None
    push_notifications: bool | None = None
    marketing_emails: bool | None = None
    order_updates: bool | None = None
    payment_updates: bool | None = None
    message_notifications: bool | None = None
    review_notifications: bool | None = None
    promotional_notifications: bool | None = None
    digest_frequency: str | None = Field(default=None, pattern="^(instant|daily|weekly|never)$")
    quiet_hours_start: str | None = Field(default=None, pattern="^([01]\\d|2[0-3]):[0-5]\\d$")
    quiet_hours_end: str | None = Field(default=None, pattern="^([01]\\d|2[0-3]):[0-5]\\d$")


class SendNotificationRequest(BaseModel):
    user_id: UUID
    notification_type: NotificationType
    title: str = Field(min_length=1, max_length=200)
    body: str | None = Field(default=None, max_length=5000)
    channel: NotificationChannel = NotificationChannel.IN_APP
    priority: NotificationPriority = NotificationPriority.MEDIUM
    reference_type: str | None = Field(default=None, max_length=50)
    reference_id: UUID | None = None
    action_url: str | None = Field(default=None, max_length=500)
    image_url: str | None = Field(default=None, max_length=500)
    metadata: dict | None = None
