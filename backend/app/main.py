from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk import init as sentry_init

from app.api.router import api_router
from app.core.config import settings
from app.core.database import close_redis, engine
from app.core.logging import app_logger, SecurityLogger
from app.exceptions import exception_handlers
from app.middleware import CorrelationIDMiddleware, LocalizationMiddleware, RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app_logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    SecurityLogger.log(event="APPLICATION_STARTUP")

    yield

    app_logger.info(f"Shutting down {settings.app_name}")
    SecurityLogger.log(event="APPLICATION_SHUTDOWN")
    await engine.dispose()
    await close_redis()


def create_application() -> FastAPI:
    if settings.sentry_dsn:
        sentry_init(dsn=settings.sentry_dsn, environment=settings.environment)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise multi-vendor digital marketplace API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        default_response_class=JSONResponse,
        exception_handlers=exception_handlers,
    )

    _register_middleware(app)
    _register_routes(app)

    app_logger.info(f"Application initialized with {len(app.routes)} routes")
    return app


def _register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Correlation-ID"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(LocalizationMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(RequestIDMiddleware)


def _register_routes(app: FastAPI) -> None:
    app.include_router(api_router)


app = create_application()
