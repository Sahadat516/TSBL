from __future__ import annotations

from app.modules.affiliate.domain.value_objects import CommissionLevel, CommissionStatus, ReferralStatus


class TestCommissionLevel:
    def test_values(self):
        assert CommissionLevel.LEVEL_1 == 1
        assert CommissionLevel.LEVEL_2 == 2
        assert CommissionLevel.LEVEL_3 == 3


class TestCommissionStatus:
    def test_values(self):
        assert CommissionStatus.PENDING == "pending"
        assert CommissionStatus.PAID == "paid"
        assert CommissionStatus.CANCELLED == "cancelled"


class TestReferralStatus:
    def test_values(self):
        assert ReferralStatus.CLICKED == "clicked"
        assert ReferralStatus.SIGNED_UP == "signed_up"
        assert ReferralStatus.CONVERTED == "converted"
