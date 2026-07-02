from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_redis

router = APIRouter(tags=["Health"])

_startup_time = datetime.now(timezone.utc)


class HealthStatus(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    timestamp: str


class ReadinessStatus(BaseModel):
    status: str
    database: str
    redis: str
    database_latency_ms: float | None = None
    redis_latency_ms: float | None = None


class LivenessStatus(BaseModel):
    status: str


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check() -> HealthStatus:
    uptime = (datetime.now(timezone.utc) - _startup_time).total_seconds()
    return HealthStatus(
        status="healthy",
        version=settings.app_version,
        uptime_seconds=uptime,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", response_model=ReadinessStatus, status_code=status.HTTP_200_OK)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ReadinessStatus:
    db_ok = False
    db_latency: float | None = None
    try:
        import time
        t0 = time.monotonic()
        await db.execute(select(1))
        db_latency = (time.monotonic() - t0) * 1000
        db_ok = True
    except Exception:
        db_ok = False

    redis_ok = False
    redis_latency: float | None = None
    try:
        import time
        t0 = time.monotonic()
        await redis.ping()
        redis_latency = (time.monotonic() - t0) * 1000
        redis_ok = True
    except Exception:
        redis_ok = False

    overall = "ready" if (db_ok and redis_ok) else "degraded"
    status_code = status.HTTP_200_OK if overall == "ready" else status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessStatus(
        status=overall,
        database="connected" if db_ok else "disconnected",
        redis="connected" if redis_ok else "disconnected",
        database_latency_ms=db_latency,
        redis_latency_ms=redis_latency,
    )


@router.get("/live", response_model=LivenessStatus, status_code=status.HTTP_200_OK)
async def liveness_check() -> LivenessStatus:
    return LivenessStatus(status="alive")
