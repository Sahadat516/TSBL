from __future__ import annotations

from app.exceptions.base import AppException


class WalletDomainError(AppException):
    code: str = "wallet_domain_error"
    detail: str = "Wallet domain error"


class WalletNotFoundError(WalletDomainError):
    status_code: int = 404
    code: str = "wallet_not_found"
    detail: str = "Wallet not found"


class WalletAlreadyExistsError(WalletDomainError):
    status_code: int = 409
    code: str = "wallet_already_exists"
    detail: str = "Wallet already exists for this user"


class WalletFrozenError(WalletDomainError):
    status_code: int = 400
    code: str = "wallet_frozen"
    detail: str = "Wallet is frozen"


class InsufficientWalletBalanceError(WalletDomainError):
    status_code: int = 400
    code: str = "insufficient_wallet_balance"
    detail: str = "Insufficient wallet balance"


class TransactionNotFoundError(WalletDomainError):
    status_code: int = 404
    code: str = "transaction_not_found"
    detail: str = "Transaction not found"
