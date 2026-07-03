from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.wallet.domain.entities import Transaction as WalletTxn
from app.modules.wallet.domain.entities import Wallet
from app.modules.wallet.domain.value_objects import (
    TransactionDirection,
    TransactionType,
    WalletStatus,
)
from app.modules.wallet.infrastructure.wallet_repository import TransactionRepository, WalletRepository
from app.modules.wallet.schemas.wallet_schema import (
    DepositRequest,
    TransactionListResponse,
    TransactionResponse,
    WalletAdjustmentRequest,
    WalletResponse,
    WithdrawalRequest,
)


class WalletService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.wallet_repo = WalletRepository(db)
        self.txn_repo = TransactionRepository(db)

    async def get_wallet(self, user_id: uuid.UUID) -> WalletResponse:
        wallet = await self.wallet_repo.get_or_create(user_id)
        return WalletResponse.model_validate(wallet)

    async def deposit(self, request: DepositRequest, user_id: uuid.UUID) -> TransactionResponse:
        wallet = await self.wallet_repo.get_or_create(user_id)
        self._ensure_wallet_active(wallet)

        balance_before = wallet.balance
        balance_after = balance_before + request.amount

        wallet.balance = balance_after
        wallet.total_deposited += request.amount
        wallet.last_transaction_at = datetime.now(timezone.utc)
        wallet.version += 1

        txn = WalletTxn(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type=TransactionType.DEPOSIT,
            direction=TransactionDirection.CREDIT,
            amount=request.amount,
            balance_before=balance_before,
            balance_after=balance_after,
            currency=wallet.currency,
            gateway=request.gateway,
            gateway_transaction_id=request.gateway_transaction_id,
            description=request.description,
            metadata=request.metadata,
        )
        await self.txn_repo.create(txn)
        await self.db.flush()

        AuditLogger.log(
            action="WALLET_DEPOSIT",
            actor_id=str(user_id),
            resource="wallet",
            resource_id=str(wallet.id),
            details={"amount": str(request.amount), "gateway": request.gateway},
        )

        return TransactionResponse.model_validate(txn)

    async def withdraw(self, request: WithdrawalRequest, user_id: uuid.UUID) -> TransactionResponse:
        wallet = await self.wallet_repo.get_or_create(user_id)
        self._ensure_wallet_active(wallet)

        available = wallet.balance - wallet.frozen_amount
        if request.amount > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient available balance. Available: {available}",
            )

        balance_before = wallet.balance
        balance_after = balance_before - request.amount

        wallet.balance = balance_after
        wallet.total_withdrawn += request.amount
        wallet.last_transaction_at = datetime.now(timezone.utc)
        wallet.version += 1

        txn = WalletTxn(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type=TransactionType.WITHDRAWAL,
            direction=TransactionDirection.DEBIT,
            amount=request.amount,
            balance_before=balance_before,
            balance_after=balance_after,
            currency=wallet.currency,
            description=request.description,
            metadata=request.metadata,
        )
        await self.txn_repo.create(txn)
        await self.db.flush()

        AuditLogger.log(
            action="WALLET_WITHDRAWAL",
            actor_id=str(user_id),
            resource="wallet",
            resource_id=str(wallet.id),
            details={"amount": str(request.amount)},
        )

        return TransactionResponse.model_validate(txn)

    async def list_transactions(
        self, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> TransactionListResponse:
        wallet = await self.wallet_repo.get_or_create(user_id)
        items, total = await self.txn_repo.list_by_wallet(wallet.id, page, page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return TransactionListResponse(
            items=[TransactionResponse.model_validate(t) for t in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def adjust_balance(
        self, request: WalletAdjustmentRequest, admin_id: uuid.UUID
    ) -> TransactionResponse:
        wallet = await self.wallet_repo.get_by_user_id(request.reference_id) if request.reference_id else None
        if not wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

        balance_before = wallet.balance
        if request.direction == TransactionDirection.CREDIT:
            balance_after = balance_before + request.amount
            txn_type = TransactionType.ADJUSTMENT
        else:
            if request.amount > wallet.balance:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance"
                )
            balance_after = balance_before - request.amount
            txn_type = TransactionType.ADJUSTMENT

        wallet.balance = balance_after
        wallet.last_transaction_at = datetime.now(timezone.utc)
        wallet.version += 1

        txn = WalletTxn(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            transaction_type=txn_type,
            direction=request.direction,
            amount=request.amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=request.description,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            metadata={"reason": request.reason},
        )
        await self.txn_repo.create(txn)
        await self.db.flush()

        AuditLogger.log(
            action="WALLET_ADJUSTMENT",
            actor_id=str(admin_id),
            resource="wallet",
            resource_id=str(wallet.id),
            details={
                "amount": str(request.amount),
                "direction": request.direction.value,
                "reason": request.reason,
            },
        )

        return TransactionResponse.model_validate(txn)

    def _ensure_wallet_active(self, wallet: Wallet) -> None:
        if wallet.status != WalletStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Wallet is {wallet.status.value}",
            )
