from __future__ import annotations

from enum import StrEnum


class ReportType(StrEnum):
    SALES = "sales"
    REVENUE = "revenue"
    USERS = "users"
    PRODUCTS = "products"
    ORDERS = "orders"
    COMMISSION = "commission"
    AFFILIATE = "affiliate"
    CUSTOM = "custom"


class ReportPeriod(StrEnum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    LAST_QUARTER = "last_quarter"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"
