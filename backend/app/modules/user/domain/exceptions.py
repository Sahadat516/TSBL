from __future__ import annotations

from app.exceptions.base import AppException


class UserDomainError(AppException):
    code: str = "user_domain_error"
    detail: str = "User domain error"


class UserNotFoundError(UserDomainError):
    status_code: int = 404
    code: str = "user_not_found"
    detail: str = "User not found"


class ProfileNotFoundError(UserDomainError):
    status_code: int = 404
    code: str = "profile_not_found"
    detail: str = "Profile not found"


class SellerProfileNotFoundError(UserDomainError):
    status_code: int = 404
    code: str = "seller_profile_not_found"
    detail: str = "Seller profile not found"


class BuyerProfileNotFoundError(UserDomainError):
    status_code: int = 404
    code: str = "buyer_profile_not_found"
    detail: str = "Buyer profile not found"


class ProfileAlreadyExistsError(UserDomainError):
    status_code: int = 409
    code: str = "profile_already_exists"
    detail: str = "Profile already exists"


class StoreSlugAlreadyTakenError(UserDomainError):
    status_code: int = 409
    code: str = "store_slug_already_taken"
    detail: str = "Store slug already taken"


class ProfileAccessDeniedError(UserDomainError):
    status_code: int = 403
    code: str = "profile_access_denied"
    detail: str = "Access to this profile is denied"
