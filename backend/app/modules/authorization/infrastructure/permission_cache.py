from __future__ import annotations

import json
import uuid

from redis.asyncio import Redis


class PermissionCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self._user_key_prefix = "authz:user:"
        self._role_key_prefix = "authz:role:"
        self._flag_key = "authz:flags"
        self._ttl = 300

    async def get_user_permissions(self, user_id: uuid.UUID) -> list[str] | None:
        key = f"{self._user_key_prefix}{user_id}:perms"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_user_permissions(self, user_id: uuid.UUID, permissions: list[str]) -> None:
        key = f"{self._user_key_prefix}{user_id}:perms"
        await self.redis.setex(key, self._ttl, json.dumps(permissions))

    async def invalidate_user(self, user_id: uuid.UUID) -> None:
        key = f"{self._user_key_prefix}{user_id}:perms"
        await self.redis.delete(key)

    async def get_role_permissions(self, role_id: uuid.UUID) -> list[str] | None:
        key = f"{self._role_key_prefix}{role_id}:perms"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_role_permissions(self, role_id: uuid.UUID, permissions: list[str]) -> None:
        key = f"{self._role_key_prefix}{role_id}:perms"
        await self.redis.setex(key, self._ttl, json.dumps(permissions))

    async def invalidate_role(self, role_id: uuid.UUID) -> None:
        key = f"{self._role_key_prefix}{role_id}:perms"
        await self.redis.delete(key)

    async def invalidate_role_all_users(self, role_id: uuid.UUID) -> None:
        pattern = f"{self._user_key_prefix}*:perms"
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break

    async def get_feature_flags(self) -> dict | None:
        data = await self.redis.get(self._flag_key)
        if data:
            return json.loads(data)
        return None

    async def set_feature_flags(self, flags: dict) -> None:
        await self.redis.setex(self._flag_key, self._ttl, json.dumps(flags))

    async def invalidate_feature_flags(self) -> None:
        await self.redis.delete(self._flag_key)

    async def invalidate_all(self) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=f"{self._user_key_prefix}*")
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=f"{self._role_key_prefix}*")
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
        await self.redis.delete(self._flag_key)
