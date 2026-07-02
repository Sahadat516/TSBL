from __future__ import annotations

import time

from redis.asyncio import Redis

from app.modules.auth.domain.interfaces import RateLimiter


class RedisRateLimiter(RateLimiter):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = int(time.time())
        window_key = f"ratelimit:{key}:{now // window_seconds}"

        count = await self.redis.incr(window_key)
        if count == 1:
            await self.redis.expire(window_key, window_seconds + 1)

        return count <= max_requests

    async def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        now = int(time.time())
        window_key = f"ratelimit:{key}:{now // window_seconds}"

        current = await self.redis.get(window_key)
        if current is None:
            return max_requests
        return max(0, max_requests - int(current))

    async def reset(self, key: str) -> None:
        pattern = f"ratelimit:{key}:*"
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break


class InMemoryRateLimiter(RateLimiter):
    def __init__(self) -> None:
        self._store: dict[str, dict[int, int]] = {}

    async def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = int(time.time())
        window = now // window_seconds

        if key not in self._store:
            self._store[key] = {}

        if window not in self._store[key]:
            self._store[key] = {window: 1}
            return True

        self._store[key][window] += 1
        return self._store[key][window] <= max_requests

    async def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        now = int(time.time())
        window = now // window_seconds

        if key not in self._store or window not in self._store[key]:
            return max_requests
        return max(0, max_requests - self._store[key][window])

    async def reset(self, key: str) -> None:
        self._store.pop(key, None)


def get_rate_limiter(redis: Redis | None = None) -> RateLimiter:
    if redis:
        return RedisRateLimiter(redis)
    return InMemoryRateLimiter()
