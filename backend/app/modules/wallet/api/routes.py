from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.modules.auth.domain.entities import User
from app.modules.wallet.application.wallet_service import WalletService
from app.modules.wallet.schemas.wallet_schema import (
    DepositRequest,
    TransactionListResponse,
    TransactionResponse,
    WalletAdjustmentRequest,
    WalletResponse,
    WithdrawalRequest,
)

router = APIRouter(prefix="/wallet", tags=["Wallet"])


def get_wallet_service(db: AsyncSession = Depends(get_db)) -> WalletService:
    return WalletService(db)


@router.get("", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
) -> WalletResponse:
    return await service.get_wallet(current_user.id)


@router.post("/deposit", response_model=TransactionResponse, status_code=201)
async def deposit(
    request: DepositRequest,
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
) -> TransactionResponse:
    return await service.deposit(request, current_user.id)


@router.post("/withdraw", response_model=TransactionResponse, status_code=201)
async def withdraw(
    request: WithdrawalRequest,
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
) -> TransactionResponse:
    return await service.withdraw(request, current_user.id)


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
) -> TransactionListResponse:
    return await service.list_transactions(current_user.id, page=page, page_size=page_size)


@router.post("/adjust", response_model=TransactionResponse)
async def adjust_balance(
    request: WalletAdjustmentRequest,
    admin: User = Depends(get_current_admin),
    service: WalletService = Depends(get_wallet_service),
) -> TransactionResponse:
    return await service.adjust_balance(request, admin.id)
