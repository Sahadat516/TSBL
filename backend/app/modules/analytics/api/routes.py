from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.modules.analytics.application.analytics_service import AnalyticsService
from app.modules.analytics.schemas.analytics_schema import (
    CreateReportRequest,
    DashboardStatsResponse,
    ProductAnalyticsResponse,
    RevenueAnalyticsResponse,
    SavedReportResponse,
    UserAnalyticsResponse,
)
from app.modules.auth.domain.entities import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    admin: User = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> DashboardStatsResponse:
    return await service.get_dashboard_stats()


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    period: str = Query("this_month", regex="^(today|this_week|this_month|last_month|this_quarter|this_year)$"),
    admin: User = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> RevenueAnalyticsResponse:
    return await service.get_revenue_analytics(period)


@router.get("/users", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    admin: User = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> UserAnalyticsResponse:
    return await service.get_user_analytics()


@router.get("/products", response_model=ProductAnalyticsResponse)
async def get_product_analytics(
    admin: User = Depends(get_current_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ProductAnalyticsResponse:
    return await service.get_product_analytics()


@router.post("/reports", response_model=SavedReportResponse, status_code=201)
async def save_report(
    request: CreateReportRequest,
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> SavedReportResponse:
    return await service.save_report(request, current_user.id)


@router.get("/reports", response_model=list[SavedReportResponse])
async def list_reports(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[SavedReportResponse]:
    return await service.list_saved_reports(current_user.id)
