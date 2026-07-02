from __future__ import annotations

import functools
from typing import Any, Callable, Coroutine

from fastapi import Depends, HTTPException, status

from app.modules.authorization.dependencies import get_authz_service


def require_permission(permission: str):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            authz = kwargs.get("authz_service") or kwargs.get("authz")
            current_user = kwargs.get("current_user")
            if authz and current_user:
                has_perm = await authz.has_permission(current_user.id, permission)
                if not has_perm:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required permission: {permission}",
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: list[str]):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            authz = kwargs.get("authz_service") or kwargs.get("authz")
            current_user = kwargs.get("current_user")
            if authz and current_user:
                has_perm = await authz.has_any_permission(current_user.id, permissions)
                if not has_perm:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing any required permission",
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_ownership(resource_id_param: str = "resource_id"):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_user = kwargs.get("current_user")
            authz = kwargs.get("authz_service") or kwargs.get("authz")
            resource_id = kwargs.get(resource_id_param)

            if current_user and authz:
                roles = await authz.get_user_roles(current_user.id)
                is_admin = any(r.role_slug in ("admin", "super_admin") for r in roles)
                if is_admin:
                    return await func(*args, **kwargs)

            return await func(*args, **kwargs)
        return wrapper
    return decorator
