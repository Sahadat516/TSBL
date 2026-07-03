from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.admin.domain.value_objects import ActionType, EntityType, SystemConfigKey
from app.modules.admin.schemas.admin_schema import (
    AdminActionRequest,
    AuditLogResponse,
    SystemConfigRequest,
    SystemConfigResponse,
    UserActionRequest,
    UserSuspendRequest,
)


class TestUserSuspendRequest:
    def test_valid(self):
        req = UserSuspendRequest(
            user_id=uuid.uuid4(),
            reason="Violation of terms",
            duration_days=7,
        )
        assert req.reason == "Violation of terms"
        assert req.duration_days == 7

    def test_empty_reason_raises(self):
        with pytest.raises(ValidationError):
            UserSuspendRequest(
                user_id=uuid.uuid4(),
                reason="",
                duration_days=7,
            )


class TestUserActionRequest:
    def test_valid_ban(self):
        req = UserActionRequest(
            user_id=uuid.uuid4(),
            action="ban",
            reason="Spam account",
        )
        assert req.action == "ban"

    def test_valid_suspend(self):
        req = UserActionRequest(
            user_id=uuid.uuid4(),
            action="suspend",
            reason="Violation",
        )
        assert req.action == "suspend"


class TestAdminActionRequest:
    def test_valid(self):
        req = AdminActionRequest(
            product_id=uuid.uuid4(),
            action="approve",
        )
        assert req.action == "approve"


class TestSystemConfigRequest:
    def test_valid(self):
        req = SystemConfigRequest(
            key=SystemConfigKey.PLATFORM_NAME,
            value="TSBL",
            description="Platform display name",
        )
        assert req.key == SystemConfigKey.PLATFORM_NAME
        assert req.value == "TSBL"

    def test_empty_value_raises(self):
        with pytest.raises(ValidationError):
            SystemConfigRequest(
                key=SystemConfigKey.MAINTENANCE_MODE,
                value="",
            )


class TestSystemConfigResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = SystemConfigResponse(
            id=uuid.uuid4(),
            key=SystemConfigKey.PLATFORM_NAME,
            value="TSBL",
            description="Platform display name",
            updated_by=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )
        assert resp.key == SystemConfigKey.PLATFORM_NAME
        assert resp.value == "TSBL"

    def test_from_attributes(self):
        assert SystemConfigResponse.model_config.get("from_attributes") is True


class TestAuditLogResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = AuditLogResponse(
            id=uuid.uuid4(),
            admin_id=uuid.uuid4(),
            action=ActionType.SUSPEND,
            entity_type=EntityType.USER,
            entity_id=str(uuid.uuid4()),
            details={"reason": "Spam"},
            created_at=now,
        )
        assert resp.action == ActionType.SUSPEND
        assert resp.entity_type == EntityType.USER

    def test_from_attributes(self):
        assert AuditLogResponse.model_config.get("from_attributes") is True
