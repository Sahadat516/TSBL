from __future__ import annotations

import traceback
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.logging import app_logger, SecurityLogger
from app.exceptions.base import AppException


def _build_error_response(
    status_code: int,
    code: str,
    detail: str,
    request: Request,
    context: dict[str, Any] | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": code,
        "detail": detail,
        "request_id": getattr(request.state, "request_id", None),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }
    if context:
        error["context"] = context
    return JSONResponse(
        status_code=status_code,
        content={"error": error},
        headers=getattr(request.state, "error_headers", None),
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return _build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        detail=exc.detail,
        request=request,
        context=exc.context,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return _build_error_response(
        status_code=exc.status_code,
        code="http_error",
        detail=str(exc.detail),
        request=request,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    detail = errors[0]["msg"] if errors else "Validation failed"
    return _build_error_response(
        status_code=422,
        code="validation_error",
        detail=detail,
        request=request,
        context={"errors": errors},
    )


async def pydantic_validation_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    errors = exc.errors()
    return _build_error_response(
        status_code=422,
        code="validation_error",
        detail=str(errors[0]["msg"]) if errors else "Validation failed",
        request=request,
        context={"errors": errors},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app_logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    SecurityLogger.log(
        event="UNHANDLED_EXCEPTION",
        details={"path": str(request.url), "method": request.method},
    )
    return _build_error_response(
        status_code=500,
        code="internal_error",
        detail="An unexpected error occurred",
        request=request,
    )


exception_handlers = {
    AppException: app_exception_handler,
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    PydanticValidationError: pydantic_validation_handler,
    Exception: unhandled_exception_handler,
}
