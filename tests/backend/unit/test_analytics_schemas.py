from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.analytics.schemas.analytics_schema import (
    AdminAnalyticsResponse,
    DashboardStatsResponse,
    ProductAnalyticsResponse,
    RevenueAnalyticsItem,
    RevenueAnalyticsResponse,
    SaveReportRequest,
    SavedReportResponse,
    UserAnalyticsResponse,
)


class TestDashboardStatsResponse:
    def test_valid(self):
        resp = DashboardStatsResponse(
            total_users=100,
            total_products=50,
            total_orders=200,
            total_revenue="50000.00",
            active_sellers=10,
            pending_orders=5,
        )
        assert resp.total_users == 100
        assert resp.total_revenue == "50000.00"

    def test_zero_defaults(self):
        resp = DashboardStatsResponse()
        assert resp.total_users == 0
        assert resp.total_revenue == "0.00"


class TestRevenueAnalyticsItem:
    def test_valid(self):
        item = RevenueAnalyticsItem(
            period="2026-01",
            revenue="1000.00",
            orders=10,
            average_order_value="100.00",
        )
        assert item.period == "2026-01"
        assert item.orders == 10


class TestRevenueAnalyticsResponse:
    def test_valid(self):
        items = [
            RevenueAnalyticsItem(period="2026-01", revenue="1000.00", orders=10, average_order_value="100.00"),
        ]
        resp = RevenueAnalyticsResponse(
            items=items,
            total_revenue="1000.00",
            total_orders=10,
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        assert len(resp.items) == 1
        assert resp.total_revenue == "1000.00"


class TestUserAnalyticsResponse:
    def test_valid(self):
        resp = UserAnalyticsResponse(
            total_users=500,
            buyer_count=300,
            seller_count=150,
            admin_count=5,
            verified_sellers=100,
            new_users_30d=20,
        )
        assert resp.buyer_count == 300
        assert resp.verified_sellers == 100


class TestProductAnalyticsResponse:
    def test_valid(self):
        resp = ProductAnalyticsResponse(
            total_products=200,
            active_products=150,
            pending_products=20,
            archived_products=30,
            top_selling=[],
        )
        assert resp.active_products == 150
        assert resp.top_selling == []


class TestAdminAnalyticsResponse:
    def test_valid(self):
        resp = AdminAnalyticsResponse(
            dashboard=DashboardStatsResponse(total_users=100, total_revenue="50000.00"),
            revenue=RevenueAnalyticsResponse(
                items=[],
                total_revenue="0",
                total_orders=0,
                start_date="2026-01-01",
                end_date="2026-01-31",
            ),
        )
        assert resp.dashboard.total_users == 100


class TestSaveReportRequest:
    def test_valid(self):
        req = SaveReportRequest(
            name="Monthly Report",
            report_type="revenue",
            parameters={"start_date": "2026-01-01", "end_date": "2026-01-31"},
        )
        assert req.name == "Monthly Report"

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            SaveReportRequest(
                name="",
                report_type="revenue",
            )


class TestSavedReportResponse:
    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = SavedReportResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="Monthly Report",
            report_type="revenue",
            parameters={},
            created_at=now,
        )
        assert resp.name == "Monthly Report"

    def test_from_attributes(self):
        assert SavedReportResponse.model_config.get("from_attributes") is True
