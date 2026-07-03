from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import OrderStatus, PaymentStatus, UserStatus
from app.modules.analytics.domain.entities import SavedReport
from app.modules.analytics.domain.value_objects import ReportType
from app.modules.analytics.infrastructure.analytics_repository import SavedReportRepository
from app.modules.analytics.schemas.analytics_schema import (
    CreateReportRequest,
    DashboardStatsResponse,
    ProductAnalyticsResponse,
    RevenueAnalyticsResponse,
    RevenueChartData,
    SavedReportResponse,
    UserAnalyticsResponse,
)
from app.modules.auth.domain.entities import User
from app.modules.marketplace.domain.entities import Product
from app.modules.orders.domain.entities import Order
from app.modules.payments.domain.entities import Payment
from app.modules.payments.domain.value_objects import TransactionStatus


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.report_repo = SavedReportRepository(db)

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        user_count = await self.db.execute(select(func.count(User.id)).where(User.deleted_at.is_(None)))
        product_count = await self.db.execute(select(func.count(Product.id)).where(Product.deleted_at.is_(None)))
        order_count = await self.db.execute(select(func.count(Order.id)).where(Order.deleted_at.is_(None)))

        revenue = await self.db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == TransactionStatus.SUCCESS,
                Payment.deleted_at.is_(None),
            )
        )
        pending_orders = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED]),
                Order.deleted_at.is_(None),
            )
        )
        active_products = await self.db.execute(
            select(func.count(Product.id)).where(
                Product.is_active.is_(True),
                Product.deleted_at.is_(None),
            )
        )
        new_users_today = await self.db.execute(
            select(func.count(User.id)).where(
                User.created_at >= today_start,
                User.deleted_at.is_(None),
            )
        )
        revenue_today = await self.db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == TransactionStatus.SUCCESS,
                Payment.paid_at >= today_start,
                Payment.deleted_at.is_(None),
            )
        )

        return DashboardStatsResponse(
            total_users=user_count.scalar() or 0,
            total_products=product_count.scalar() or 0,
            total_orders=order_count.scalar() or 0,
            total_revenue=revenue.scalar() or Decimal("0.00"),
            pending_orders=pending_orders.scalar() or 0,
            active_listings=active_products.scalar() or 0,
            new_users_today=new_users_today.scalar() or 0,
            revenue_today=revenue_today.scalar() or Decimal("0.00"),
        )

    async def get_revenue_analytics(self, period: str = "this_month") -> RevenueAnalyticsResponse:
        now = datetime.now(timezone.utc)
        if period == "this_month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "last_month":
            first_of_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_date = (first_of_this - timedelta(days=1)).replace(day=1)
        else:
            start_date = now - timedelta(days=30)

        payments_result = await self.db.execute(
            select(Payment).where(
                Payment.status == TransactionStatus.SUCCESS,
                Payment.paid_at >= start_date,
                Payment.deleted_at.is_(None),
            )
        )
        payments = payments_result.scalars().all()

        return RevenueAnalyticsResponse(
            total_revenue=sum(p.amount for p in payments) if payments else Decimal("0.00"),
            platform_fees=sum(p.gateway_fee for p in payments) if payments else Decimal("0.00"),
            seller_earnings=sum(p.net_amount for p in payments) if payments else Decimal("0.00"),
            period=period,
        )

    async def get_user_analytics(self) -> UserAnalyticsResponse:
        result = await self.db.execute(select(User).where(User.deleted_at.is_(None)))
        users = result.scalars().all()

        total = len(users)
        buyers = sum(1 for u in users if u.role.value == "buyer")
        sellers = sum(1 for u in users if u.role.value == "seller")
        verified = sum(1 for u in users if u.is_verified)
        active = sum(1 for u in users if u.status == UserStatus.ACTIVE)

        return UserAnalyticsResponse(
            total_users=total,
            active_users=active,
            buyer_count=buyers,
            seller_count=sellers,
            verified_users=verified,
        )

    async def get_product_analytics(self) -> ProductAnalyticsResponse:
        result = await self.db.execute(select(Product).where(Product.deleted_at.is_(None)))
        products = result.scalars().all()

        total = len(products)
        active = sum(1 for p in products if p.is_active)
        pending = sum(1 for p in products if p.status.value == "pending")

        return ProductAnalyticsResponse(
            total_products=total,
            active_products=active,
            pending_products=pending,
            top_selling=[{"title": p.title, "sales": p.total_sales} for p in sorted(products, key=lambda x: x.total_sales, reverse=True)[:10]],
        )

    async def save_report(self, request: CreateReportRequest, user_id: uuid.UUID) -> SavedReportResponse:
        report = SavedReport(
            id=uuid.uuid4(),
            user_id=user_id,
            name=request.name,
            report_type=request.report_type,
            period=request.period,
            filters=request.filters,
            config=request.config,
            schedule=request.schedule,
        )
        await self.report_repo.create(report)
        return SavedReportResponse.model_validate(report)

    async def list_saved_reports(self, user_id: uuid.UUID) -> list[SavedReportResponse]:
        result = await self.db.execute(
            select(SavedReport).where(
                SavedReport.user_id == user_id, SavedReport.deleted_at.is_(None)
            ).order_by(SavedReport.created_at.desc())
        )
        return [SavedReportResponse.model_validate(r) for r in result.scalars().all()]
