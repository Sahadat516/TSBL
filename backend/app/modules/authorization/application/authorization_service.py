from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import AuditLogger, SecurityLogger
from app.modules.authorization.domain.entities import (
    AuthorizationLog,
    FeatureFlag,
    Permission,
    PermissionGroup,
    Role,
    RolePermission,
    UserPermission,
    UserRole,
)
from app.modules.authorization.infrastructure.authorization_repository import (
    AuthorizationLogRepository,
    FeatureFlagRepository,
    PermissionGroupRepository,
    PermissionRepository,
    RolePermissionRepository,
    RoleRepository,
    UserPermissionRepository,
    UserRoleRepository,
)
from app.modules.authorization.infrastructure.permission_cache import PermissionCache
from app.modules.authorization.schemas.authz_schema import (
    AssignPermissionRequest,
    AssignRoleRequest,
    AuthorizationLogListResponse,
    AuthorizationLogResponse,
    BulkAssignRoleRequest,
    BulkRemoveRoleRequest,
    FeatureFlagCreateRequest,
    FeatureFlagListResponse,
    FeatureFlagResponse,
    FeatureFlagUpdateRequest,
    PermissionCreateRequest,
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
    UserRoleResponse,
)
from app.modules.authorization.seed import DEFAULT_ROLES, DEFAULT_PERMISSIONS, PERMISSION_GROUPS


class AuthorizationService:
    def __init__(self, db: AsyncSession, redis: Redis | None = None) -> None:
        self.db = db
        self.cache = PermissionCache(redis) if redis else None
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
        self.group_repo = PermissionGroupRepository(db)
        self.user_role_repo = UserRoleRepository(db)
        self.user_perm_repo = UserPermissionRepository(db)
        self.role_perm_repo = RolePermissionRepository(db)
        self.flag_repo = FeatureFlagRepository(db)
        self.log_repo = AuthorizationLogRepository(db)

    async def seed_defaults(self) -> dict[str, int]:
        result = {"roles": 0, "permissions": 0, "groups": 0}

        for group_data in PERMISSION_GROUPS:
            existing = await self.group_repo.find_by_slug(group_data["slug"])
            if not existing:
                group = PermissionGroup(
                    id=uuid.uuid4(),
                    name=group_data["name"],
                    slug=group_data["slug"],
                    description=group_data.get("description"),
                    sort_order=group_data.get("sort_order", 0),
                )
                await self.group_repo.create(group)
                result["groups"] += 1

        for perm_data in DEFAULT_PERMISSIONS:
            existing = await self.permission_repo.find_by_resource_action(
                perm_data["resource"], perm_data["action"]
            )
            if not existing:
                group = await self.group_repo.find_by_slug(perm_data.get("group", ""))
                perm = Permission(
                    id=uuid.uuid4(),
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    name=perm_data["name"],
                    description=perm_data.get("description"),
                    group_id=group.id if group else None,
                    is_system=True,
                )
                await self.permission_repo.create(perm)
                result["permissions"] += 1

        for role_data in DEFAULT_ROLES:
            existing = await self.role_repo.find_by_slug(role_data["slug"])
            if not existing:
                role = Role(
                    id=uuid.uuid4(),
                    name=role_data["name"],
                    slug=role_data["slug"],
                    description=role_data.get("description"),
                    is_system=True,
                    is_default=role_data.get("is_default", False),
                    priority=role_data.get("priority", 0),
                )
                await self.role_repo.create(role)

                for perm_slug in role_data.get("permissions", []):
                    resource, action = perm_slug.split(":", 1)
                    perm = await self.permission_repo.find_by_resource_action(resource, action)
                    if perm:
                        rp = RolePermission(
                            id=uuid.uuid4(), role_id=role.id, permission_id=perm.id, is_granted=True
                        )
                        self.db.add(rp)

                result["roles"] += 1

        await self.db.flush()
        await self._invalidate_all_cache()
        return result

    async def create_role(self, request: RoleCreateRequest, actor_id: uuid.UUID) -> RoleResponse:
        existing = await self.role_repo.find_by_slug(request.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role slug already exists")

        role = Role(
            id=uuid.uuid4(),
            name=request.name,
            slug=request.slug,
            description=request.description,
            is_default=request.is_default,
            priority=request.priority,
            metadata=request.metadata,
        )
        await self.role_repo.create(role)

        AuditLogger.log(
            action="ROLE_CREATED", actor_id=str(actor_id),
            resource="role", resource_id=str(role.id),
            details={"name": request.name, "slug": request.slug},
        )
        return await self._build_role_response(role.id)

    async def update_role(self, role_id: uuid.UUID, request: RoleUpdateRequest, actor_id: uuid.UUID) -> RoleResponse:
        role = await self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        if role.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify system roles")

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(role, field):
                setattr(role, field, value)

        await self.db.flush()

        AuditLogger.log(
            action="ROLE_UPDATED", actor_id=str(actor_id),
            resource="role", resource_id=str(role_id),
            details={"changes": list(update_data.keys())},
        )
        return await self._build_role_response(role_id)

    async def delete_role(self, role_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        role = await self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        if role.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete system roles")

        await self.role_repo.soft_delete(role_id)
        await self._invalidate_role_cache(role_id)

        AuditLogger.log(
            action="ROLE_DELETED", actor_id=str(actor_id),
            resource="role", resource_id=str(role_id),
        )

    async def get_role(self, role_id: uuid.UUID) -> RoleResponse:
        role = await self.role_repo.get_with_counts(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return await self._build_role_response(role_id)

    async def list_roles(
        self, search: str | None = None,
        sort_by: str = "priority", sort_order: str = "asc",
        page: int = 1, page_size: int = 20,
    ) -> RoleListResponse:
        roles, total = await self.role_repo.list_all(search, sort_by, sort_order, page, page_size)
        items = []
        for role in roles:
            items.append(await self._build_role_response(role.id))

        total_pages = max(1, (total + page_size - 1) // page_size)
        return RoleListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)

    async def _build_role_response(self, role_id: uuid.UUID) -> RoleResponse:
        role = await self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        perm_count = await self.role_repo.count_permissions(role_id)
        user_count = await self.role_repo.count_users(role_id)
        return RoleResponse(
            id=role.id, name=role.name, slug=role.slug,
            description=role.description, is_system=role.is_system,
            is_default=role.is_default, priority=role.priority,
            permission_count=perm_count, user_count=user_count,
            created_at=role.created_at,
        )

    async def create_permission(self, request: PermissionCreateRequest, actor_id: uuid.UUID) -> PermissionResponse:
        existing = await self.permission_repo.find_by_resource_action(request.resource, request.action)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission already exists")

        perm = Permission(
            id=uuid.uuid4(),
            resource=request.resource,
            action=request.action,
            name=request.name,
            description=request.description,
            group_id=request.group_id,
            conditions=request.conditions,
        )
        await self.permission_repo.create(perm)

        AuditLogger.log(
            action="PERMISSION_CREATED", actor_id=str(actor_id),
            resource="permission", resource_id=str(perm.id),
            details={"resource": request.resource, "action": request.action},
        )
        return await self._build_permission_response(perm.id)

    async def update_permission(self, perm_id: uuid.UUID, request: PermissionUpdateRequest, actor_id: uuid.UUID) -> PermissionResponse:
        perm = await self.permission_repo.get(perm_id)
        if not perm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        if perm.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify system permissions")

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(perm, field):
                setattr(perm, field, value)

        await self.db.flush()

        AuditLogger.log(
            action="PERMISSION_UPDATED", actor_id=str(actor_id),
            resource="permission", resource_id=str(perm_id),
            details={"changes": list(update_data.keys())},
        )
        return await self._build_permission_response(perm_id)

    async def delete_permission(self, perm_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        perm = await self.permission_repo.get(perm_id)
        if not perm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        if perm.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete system permissions")

        await self.permission_repo.soft_delete(perm_id)
        await self._invalidate_all_cache()

        AuditLogger.log(
            action="PERMISSION_DELETED", actor_id=str(actor_id),
            resource="permission", resource_id=str(perm_id),
        )

    async def list_permissions(
        self, group_id: uuid.UUID | None = None,
        resource: str | None = None, search: str | None = None,
        sort_by: str = "resource", sort_order: str = "asc",
        page: int = 1, page_size: int = 50,
    ) -> PermissionListResponse:
        permissions, total = await self.permission_repo.list_all(
            group_id, resource, search, sort_by, sort_order, page, page_size
        )
        items = [await self._build_permission_response(p.id) for p in permissions]
        total_pages = max(1, (total + page_size - 1) // page_size)
        return PermissionListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)

    async def _build_permission_response(self, perm_id: uuid.UUID) -> PermissionResponse:
        perm = await self.permission_repo.get(perm_id)
        if not perm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        group_name = perm.group.name if perm.group else None
        return PermissionResponse(
            id=perm.id, resource=perm.resource, action=perm.action,
            name=perm.name, description=perm.description,
            group_id=perm.group_id, group_name=group_name,
            is_system=perm.is_system, created_at=perm.created_at,
        )

    async def create_group(self, request: PermissionGroupCreateRequest, actor_id: uuid.UUID) -> PermissionGroupResponse:
        existing = await self.group_repo.find_by_slug(request.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Group slug already exists")

        group = PermissionGroup(
            id=uuid.uuid4(), name=request.name, slug=request.slug,
            description=request.description, sort_order=request.sort_order,
        )
        await self.group_repo.create(group)

        AuditLogger.log(
            action="GROUP_CREATED", actor_id=str(actor_id),
            resource="permission_group", resource_id=str(group.id),
            details={"name": request.name},
        )
        return PermissionGroupResponse(
            id=group.id, name=group.name, slug=group.slug,
            description=group.description, sort_order=group.sort_order,
            permission_count=0, created_at=group.created_at,
        )

    async def list_groups(self) -> list[PermissionGroupResponse]:
        groups = await self.group_repo.list_all()
        result = []
        for g in groups:
            count = await self.group_repo.count_permissions(g.id)
            result.append(PermissionGroupResponse(
                id=g.id, name=g.name, slug=g.slug,
                description=g.description, sort_order=g.sort_order,
                permission_count=count, created_at=g.created_at,
            ))
        return result

    async def assign_role(self, request: AssignRoleRequest, actor_id: uuid.UUID) -> UserRoleResponse:
        existing = await self.user_role_repo.find(request.user_id, request.role_id)
        if existing and existing.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already has this role")

        if existing:
            existing.is_active = True
            existing.expires_at = request.expires_at
            existing.assigned_by = actor_id
            ur = existing
        else:
            ur = UserRole(
                id=uuid.uuid4(), user_id=request.user_id, role_id=request.role_id,
                assigned_by=actor_id, expires_at=request.expires_at,
            )
            self.db.add(ur)

        await self.db.flush()
        await self._invalidate_user_cache(request.user_id)

        AuditLogger.log(
            action="ROLE_ASSIGNED", actor_id=str(actor_id),
            resource="user_role", resource_id=str(ur.id),
            details={"user_id": str(request.user_id), "role_id": str(request.role_id)},
        )

        role = await self.role_repo.get(request.role_id)
        return UserRoleResponse(
            id=ur.id, user_id=ur.user_id, role_id=ur.role_id,
            role_name=role.name if role else "", role_slug=role.slug if role else "",
            is_active=ur.is_active, expires_at=ur.expires_at, created_at=ur.created_at,
        )

    async def remove_role(self, request: RemoveRoleRequest, actor_id: uuid.UUID) -> None:
        ur = await self.user_role_repo.find(request.user_id, request.role_id)
        if not ur or not ur.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role assignment not found")

        role = await self.role_repo.get(request.role_id)
        if role and role.is_system and role.slug == "super_admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove super admin role")

        ur.is_active = False
        await self.db.flush()
        await self._invalidate_user_cache(request.user_id)

        AuditLogger.log(
            action="ROLE_REMOVED", actor_id=str(actor_id),
            resource="user_role", resource_id=str(ur.id),
            details={"user_id": str(request.user_id), "role_id": str(request.role_id)},
        )

    async def assign_permission(self, request: AssignPermissionRequest, actor_id: uuid.UUID) -> None:
        existing = await self.user_perm_repo.find(request.user_id, request.permission_id)
        if existing:
            existing.is_granted = request.is_granted
            existing.granted_by = actor_id
            existing.expires_at = request.expires_at
        else:
            up = UserPermission(
                id=uuid.uuid4(), user_id=request.user_id, permission_id=request.permission_id,
                is_granted=request.is_granted, granted_by=actor_id, expires_at=request.expires_at,
            )
            self.db.add(up)

        await self.db.flush()
        await self._invalidate_user_cache(request.user_id)

        AuditLogger.log(
            action="PERMISSION_ASSIGNED", actor_id=str(actor_id),
            resource="user_permission",
            details={"user_id": str(request.user_id), "permission_id": str(request.permission_id), "granted": request.is_granted},
        )

    async def remove_permission(self, request: RemovePermissionRequest, actor_id: uuid.UUID) -> None:
        up = await self.user_perm_repo.find(request.user_id, request.permission_id)
        if not up:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission assignment not found")

        await self.user_perm_repo.hard_delete(up.id)
        await self._invalidate_user_cache(request.user_id)

        AuditLogger.log(
            action="PERMISSION_REMOVED", actor_id=str(actor_id),
            resource="user_permission",
            details={"user_id": str(request.user_id), "permission_id": str(request.permission_id)},
        )

    async def get_user_permissions(self, user_id: uuid.UUID) -> list[str]:
        if self.cache:
            cached = await self.cache.get_user_permissions(user_id)
            if cached is not None:
                return cached

        perms = await self.permission_repo.get_permission_strings_by_user(user_id)

        if self.cache:
            await self.cache.set_user_permissions(user_id, perms)

        return perms

    async def get_user_roles(self, user_id: uuid.UUID) -> list[UserRoleResponse]:
        assignments = await self.user_role_repo.get_user_roles(user_id)
        result = []
        for ur in assignments:
            if ur.role:
                result.append(UserRoleResponse(
                    id=ur.id, user_id=ur.user_id, role_id=ur.role_id,
                    role_name=ur.role.name, role_slug=ur.role.slug,
                    is_active=ur.is_active, expires_at=ur.expires_at, created_at=ur.created_at,
                ))
        return result

    async def check_permission(self, user_id: uuid.UUID, permission: str, resource_id: str | None = None, context: dict | None = None) -> PermissionEvaluateResponse:
        user_perms = await self.get_user_permissions(user_id)

        if permission in user_perms:
            await self._log_access(user_id, permission, "granted", resource_id, "role_permission")
            return PermissionEvaluateResponse(is_granted=True, source="permission", reason="Permission granted")

        direct_perms = await self.user_perm_repo.get_user_permissions(user_id)
        for dp in direct_perms:
            perm_str = f"{dp.permission.resource}:{dp.permission.action}" if dp.permission else ""
            if perm_str == permission and dp.is_granted:
                await self._log_access(user_id, permission, "granted", resource_id, "direct")
                return PermissionEvaluateResponse(is_granted=True, source="direct", reason="Direct permission override")

        await self._log_access(user_id, permission, "denied", resource_id, "none")
        return PermissionEvaluateResponse(is_granted=False, source=None, reason="Permission not found")

    async def has_permission(self, user_id: uuid.UUID, permission: str) -> bool:
        result = await self.check_permission(user_id, permission)
        return result.is_granted

    async def has_any_permission(self, user_id: uuid.UUID, permissions: list[str]) -> bool:
        for perm in permissions:
            if await self.has_permission(user_id, perm):
                return True
        return False

    async def has_all_permissions(self, user_id: uuid.UUID, permissions: list[str]) -> bool:
        for perm in permissions:
            if not await self.has_permission(user_id, perm):
                return False
        return True

    async def bulk_assign_role(self, request: BulkAssignRoleRequest, actor_id: uuid.UUID) -> int:
        count = await self.user_role_repo.bulk_assign(request.user_ids, request.role_id, actor_id)
        for uid in request.user_ids:
            await self._invalidate_user_cache(uid)

        AuditLogger.log(
            action="ROLE_BULK_ASSIGN", actor_id=str(actor_id),
            resource="user_role",
            details={"user_count": len(request.user_ids), "role_id": str(request.role_id)},
        )
        return count

    async def bulk_remove_role(self, request: BulkRemoveRoleRequest, actor_id: uuid.UUID) -> int:
        count = await self.user_role_repo.bulk_remove(request.user_ids, request.role_id)
        for uid in request.user_ids:
            await self._invalidate_user_cache(uid)

        AuditLogger.log(
            action="ROLE_BULK_REMOVE", actor_id=str(actor_id),
            resource="user_role",
            details={"user_count": len(request.user_ids), "role_id": str(request.role_id)},
        )
        return count

    async def sync_role_permissions(self, role_id: uuid.UUID, permission_ids: list[uuid.UUID], actor_id: uuid.UUID) -> None:
        role = await self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        if role.is_system:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify system role permissions")

        await self.role_perm_repo.sync_role_permissions(role_id, permission_ids)
        if self.cache:
            await self.cache.invalidate_role(role_id)
            await self.cache.invalidate_role_all_users(role_id)

        AuditLogger.log(
            action="ROLE_PERMISSIONS_SYNCED", actor_id=str(actor_id),
            resource="role_permission", resource_id=str(role_id),
            details={"permission_count": len(permission_ids)},
        )

    async def create_feature_flag(self, request: FeatureFlagCreateRequest) -> FeatureFlagResponse:
        existing = await self.flag_repo.find_by_slug(request.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Feature flag slug already exists")

        flag = FeatureFlag(
            id=uuid.uuid4(), name=request.name, slug=request.slug,
            description=request.description, is_enabled=request.is_enabled,
            is_global=request.is_global, roles=request.roles,
            users=[str(u) for u in request.users] if request.users else None,
            percentage=request.percentage, metadata=request.metadata,
        )
        await self.flag_repo.create(flag)
        await self._invalidate_flag_cache()
        return FeatureFlagResponse.model_validate(flag)

    async def update_feature_flag(self, flag_id: uuid.UUID, request: FeatureFlagUpdateRequest) -> FeatureFlagResponse:
        flag = await self.flag_repo.get(flag_id)
        if not flag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")

        update_data = request.model_dump(exclude_unset=True)
        if "users" in update_data and update_data["users"] is not None:
            update_data["users"] = [str(u) for u in update_data["users"]]

        for field, value in update_data.items():
            if hasattr(flag, field):
                setattr(flag, field, value)

        await self.db.flush()
        await self._invalidate_flag_cache()
        return FeatureFlagResponse.model_validate(flag)

    async def delete_feature_flag(self, flag_id: uuid.UUID) -> None:
        flag = await self.flag_repo.get(flag_id)
        if not flag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")
        await self.flag_repo.soft_delete(flag_id)
        await self._invalidate_flag_cache()

    async def list_feature_flags(
        self, is_enabled: bool | None = None,
        search: str | None = None, page: int = 1, page_size: int = 20,
    ) -> FeatureFlagListResponse:
        flags, total = await self.flag_repo.list_all(is_enabled, search, page, page_size)
        items = [FeatureFlagResponse.model_validate(f) for f in flags]
        total_pages = max(1, (total + page_size - 1) // page_size)
        return FeatureFlagListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)

    async def is_feature_enabled(self, slug: str, user_id: uuid.UUID | None = None, role: str | None = None) -> bool:
        return await self.flag_repo.is_enabled(slug, user_id, role)

    async def get_authorization_logs(
        self, user_id: uuid.UUID | None = None,
        action: str | None = None, resource: str | None = None,
        is_granted: bool | None = None,
        from_date: datetime | None = None, to_date: datetime | None = None,
        page: int = 1, page_size: int = 50,
    ) -> AuthorizationLogListResponse:
        logs, total = await self.log_repo.list_all(
            user_id, action, resource, is_granted, from_date, to_date, page, page_size
        )
        items = [AuthorizationLogResponse.model_validate(log) for log in logs]
        total_pages = max(1, (total + page_size - 1) // page_size)
        return AuthorizationLogListResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)

    async def _log_access(self, user_id: uuid.UUID, permission: str, action: str, resource_id: str | None = None, reason: str | None = None) -> None:
        parts = permission.split(":", 1)
        resource = parts[0] if len(parts) > 0 else "unknown"
        log = AuthorizationLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            permission=permission,
            is_granted=(action == "granted"),
            reason=reason,
        )
        self.db.add(log)
        await self.db.flush()

        SecurityLogger.log(
            event=f"AUTHZ_{action.upper()}",
            user_id=str(user_id),
            details={"permission": permission, "resource": resource, "resource_id": resource_id, "reason": reason},
        )

    async def _invalidate_user_cache(self, user_id: uuid.UUID) -> None:
        if self.cache:
            await self.cache.invalidate_user(user_id)

    async def _invalidate_role_cache(self, role_id: uuid.UUID) -> None:
        if self.cache:
            await self.cache.invalidate_role(role_id)

    async def _invalidate_flag_cache(self) -> None:
        if self.cache:
            await self.cache.invalidate_feature_flags()

    async def _invalidate_all_cache(self) -> None:
        if self.cache:
            await self.cache.invalidate_all()
