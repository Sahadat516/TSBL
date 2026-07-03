from __future__ import annotations

from app.modules.reviews.domain.exceptions import (
    ReviewDomainError,
    ReviewNotFoundError,
    SelfReviewError,
    UnverifiedPurchaseError,
)


class TestReviewExceptions:
    def test_hierarchy(self):
        assert issubclass(ReviewNotFoundError, ReviewDomainError)
        assert issubclass(SelfReviewError, ReviewDomainError)

    def test_status_codes(self):
        assert ReviewNotFoundError.status_code == 404
        assert SelfReviewError.status_code == 400
        assert UnverifiedPurchaseError.status_code == 403

    def test_error_codes(self):
        assert ReviewNotFoundError.code == "review_not_found"
        assert SelfReviewError.code == "self_review"
        assert UnverifiedPurchaseError.code == "unverified_purchase"
