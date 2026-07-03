from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.modules.affiliate.domain.value_objects import CommissionLevel, CommissionStatus, ReferralStatus
from app.modules.affiliate.schemas.affiliate_schema import (
    AffiliateProfileResponse,
    CommissionResponse,
    ReferralResponse,
)


class TestAffiliateProfileResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = AffiliateProfileResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            referral_code="ABC12345",
            commission_rate=Decimal("10.00"),
            commission_level=CommissionLevel.LEVEL_1,
            total_earned=Decimal("0.00"),
            total_referred=0,
            created_at=now,
            updated_at=now,
        )
        assert resp.referral_code == "ABC12345"
        assert resp.commission_level == CommissionLevel.LEVEL_1

    def test_from_attributes(self):
        assert AffiliateProfileResponse.model_config.get("from_attributes") is True


class TestReferralResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = ReferralResponse(
            id=uuid.uuid4(),
            affiliate_id=uuid.uuid4(),
            referred_user_id=uuid.uuid4(),
            status=ReferralStatus.CONVERTED,
            created_at=now,
        )
        assert resp.status == ReferralStatus.CONVERTED

    def test_from_attributes(self):
        assert ReferralResponse.model_config.get("from_attributes") is True


class TestCommissionResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = CommissionResponse(
            id=uuid.uuid4(),
            referral_id=uuid.uuid4(),
            amount=Decimal("5.00"),
            level=CommissionLevel.LEVEL_1,
            status=CommissionStatus.PAID,
            created_at=now,
        )
        assert resp.amount == Decimal("5.00")
        assert resp.status == CommissionStatus.PAID

    def test_from_attributes(self):
        assert CommissionResponse.model_config.get("from_attributes") is True
