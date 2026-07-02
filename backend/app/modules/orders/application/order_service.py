from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import OrderStatus
from app.core.logging import AuditLogger
from app.modules.marketplace.domain.entities import Product
from app.modules.orders.domain.entities import Order, OrderItem
from app.modules.orders.infrastructure.order_repository import OrderRepository
from app.modules.orders.schemas.order_schema import (
    CancelOrderRequest,
    OrderCreateRequest,
    OrderListResponse,
    OrderResponse,
    OrderTimelineResponse,
    StatusHistoryResponse,
)


class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.order_repo = OrderRepository(db)

    async def create_order(self, request: OrderCreateRequest, buyer_id: uuid.UUID) -> OrderResponse:
        if not request.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Order must have at least one item"
            )

        product_ids = [item.product_id for item in request.items]
        result = await self.db.execute(
            select(Product).where(
                Product.id.in_(product_ids),
                Product.is_active.is_(True),
                Product.deleted_at.is_(None),
            )
        )
        products = {p.id: p for p in result.scalars().all()}

        if len(products) != len(product_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more products not found or inactive",
            )

        seller_ids = {p.seller_id for p in products.values()}
        if len(seller_ids) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All items must be from the same seller",
            )

        seller_id = seller_ids.pop()
        order_number = await self.order_repo.get_next_order_number()

        subtotal = sum(
            products[item.product_id].base_price * item.quantity
            for item in request.items
        )

        order = Order(
            id=uuid.uuid4(),
            order_number=order_number,
            buyer_id=buyer_id,
            seller_id=seller_id,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            total_amount=subtotal,
            buyer_note=request.buyer_note,
            metadata=request.metadata,
        )
        await self.order_repo.create(order)

        for item in request.items:
            product = products[item.product_id]
            order_item = OrderItem(
                id=uuid.uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                seller_id=product.seller_id,
                product_name=product.title,
                quantity=item.quantity,
                unit_price=product.base_price,
                total_price=product.base_price * item.quantity,
                is_digital=product.is_digital,
            )
            self.db.add(order_item)

        await self.order_repo.add_status_history(
            order_id=order.id,
            from_status=None,
            to_status=OrderStatus.PENDING.value,
            changed_by=buyer_id,
            is_automated=True,
        )

        await self.db.flush()

        AuditLogger.log(
            action="ORDER_CREATED",
            actor_id=str(buyer_id),
            resource="order",
            resource_id=str(order.id),
            details={"order_number": order_number, "total": str(subtotal)},
        )

        return await self._load_order_response(order.id)

    async def get_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> OrderResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your order"
            )
        return OrderResponse.model_validate(order)

    async def list_my_orders(
        self,
        user_id: uuid.UUID,
        role: str = "buyer",
        status: OrderStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> OrderListResponse:
        if role == "seller":
            orders, total = await self.order_repo.list_by_seller(
                seller_id=user_id, status=status, search=search,
                sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size,
            )
        else:
            orders, total = await self.order_repo.list_by_buyer(
                buyer_id=user_id, status=status, search=search,
                sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size,
            )

        total_pages = max(1, (total + page_size - 1) // page_size)
        return OrderListResponse(
            items=[OrderResponse.model_validate(o) for o in orders],
            total=total, page=page, page_size=page_size, total_pages=total_pages,
        )

    async def cancel_order(
        self, order_id: uuid.UUID, user_id: uuid.UUID, request: CancelOrderRequest
    ) -> OrderResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.buyer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the buyer can cancel")
        if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be cancelled in its current status",
            )

        old_status = order.status.value
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)
        order.cancelled_by = user_id
        order.cancellation_reason = request.reason

        await self.order_repo.add_status_history(
            order_id=order.id, from_status=old_status,
            to_status=OrderStatus.CANCELLED.value,
            changed_by=user_id, reason=request.reason,
        )
        await self.db.flush()

        AuditLogger.log(
            action="ORDER_CANCELLED", actor_id=str(user_id),
            resource="order", resource_id=str(order.id),
            details={"reason": request.reason},
        )
        return OrderResponse.model_validate(order)

    async def confirm_delivery(self, order_id: uuid.UUID, user_id: uuid.UUID) -> OrderResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.buyer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the buyer can confirm delivery")
        if order.status != OrderStatus.DELIVERED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not in delivered status")

        old_status = order.status.value
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now(timezone.utc)

        await self.order_repo.add_status_history(
            order_id=order.id, from_status=old_status,
            to_status=OrderStatus.COMPLETED.value,
            changed_by=user_id, reason="Buyer confirmed delivery",
        )
        await self.db.flush()

        AuditLogger.log(
            action="ORDER_COMPLETED", actor_id=str(user_id),
            resource="order", resource_id=str(order.id),
        )
        return OrderResponse.model_validate(order)

    async def get_timeline(self, order_id: uuid.UUID, user_id: uuid.UUID) -> OrderTimelineResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
        return OrderTimelineResponse(
            current_status=order.status,
            timeline=[StatusHistoryResponse.model_validate(h) for h in order.status_history],
        )

    async def _load_order_response(self, order_id: uuid.UUID) -> OrderResponse:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderResponse.model_validate(order)
