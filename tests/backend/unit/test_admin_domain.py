from __future__ import annotations

from app.modules.admin.domain.value_objects import ActionType, EntityType, SystemConfigKey


class TestActionType:
    def test_values(self):
        assert ActionType.CREATE == "create"
        assert ActionType.UPDATE == "update"
        assert ActionType.DELETE == "delete"
        assert ActionType.SUSPEND == "suspend"
        assert ActionType.BAN == "ban"
        assert ActionType.APPROVE == "approve"
        assert ActionType.REJECT == "reject"


class TestEntityType:
    def test_values(self):
        assert EntityType.USER == "user"
        assert EntityType.PRODUCT == "product"
        assert EntityType.ORDER == "order"


class TestSystemConfigKey:
    def test_values(self):
        assert SystemConfigKey.PLATFORM_NAME == "platform_name"
        assert SystemConfigKey.COMMISSION_RATE == "commission_rate"
        assert SystemConfigKey.MAINTENANCE_MODE == "maintenance_mode"
        assert SystemConfigKey.MIN_WITHDRAWAL_AMOUNT == "min_withdrawal_amount"
        assert SystemConfigKey.MAX_PRODUCT_TITLE_LENGTH == "max_product_title_length"
