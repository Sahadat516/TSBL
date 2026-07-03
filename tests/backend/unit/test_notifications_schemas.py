from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.notifications.domain.value_objects import (
    ChannelType,
    DigestFrequency,
    NotificationPriority,
)
from app.modules.notifications.schemas.notification_schema import (
    NotificationPreferenceResponse,
    NotificationResponse,
    UpdatePreferenceRequest,
)


class TestUpdatePreferenceRequest:
    def test_valid(self):
        req = UpdatePreferenceRequest(
            channel=ChannelType.EMAIL,
            digest_frequency=DigestFrequency.DAILY,
            enabled=True,
            quiet_hours_start="22:00",
            quiet_hours_end="08:00",
        )
        assert req.channel == ChannelType.EMAIL
        assert req.digest_frequency == DigestFrequency.DAILY

    def test_enabled_default(self):
        req = UpdatePreferenceRequest(
            channel=ChannelType.IN_APP,
            digest_frequency=DigestFrequency.INSTANT,
        )
        assert req.enabled is True

    def test_invalid_quiet_hours_format(self):
        with pytest.raises(ValidationError):
            UpdatePreferenceRequest(
                channel=ChannelType.EMAIL,
                digest_frequency=DigestFrequency.DAILY,
                quiet_hours_start="25:00",
                quiet_hours_end="08:00",
            )


class TestNotificationResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = NotificationResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            title="Order Shipped",
            message="Your order #123 has shipped",
            channel=ChannelType.IN_APP,
            priority=NotificationPriority.HIGH,
            is_read=False,
            created_at=now,
        )
        assert resp.title == "Order Shipped"
        assert resp.is_read is False
        assert resp.priority == NotificationPriority.HIGH

    def test_from_attributes(self):
        assert NotificationResponse.model_config.get("from_attributes") is True


class TestNotificationPreferenceResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = NotificationPreferenceResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            channel=ChannelType.EMAIL,
            digest_frequency=DigestFrequency.WEEKLY,
            enabled=True,
            created_at=now,
        )
        assert resp.channel == ChannelType.EMAIL
        assert resp.enabled is True

    def test_from_attributes(self):
        assert NotificationPreferenceResponse.model_config.get("from_attributes") is True
