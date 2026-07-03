from __future__ import annotations

from app.exceptions.base import AppException


class NotificationDomainError(AppException):
    code: str = "notification_domain_error"
    detail: str = "Notification domain error"


class NotificationNotFoundError(NotificationDomainError):
    status_code: int = 404
    code: str = "notification_not_found"
    detail: str = "Notification not found"


class NotificationPreferenceNotFoundError(NotificationDomainError):
    status_code: int = 404
    code: str = "notification_preference_not_found"
    detail: str = "Notification preference not found"
