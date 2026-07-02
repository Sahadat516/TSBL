from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import OrderStatus
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.orders.application.order_service import OrderService
from app.modules.orders.schemas.order_schema import (
    CancelOrderRequest,
    OrderCreateRequest,
    OrderListResponse,
    OrderResponse,
    OrderTimelineResponse,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    request: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await service.create_order(request, current_user.id)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    status: OrderStatus | None = Query(None),
    role: str = Query("buyer", regex="^(buyer|seller)$"),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    return await service.list_my_orders(
        user_id=current_user.id, role=role, status=status,
        search=search, sort_by=sort_by, sort_order=sort_order,
        page=page, page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await service.get_order(uuid.UUID(order_id), current_user.id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    request: CancelOrderRequest,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await service.cancel_order(uuid.UUID(order_id), current_user.id, request)


@router.post("/{order_id}/confirm-delivery", response_model=OrderResponse)
async def confirm_delivery(
    order_id: str,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await service.confirm_delivery(uuid.UUID(order_id), current_user.id)


@router.get("/{order_id}/timeline", response_model=OrderTimelineResponse)
async def get_order_timeline(
    order_id: str,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderTimelineResponse:
    return await service.get_timeline(uuid.UUID(order_id), current_user.id)
