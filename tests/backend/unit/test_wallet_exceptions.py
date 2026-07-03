from __future__ import annotations

from app.modules.wallet.domain.exceptions import (
    InsufficientWalletBalanceError,
    TransactionNotFoundError,
    WalletAlreadyExistsError,
    WalletDomainError,
    WalletFrozenError,
    WalletNotFoundError,
)


class TestWalletExceptions:
    def test_hierarchy(self):
        assert issubclass(WalletNotFoundError, WalletDomainError)
        assert issubclass(InsufficientWalletBalanceError, WalletDomainError)

    def test_status_codes(self):
        assert WalletNotFoundError.status_code == 404
        assert WalletAlreadyExistsError.status_code == 409
        assert WalletFrozenError.status_code == 400
        assert InsufficientWalletBalanceError.status_code == 400

    def test_error_codes(self):
        assert WalletNotFoundError.code == "wallet_not_found"
        assert WalletFrozenError.code == "wallet_frozen"
        assert TransactionNotFoundError.code == "transaction_not_found"
