from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.authorization.application.authorization_service import AuthorizationService
from app.modules.authorization.dependencies import (
    get_authz_service,
    get_current_user_permissions,
    require_admin,
    require_permission,
    require_super_admin,
)
from app.modules.authorization.schemas.authz_schema import (
    AssignPermissionRequest,
    AssignRoleRequest,
    AuthorizationLogListResponse,
    BulkAssignRoleRequest,
    BulkRemoveRoleRequest,
    FeatureFlagCreateRequest,
    FeatureFlagListResponse,
    FeatureFlagResponse,
    FeatureFlagUpdateRequest,
    PermissionCreateRequest,
    PermissionEvaluateRequest,
    PermissionEvaluateResponse,
    PermissionGroupCreateRequest,
    PermissionGroupResponse,
    PermissionListResponse,
    PermissionResponse,
    PermissionUpdateRequest,
    RemovePermissionRequest,
    RemoveRoleRequest,
    RoleCreateRequest,
    RoleListResponse,
    RoleResponse,
    RoleUpdateRequest,
    SyncRolePermissionsRequest,
    UserRoleResponse,
)

router = APIRouter(prefix="/authz", tags=["Authorization"])


# --- Role Management ---

@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    request: RoleCreateRequest,
    current_user: User = Depends(require_permission("roles:create")),
    service: AuthorizationService = Depends(get_authz_service),
) -> RoleResponse:
    return await service.create_role(request, current_user.id)


@router.get("/roles", response_model=RoleListResponse)
async def list_roles(
    search: str | None = Query(None),
    sort_by: str = Query("priority"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("roles:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> RoleListResponse:
    return await service.list_roles(search, sort_by, sort_order, page, page_size)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    current_user: User = Depends(require_permission("roles:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> RoleResponse:
    return await service.get_role(uuid.UUID(role_id))


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    request: RoleUpdateRequest,
    current_user: User = Depends(require_permission("roles:update")),
    service: AuthorizationService = Depends(get_authz_service),
) -> RoleResponse:
    return await service.update_role(uuid.UUID(role_id), request, current_user.id)


@router.delete("/roles/{role_id}", status_code=200)
async def delete_role(
    role_id: str,
    current_user: User = Depends(require_permission("roles:delete")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.delete_role(uuid.UUID(role_id), current_user.id)
    return {"ok": True}


@router.post("/roles/{role_id}/sync-permissions", status_code=200)
async def sync_role_permissions(
    role_id: str,
    request: SyncRolePermissionsRequest,
    current_user: User = Depends(require_permission("roles:manage_permissions")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.sync_role_permissions(uuid.UUID(role_id), request.permission_ids, current_user.id)
    return {"ok": True}


@router.get("/roles/{role_id}/permissions", response_model=list[str])
async def get_role_permissions(
    role_id: str,
    current_user: User = Depends(require_permission("roles:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> list[str]:
    return await service.permission_repo.get_permission_strings_by_role(uuid.UUID(role_id))


# --- Permission Management ---

@router.post("/permissions", response_model=PermissionResponse, status_code=201)
async def create_permission(
    request: PermissionCreateRequest,
    current_user: User = Depends(require_permission("permissions:create")),
    service: AuthorizationService = Depends(get_authz_service),
) -> PermissionResponse:
    return await service.create_permission(request, current_user.id)


@router.get("/permissions", response_model=PermissionListResponse)
async def list_permissions(
    group_id: str | None = Query(None),
    resource: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("resource"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_permission("permissions:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> PermissionListResponse:
    gid = uuid.UUID(group_id) if group_id else None
    return await service.list_permissions(gid, resource, search, sort_by, sort_order, page, page_size)


@router.put("/permissions/{perm_id}", response_model=PermissionResponse)
async def update_permission(
    perm_id: str,
    request: PermissionUpdateRequest,
    current_user: User = Depends(require_permission("permissions:update")),
    service: AuthorizationService = Depends(get_authz_service),
) -> PermissionResponse:
    return await service.update_permission(uuid.UUID(perm_id), request, current_user.id)


@router.delete("/permissions/{perm_id}", status_code=200)
async def delete_permission(
    perm_id: str,
    current_user: User = Depends(require_permission("permissions:delete")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.delete_permission(uuid.UUID(perm_id), current_user.id)
    return {"ok": True}


# --- Permission Groups ---

@router.post("/groups", response_model=PermissionGroupResponse, status_code=201)
async def create_group(
    request: PermissionGroupCreateRequest,
    current_user: User = Depends(require_permission("permissions:create")),
    service: AuthorizationService = Depends(get_authz_service),
) -> PermissionGroupResponse:
    return await service.create_group(request, current_user.id)


@router.get("/groups", response_model=list[PermissionGroupResponse])
async def list_groups(
    current_user: User = Depends(require_permission("permissions:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> list[PermissionGroupResponse]:
    return await service.list_groups()


# --- Role Assignment ---

@router.post("/assign-role", response_model=UserRoleResponse, status_code=201)
async def assign_role(
    request: AssignRoleRequest,
    current_user: User = Depends(require_permission("roles:assign")),
    service: AuthorizationService = Depends(get_authz_service),
) -> UserRoleResponse:
    return await service.assign_role(request, current_user.id)


@router.post("/remove-role", status_code=200)
async def remove_role(
    request: RemoveRoleRequest,
    current_user: User = Depends(require_permission("roles:assign")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.remove_role(request, current_user.id)
    return {"ok": True}


@router.post("/bulk-assign-role", status_code=200)
async def bulk_assign_role(
    request: BulkAssignRoleRequest,
    current_user: User = Depends(require_permission("roles:assign")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    count = await service.bulk_assign_role(request, current_user.id)
    return {"assigned": count}


@router.post("/bulk-remove-role", status_code=200)
async def bulk_remove_role(
    request: BulkRemoveRoleRequest,
    current_user: User = Depends(require_permission("roles:assign")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    count = await service.bulk_remove_role(request, current_user.id)
    return {"removed": count}


# --- Direct User Permissions ---

@router.post("/assign-permission", status_code=200)
async def assign_permission(
    request: AssignPermissionRequest,
    current_user: User = Depends(require_permission("permissions:direct_assign")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.assign_permission(request, current_user.id)
    return {"ok": True}


@router.post("/remove-permission", status_code=200)
async def remove_permission(
    request: RemovePermissionRequest,
    current_user: User = Depends(require_permission("permissions:direct_assign")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.remove_permission(request, current_user.id)
    return {"ok": True}


# --- User Permission Lookup ---

@router.get("/users/{user_id}/permissions", response_model=list[str])
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(require_permission("permissions:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> list[str]:
    return await service.get_user_permissions(uuid.UUID(user_id))


@router.get("/users/{user_id}/roles", response_model=list[UserRoleResponse])
async def get_user_roles(
    user_id: str,
    current_user: User = Depends(require_permission("roles:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> list[UserRoleResponse]:
    return await service.get_user_roles(uuid.UUID(user_id))


@router.get("/me/permissions", response_model=list[str])
async def my_permissions(
    current_user: User = Depends(get_current_user),
    service: AuthorizationService = Depends(get_authz_service),
) -> list[str]:
    return await service.get_user_permissions(current_user.id)


@router.get("/me/roles", response_model=list[UserRoleResponse])
async def my_roles(
    current_user: User = Depends(get_current_user),
    service: AuthorizationService = Depends(get_authz_service),
) -> list[UserRoleResponse]:
    return await service.get_user_roles(current_user.id)


# --- Permission Evaluation ---

@router.post("/evaluate", response_model=PermissionEvaluateResponse)
async def evaluate_permission(
    request: PermissionEvaluateRequest,
    current_user: User = Depends(require_permission("permissions:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> PermissionEvaluateResponse:
    return await service.check_permission(
        request.user_id, request.permission, request.resource_id, request.context,
    )


@router.post("/check", response_model=bool)
async def check_permission(
    permission: str,
    current_user: User = Depends(get_current_user),
    service: AuthorizationService = Depends(get_authz_service),
) -> bool:
    return await service.has_permission(current_user.id, permission)


# --- Feature Flags ---

@router.post("/feature-flags", response_model=FeatureFlagResponse, status_code=201)
async def create_feature_flag(
    request: FeatureFlagCreateRequest,
    current_user: User = Depends(require_permission("feature_flags:create")),
    service: AuthorizationService = Depends(get_authz_service),
) -> FeatureFlagResponse:
    return await service.create_feature_flag(request)


@router.get("/feature-flags", response_model=FeatureFlagListResponse)
async def list_feature_flags(
    is_enabled: bool | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("feature_flags:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> FeatureFlagListResponse:
    return await service.list_feature_flags(is_enabled, search, page, page_size)


@router.put("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_id: str,
    request: FeatureFlagUpdateRequest,
    current_user: User = Depends(require_permission("feature_flags:update")),
    service: AuthorizationService = Depends(get_authz_service),
) -> FeatureFlagResponse:
    return await service.update_feature_flag(uuid.UUID(flag_id), request)


@router.delete("/feature-flags/{flag_id}", status_code=200)
async def delete_feature_flag(
    flag_id: str,
    current_user: User = Depends(require_permission("feature_flags:delete")),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    await service.delete_feature_flag(uuid.UUID(flag_id))
    return {"ok": True}


# --- Authorization Logs ---

@router.get("/logs", response_model=AuthorizationLogListResponse)
async def list_authorization_logs(
    user_id: str | None = Query(None),
    action: str | None = Query(None),
    resource: str | None = Query(None),
    is_granted: bool | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_permission("authorization_logs:view")),
    service: AuthorizationService = Depends(get_authz_service),
) -> AuthorizationLogListResponse:
    uid = uuid.UUID(user_id) if user_id else None
    return await service.get_authorization_logs(uid, action, resource, is_granted, from_date, to_date, page, page_size)


# --- Seed Defaults ---

@router.post("/seed", status_code=200)
async def seed_defaults(
    current_user: User = Depends(require_super_admin),
    service: AuthorizationService = Depends(get_authz_service),
) -> dict:
    result = await service.seed_defaults()
    return {"seeded": result}
