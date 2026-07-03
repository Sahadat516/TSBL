from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger
from app.modules.auth.domain.entities import User
from app.modules.orders.domain.entities import Order
from app.modules.payments.domain.entities import Payment, PaymentMethod, Payout, Refund, TransactionLog
from app.modules.payments.domain.value_objects import (
    PaymentGateway,
    PayoutStatus,
    RefundReason,
    TransactionStatus,
)
from app.modules.payments.infrastructure.payment_repository import (
    PaymentMethodRepository,
    PaymentRepository,
    PayoutRepository,
    RefundRepository,
    TransactionLogRepository,
)
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


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.method_repo = PaymentMethodRepository(db)
        self.payout_repo = PayoutRepository(db)
        self.refund_repo = RefundRepository(db)
        self.log_repo = TransactionLogRepository(db)

    async def create_payment(self, request: CreatePaymentRequest, buyer_id: uuid.UUID) -> PaymentResponse:
        result = await self.db.execute(
            select(Order).where(Order.id == request.order_id, Order.deleted_at.is_(None))
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.buyer_id != buyer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")

        existing = await self.payment_repo.get_by_order_id(request.order_id)
        if existing and existing.status in (TransactionStatus.PENDING, TransactionStatus.PROCESSING):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment already exists and is being processed",
            )

        gateway_fee = Decimal("0.00")
        if request.gateway == PaymentGateway.STRIPE:
            gateway_fee = (order.total_amount * Decimal("0.029") + Decimal("0.30")).quantize(Decimal("0.01"))
        elif request.gateway == PaymentGateway.PAYPAL:
            gateway_fee = (order.total_amount * Decimal("0.049") + Decimal("0.49")).quantize(Decimal("0.01"))

        net_amount = order.total_amount - gateway_fee

        payment = Payment(
            id=uuid.uuid4(),
            order_id=request.order_id,
            buyer_id=buyer_id,
            seller_id=order.seller_id,
            amount=order.total_amount,
            currency=order.currency,
            gateway=request.gateway,
            status=TransactionStatus.PENDING,
            gateway_fee=gateway_fee,
            net_amount=net_amount,
            metadata=request.metadata,
        )
        await self.payment_repo.create(payment)

        AuditLogger.log(
            action="PAYMENT_CREATED",
            actor_id=str(buyer_id),
            resource="payment",
            resource_id=str(payment.id),
            details={"order_id": str(request.order_id), "amount": str(order.total_amount)},
        )

        return await self._load_payment_response(payment.id)

    async def process_payment(
        self, request: ProcessPaymentRequest, user_id: uuid.UUID
    ) -> PaymentResponse:
        payment = await self.payment_repo.get_with_details(request.payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        if payment.buyer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your payment")
        if payment.status != TransactionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not in pending status",
            )

        payment.gateway_payment_id = request.gateway_payment_id
        payment.gateway_transaction_id = request.gateway_transaction_id
        payment.gateway_response = request.gateway_response
        payment.status = TransactionStatus.SUCCESS
        payment.paid_at = datetime.now(timezone.utc)
        payment.version += 1

        await self.db.flush()

        AuditLogger.log(
            action="PAYMENT_PROCESSED",
            actor_id=str(user_id),
            resource="payment",
            resource_id=str(payment.id),
            details={"gateway_transaction_id": request.gateway_transaction_id},
        )

        return await self._load_payment_response(payment.id)

    async def get_payment(self, payment_id: uuid.UUID, user_id: uuid.UUID) -> PaymentResponse:
        payment = await self.payment_repo.get_with_details(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        if payment.buyer_id != user_id and payment.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your payment")
        return await self._load_payment_response(payment.id)

    async def list_my_payments(
        self, user_id: uuid.UUID, role: str = "buyer", page: int = 1, page_size: int = 20
    ) -> PaymentListResponse:
        if role == "seller":
            items, total = await self.payment_repo.list_by_seller(user_id, page, page_size)
        else:
            items, total = await self.payment_repo.list_by_buyer(user_id, page, page_size)

        total_pages = max(1, (total + page_size - 1) // page_size)
        return PaymentListResponse(
            items=[PaymentResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def refund_payment(self, request: RefundRequest, user_id: uuid.UUID) -> RefundResponse:
        payment = await self.payment_repo.get_with_details(request.payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        if payment.buyer_id != user_id and payment.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your payment")
        if payment.status != TransactionStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Payment is not in success status"
            )

        total_refunded = sum(r.amount for r in payment.refunds if r.status == TransactionStatus.SUCCESS)
        remaining = payment.amount - total_refunded
        if request.amount > remaining:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund amount exceeds remaining balance. Available: {remaining}",
            )

        refund = Refund(
            id=uuid.uuid4(),
            payment_id=request.payment_id,
            order_id=payment.order_id,
            amount=request.amount,
            currency=payment.currency,
            reason=request.reason,
            reason_detail=request.reason_detail,
            status=TransactionStatus.SUCCESS if request.reason != RefundReason.FRAUD_SUSPECTED else TransactionStatus.PENDING,
            processed_by=user_id,
            processed_at=datetime.now(timezone.utc),
        )
        await self.refund_repo.create(refund)

        new_total_refunded = total_refunded + request.amount
        if new_total_refunded >= payment.amount:
            payment.status = TransactionStatus.REFUNDED
        else:
            payment.status = TransactionStatus.PARTIALLY_REFUNDED
        payment.version += 1
        await self.db.flush()

        AuditLogger.log(
            action="REFUND_PROCESSED",
            actor_id=str(user_id),
            resource="refund",
            resource_id=str(refund.id),
            details={
                "payment_id": str(request.payment_id),
                "amount": str(request.amount),
                "reason": request.reason.value,
            },
        )

        return RefundResponse.model_validate(refund)

    async def list_payment_methods(self, user_id: uuid.UUID) -> list[PaymentMethodResponse]:
        methods = await self.method_repo.list_by_user(user_id)
        return [PaymentMethodResponse.model_validate(m) for m in methods]

    async def save_payment_method(
        self, request: SavePaymentMethodRequest, user_id: uuid.UUID
    ) -> PaymentMethodResponse:
        if request.is_default:
            await self.method_repo.unset_default(user_id)

        method = PaymentMethod(
            id=uuid.uuid4(),
            user_id=user_id,
            gateway=request.gateway,
            method_type=request.method_type,
            last_four=request.last_four,
            expiry_month=request.expiry_month,
            expiry_year=request.expiry_year,
            cardholder_name=request.cardholder_name,
            billing_address=request.billing_address,
            gateway_method_id=request.gateway_method_id,
            is_default=request.is_default,
            metadata=request.metadata,
        )
        await self.method_repo.create(method)
        return PaymentMethodResponse.model_validate(method)

    async def delete_payment_method(self, method_id: uuid.UUID, user_id: uuid.UUID) -> None:
        method = await self.method_repo.get(method_id)
        if not method:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
        if method.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your payment method")
        await self.method_repo.soft_delete(method_id)

    async def request_payout(self, request: PayoutRequest, seller_id: uuid.UUID) -> PayoutResponse:
        net_amount = request.amount
        fee_amount = Decimal("0.00")

        total_earnings = await self._calculate_seller_earnings(seller_id)
        total_pending_payouts = await self._calculate_pending_payouts(seller_id)
        available = total_earnings - total_pending_payouts

        if request.amount > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient available balance. Available: {available}",
            )

        payout = Payout(
            id=uuid.uuid4(),
            seller_id=seller_id,
            amount=request.amount,
            currency="USD",
            status=PayoutStatus.PENDING,
            payment_method=request.payment_method,
            payment_details=request.payment_details,
            fee_amount=fee_amount,
            net_amount=net_amount,
            note=request.note,
        )
        await self.payout_repo.create(payout)

        AuditLogger.log(
            action="PAYOUT_REQUESTED",
            actor_id=str(seller_id),
            resource="payout",
            resource_id=str(payout.id),
            details={"amount": str(request.amount), "payment_method": request.payment_method},
        )

        return PayoutResponse.model_validate(payout)

    async def list_my_payouts(
        self, seller_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> PayoutListResponse:
        items, total = await self.payout_repo.list_by_seller(seller_id, page, page_size)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return PayoutListResponse(
            items=[PayoutResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def _load_payment_response(self, payment_id: uuid.UUID) -> PaymentResponse:
        payment = await self.payment_repo.get_with_details(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return PaymentResponse.model_validate(payment)

    async def _calculate_seller_earnings(self, seller_id: uuid.UUID) -> Decimal:
        result = await self.db.execute(
            select(Payment).where(
                Payment.seller_id == seller_id,
                Payment.status.in_([TransactionStatus.SUCCESS]),
                Payment.deleted_at.is_(None),
            )
        )
        payments = result.scalars().all()
        return sum(p.net_amount for p in payments)

    async def _calculate_pending_payouts(self, seller_id: uuid.UUID) -> Decimal:
        result = await self.db.execute(
            select(Payout).where(
                Payout.seller_id == seller_id,
                Payout.status.in_([PayoutStatus.PENDING, PayoutStatus.PROCESSING]),
                Payout.deleted_at.is_(None),
            )
        )
        payouts = result.scalars().all()
        return sum(p.amount for p in payouts)
