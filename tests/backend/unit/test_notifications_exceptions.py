from __future__ import annotations

from app.modules.notifications.domain.exceptions import (
    NotificationDomainError,
    NotificationNotFoundError,
    NotificationPreferenceNotFoundError,
)


class TestNotificationExceptions:
    def test_hierarchy(self):
        assert issubclass(NotificationNotFoundError, NotificationDomainError)

    def test_status_codes(self):
        assert NotificationNotFoundError.status_code == 404
        assert NotificationPreferenceNotFoundError.status_code == 404

    def test_error_codes(self):
        assert NotificationNotFoundError.code == "notification_not_found"
        assert NotificationPreferenceNotFoundError.code == "notification_preference_not_found"
