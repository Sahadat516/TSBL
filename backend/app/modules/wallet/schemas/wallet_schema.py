from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.wallet.domain.value_objects import TransactionDirection, TransactionType, WalletStatus


class WalletResponse(BaseModel):
    id: UUID
    user_id: UUID
    balance: Decimal
    currency: str
    status: WalletStatus
    frozen_amount: Decimal = Decimal("0.00")
    total_deposited: Decimal = Decimal("0.00")
    total_withdrawn: Decimal = Decimal("0.00")
    last_transaction_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    transaction_type: TransactionType
    direction: TransactionDirection
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    currency: str
    reference_type: str | None = None
    reference_id: UUID | None = None
    description: str | None = None
    gateway: str | None = None
    gateway_transaction_id: str | None = None
    metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DepositRequest(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("999999.99"))
    gateway: str = Field(min_length=1, max_length=50)
    gateway_transaction_id: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    metadata: dict | None = None


class WithdrawalRequest(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("999999.99"))
    description: str | None = Field(default=None, max_length=500)
    metadata: dict | None = None


class WalletAdjustmentRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    direction: TransactionDirection
    description: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=1, max_length=500)
    reference_type: str | None = Field(default=None, max_length=50)
    reference_id: UUID | None = None
