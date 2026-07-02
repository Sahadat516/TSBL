from __future__ import annotations

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = str(record.user_id)
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        return json.dumps(log_entry, default=str)


def _create_file_handler(filename: str, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        LOG_DIR / filename,
        max_bytes=10485760,
        backupCount=10,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(JSONFormatter())
    return handler


def _create_console_handler(level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(JSONFormatter())
    return handler


def _configure_logger(name: str, level: int, filename: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(_create_console_handler(level))
    if filename:
        logger.addHandler(_create_file_handler(filename, level))
    logger.propagate = False
    return logger


app_logger = _configure_logger("tsbl", logging.INFO, "app.log")


class SecurityLogger:
    logger = _configure_logger("tsbl.security", logging.WARNING, "security.log")

    @classmethod
    def log(cls, event: str, user_id: str | None = None, details: dict[str, Any] | None = None) -> None:
        extra = {"user_id": user_id} if user_id else {}
        cls.logger.warning(f"SECURITY:{event}", extra=extra, exc_info=False)


class AuditLogger:
    logger = _configure_logger("tsbl.audit", logging.INFO, "audit.log")

    @classmethod
    def log(cls, action: str, actor_id: str, resource: str, resource_id: str, details: dict[str, Any] | None = None) -> None:
        cls.logger.info(
            f"AUDIT:{action}:{resource}:{resource_id}",
            extra={"user_id": actor_id},
        )


class PerformanceLogger:
    logger = _configure_logger("tsbl.performance", logging.INFO, "performance.log")

    @classmethod
    def log_request(cls, method: str, path: str, duration_ms: float, status_code: int) -> None:
        cls.logger.info(f"PERF:{method}:{path}:{status_code}:{duration_ms:.2f}ms")
