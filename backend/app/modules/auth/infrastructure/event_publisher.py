from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.core.logging import AuditLogger, SecurityLogger
from app.modules.auth.domain.events import DomainEvent
from app.modules.auth.domain.interfaces import EventPublisher


class RedisEventPublisher(EventPublisher):
    def __init__(self, redis: Redis | None = None) -> None:
        self.redis = redis
        self._channel = "auth:events"

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        if self.redis:
            message = json.dumps({"event": event_name, "payload": payload}, default=str)
            await self.redis.publish(self._channel, message)

        AuditLogger.log(
            action=event_name,
            actor_id=payload.get("user_id", "system"),
            resource="auth",
            resource_id=payload.get("user_id", "unknown"),
            details=payload,
        )


class LoggingEventPublisher(EventPublisher):
    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        SecurityLogger.log(event=event_name, user_id=payload.get("user_id"), details=payload)
        AuditLogger.log(
            action=event_name,
            actor_id=payload.get("user_id", "system"),
            resource="auth",
            resource_id=payload.get("user_id", "unknown"),
            details=payload,
        )


def get_event_publisher(redis: Redis | None = None) -> EventPublisher:
    if redis:
        return RedisEventPublisher(redis)
    return LoggingEventPublisher()
