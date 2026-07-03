from __future__ import annotations

from app.exceptions.base import AppException


class AffiliateDomainError(AppException):
    code: str = "affiliate_domain_error"
    detail: str = "Affiliate domain error"


class AffiliateNotFoundError(AffiliateDomainError):
    status_code: int = 404
    code: str = "affiliate_not_found"
    detail: str = "Affiliate profile not found"


class ReferralNotFoundError(AffiliateDomainError):
    status_code: int = 404
    code: str = "referral_not_found"
    detail: str = "Referral not found"


class CommissionNotFoundError(AffiliateDomainError):
    status_code: int = 404
    code: str = "commission_not_found"
    detail: str = "Commission not found"


class InvalidReferralCodeError(AffiliateDomainError):
    status_code: int = 400
    code: str = "invalid_referral_code"
    detail: str = "Invalid referral code"


class SelfReferralError(AffiliateDomainError):
    status_code: int = 400
    code: str = "self_referral_not_allowed"
    detail: str = "Cannot use your own referral code"
