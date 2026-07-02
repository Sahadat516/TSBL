from __future__ import annotations

from app.modules.user.domain.exceptions import (
    BuyerProfileNotFoundError,
    ProfileAccessDeniedError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    SellerProfileNotFoundError,
    StoreSlugAlreadyTakenError,
    UserDomainError,
    UserNotFoundError,
)


class TestUserDomainExceptions:
    def test_user_domain_error(self):
        exc = UserDomainError()
        assert exc.code == "user_domain_error"
        assert exc.status_code == 500

    def test_user_not_found(self):
        exc = UserNotFoundError()
        assert exc.code == "user_not_found"
        assert exc.status_code == 404

    def test_profile_not_found(self):
        exc = ProfileNotFoundError()
        assert exc.code == "profile_not_found"
        assert exc.status_code == 404

    def test_seller_profile_not_found(self):
        exc = SellerProfileNotFoundError()
        assert exc.code == "seller_profile_not_found"
        assert exc.status_code == 404

    def test_buyer_profile_not_found(self):
        exc = BuyerProfileNotFoundError()
        assert exc.code == "buyer_profile_not_found"
        assert exc.status_code == 404

    def test_profile_already_exists(self):
        exc = ProfileAlreadyExistsError()
        assert exc.code == "profile_already_exists"
        assert exc.status_code == 409

    def test_store_slug_already_taken(self):
        exc = StoreSlugAlreadyTakenError()
        assert exc.code == "store_slug_already_taken"
        assert exc.status_code == 409

    def test_profile_access_denied(self):
        exc = ProfileAccessDeniedError()
        assert exc.code == "profile_access_denied"
        assert exc.status_code == 403

    def test_custom_detail(self):
        exc = UserNotFoundError(detail="Custom message")
        assert exc.detail == "Custom message"
