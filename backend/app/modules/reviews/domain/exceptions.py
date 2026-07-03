from __future__ import annotations

from app.exceptions.base import AppException


class ReviewDomainError(AppException):
    code: str = "review_domain_error"
    detail: str = "Review domain error"


class ReviewNotFoundError(ReviewDomainError):
    status_code: int = 404
    code: str = "review_not_found"
    detail: str = "Review not found"


class ReviewAlreadyExistsError(ReviewDomainError):
    status_code: int = 409
    code: str = "review_already_exists"
    detail: str = "You have already reviewed this item"


class ReviewAccessDeniedError(ReviewDomainError):
    status_code: int = 403
    code: str = "review_access_denied"
    detail: str = "Access to this review is denied"


class ReviewNotVerifiedPurchaseError(ReviewDomainError):
    status_code: int = 400
    code: str = "review_not_verified_purchase"
    detail: str = "Only verified buyers can review this item"
