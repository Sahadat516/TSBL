from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.analytics.domain.value_objects import ReportPeriod, ReportType


class DashboardStatsResponse(BaseModel):
    total_users: int = 0
    total_products: int = 0
    total_orders: int = 0
    total_revenue: Decimal = Decimal("0.00")
    pending_orders: int = 0
    active_listings: int = 0
    new_users_today: int = 0
    revenue_today: Decimal = Decimal("0.00")
    conversion_rate: float = 0.0
    average_order_value: Decimal = Decimal("0.00")


class RevenueChartData(BaseModel):
    labels: list[str] = []
    values: list[Decimal] = []


class RevenueAnalyticsResponse(BaseModel):
    total_revenue: Decimal = Decimal("0.00")
    platform_fees: Decimal = Decimal("0.00")
    seller_earnings: Decimal = Decimal("0.00")
    refunded_amount: Decimal = Decimal("0.00")
    revenue_chart: RevenueChartData = RevenueChartData()
    period: str = "this_month"


class UserAnalyticsResponse(BaseModel):
    total_users: int = 0
    new_users: int = 0
    active_users: int = 0
    buyer_count: int = 0
    seller_count: int = 0
    verified_users: int = 0
    growth_percentage: float = 0.0


class ProductAnalyticsResponse(BaseModel):
    total_products: int = 0
    active_products: int = 0
    pending_products: int = 0
    total_categories: int = 0
    average_price: Decimal = Decimal("0.00")
    top_selling: list[dict] = []


class SavedReportResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    report_type: ReportType
    period: ReportPeriod
    filters: dict | None = None
    config: dict | None = None
    schedule: str | None = None
    last_generated_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateReportRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    report_type: ReportType
    period: ReportPeriod
    filters: dict | None = None
    config: dict | None = None
    schedule: str | None = Field(default=None, pattern="^(never|daily|weekly|monthly)$")
