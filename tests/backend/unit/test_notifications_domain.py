from __future__ import annotations

import pytest

from app.modules.notifications.domain.value_objects import (
    ChannelType,
    DigestFrequency,
    NotificationPriority,
)


class TestChannelType:
    def test_values(self):
        assert ChannelType.IN_APP == "in_app"
        assert ChannelType.EMAIL == "email"
        assert ChannelType.SMS == "sms"
        assert ChannelType.PUSH == "push"


class TestNotificationPriority:
    def test_values(self):
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.MEDIUM == "medium"
        assert NotificationPriority.HIGH == "high"
        assert NotificationPriority.URGENT == "urgent"


class TestDigestFrequency:
    def test_values(self):
        assert DigestFrequency.INSTANT == "instant"
        assert DigestFrequency.DAILY == "daily"
        assert DigestFrequency.WEEKLY == "weekly"
        assert DigestFrequency.NEVER == "never"
