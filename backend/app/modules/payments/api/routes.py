from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.payments.application.payment_service import PaymentService
from app.modules.payments.schemas.payment_schema import (
    CreatePaymentRequest,
    PaymentListResponse,
    PaymentMethodResponse,
    PaymentResponse,
    PayoutListResponse,
    PayoutRequest,
    PayoutResponse,
    ProcessPaymentRequest,
    RefundRequest,
    RefundResponse,
    SavePaymentMethodRequest,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


@router.post("", response_model=PaymentResponse, status_code=201)
async def create_payment(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    return await service.create_payment(request, current_user.id)


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    request: ProcessPaymentRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    return await service.process_payment(request, current_user.id)


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    role: str = Query("buyer", regex="^(buyer|seller)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListResponse:
    return await service.list_my_payments(
        user_id=current_user.id, role=role, page=page, page_size=page_size
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    return await service.get_payment(uuid.UUID(payment_id), current_user.id)


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(
    request: RefundRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> RefundResponse:
    return await service.refund_payment(request, current_user.id)


@router.get("/methods", response_model=list[PaymentMethodResponse])
async def list_payment_methods(
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> list[PaymentMethodResponse]:
    return await service.list_payment_methods(current_user.id)


@router.post("/methods", response_model=PaymentMethodResponse, status_code=201)
async def save_payment_method(
    request: SavePaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentMethodResponse:
    return await service.save_payment_method(request, current_user.id)


@router.delete("/methods/{method_id}", status_code=200)
async def delete_payment_method(
    method_id: str,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> dict:
    await service.delete_payment_method(uuid.UUID(method_id), current_user.id)
    return {"ok": True}


@router.post("/payouts", response_model=PayoutResponse, status_code=201)
async def request_payout(
    request: PayoutRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PayoutResponse:
    return await service.request_payout(request, current_user.id)


@router.get("/payouts", response_model=PayoutListResponse)
async def list_payouts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PayoutListResponse:
    return await service.list_my_payouts(current_user.id, page=page, page_size=page_size)
