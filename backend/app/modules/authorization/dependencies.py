from __future__ import annotations

from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_redis
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.authorization.application.authorization_service import AuthorizationService


async def get_authz_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> AuthorizationService:
    return AuthorizationService(db=db, redis=redis)


async def require_permission(permission: str):
    async def _require_permission(
        current_user: User = Depends(get_current_user),
        authz: AuthorizationService = Depends(get_authz_service),
    ) -> User:
        has_perm = await authz.has_permission(current_user.id, permission)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
            )
        return current_user
    return _require_permission


async def require_any_permission(permissions: list[str]):
    async def _require_any_permission(
        current_user: User = Depends(get_current_user),
        authz: AuthorizationService = Depends(get_authz_service),
    ) -> User:
        has_perm = await authz.has_any_permission(current_user.id, permissions)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing any of required permissions: {', '.join(permissions)}",
            )
        return current_user
    return _require_any_permission


async def require_all_permissions(permissions: list[str]):
    async def _require_all_permissions(
        current_user: User = Depends(get_current_user),
        authz: AuthorizationService = Depends(get_authz_service),
    ) -> User:
        has_perm = await authz.has_all_permissions(current_user.id, permissions)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(permissions)}",
            )
        return current_user
    return _require_all_permissions


async def require_admin(
    current_user: User = Depends(get_current_user),
    authz: AuthorizationService = Depends(get_authz_service),
) -> User:
    roles = await authz.get_user_roles(current_user.id)
    admin_slugs = {"admin", "super_admin"}
    if not any(r.role_slug in admin_slugs for r in roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_super_admin(
    current_user: User = Depends(get_current_user),
    authz: AuthorizationService = Depends(get_authz_service),
) -> User:
    roles = await authz.get_user_roles(current_user.id)
    if not any(r.role_slug == "super_admin" for r in roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user


async def get_current_user_permissions(
    current_user: User = Depends(get_current_user),
    authz: AuthorizationService = Depends(get_authz_service),
) -> list[str]:
    return await authz.get_user_permissions(current_user.id)
