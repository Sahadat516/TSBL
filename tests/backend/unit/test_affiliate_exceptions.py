from __future__ import annotations

from app.modules.affiliate.domain.exceptions import (
    AffiliateDomainError,
    AffiliateProfileNotFoundError,
    DuplicateReferralCodeError,
    SelfReferralError,
)


class TestAffiliateExceptions:
    def test_hierarchy(self):
        assert issubclass(AffiliateProfileNotFoundError, AffiliateDomainError)

    def test_status_codes(self):
        assert AffiliateProfileNotFoundError.status_code == 404
        assert DuplicateReferralCodeError.status_code == 409
        assert SelfReferralError.status_code == 400

    def test_error_codes(self):
        assert AffiliateProfileNotFoundError.code == "affiliate_profile_not_found"
        assert DuplicateReferralCodeError.code == "duplicate_referral_code"
        assert SelfReferralError.code == "self_referral"
