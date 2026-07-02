from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.base_repository import BaseRepository
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


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Role)

    async def find_by_slug(self, slug: str) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.slug == slug, Role.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.name == name, Role.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        search: str | None = None,
        sort_by: str = "priority",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Role], int]:
        query = select(Role).where(Role.deleted_at.is_(None))

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(Role.name.ilike(pattern), Role.description.ilike(pattern))
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        if total == 0:
            return [], 0

        sort_column = getattr(Role, sort_by, Role.priority)
        order_fn = sort_column.asc() if sort_order == "asc" else sort_column.desc()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(order_fn).offset(offset).limit(page_size)
        )
        roles = list(result.scalars().all())
        return roles, total

    async def get_with_counts(self, role_id: uuid.UUID) -> Role | None:
        result = await self.db.execute(
            select(Role)
            .where(Role.id == role_id, Role.deleted_at.is_(None))
            .options(selectinload(Role.permissions), selectinload(Role.user_assignments))
        )
        return result.scalar_one_or_none()

    async def get_default_roles(self) -> list[Role]:
        result = await self.db.execute(
            select(Role).where(Role.is_default.is_(True), Role.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def count_users(self, role_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(UserRole.id)).where(
                UserRole.role_id == role_id, UserRole.is_active.is_(True)
            )
        )
        return result.scalar() or 0

    async def count_permissions(self, role_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(RolePermission.id)).where(
                RolePermission.role_id == role_id, RolePermission.is_granted.is_(True)
            )
        )
        return result.scalar() or 0


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Permission)

    async def find_by_resource_action(self, resource: str, action: str) -> Permission | None:
        result = await self.db.execute(
            select(Permission).where(
                Permission.resource == resource,
                Permission.action == action,
                Permission.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        group_id: uuid.UUID | None = None,
        resource: str | None = None,
        search: str | None = None,
        sort_by: str = "resource",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Permission], int]:
        query = select(Permission).where(Permission.deleted_at.is_(None))

        if group_id is not None:
            query = query.where(Permission.group_id == group_id)
        if resource:
            query = query.where(Permission.resource == resource)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Permission.name.ilike(pattern),
                    Permission.resource.ilike(pattern),
                    Permission.action.ilike(pattern),
                )
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        if total == 0:
            return [], 0

        sort_column = getattr(Permission, sort_by, Permission.resource)
        order_fn = sort_column.asc() if sort_order == "asc" else sort_column.desc()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(order_fn)
            .offset(offset)
            .limit(page_size)
            .options(joinedload(Permission.group))
        )
        permissions = list(result.unique().scalars().all())
        return permissions, total

    async def get_by_role(self, role_id: uuid.UUID) -> list[Permission]:
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.is_granted.is_(True),
                Permission.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: uuid.UUID) -> list[Permission]:
        role_subquery = (
            select(RolePermission.permission_id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(
                UserRole.user_id == user_id,
                UserRole.is_active.is_(True),
                RolePermission.is_granted.is_(True),
            )
        )
        direct_subquery = (
            select(UserPermission.permission_id)
            .where(
                UserPermission.user_id == user_id,
                UserPermission.is_granted.is_(True),
            )
        )
        union_query = role_subquery.union(direct_subquery).subquery()
        result = await self.db.execute(
            select(Permission)
            .where(
                Permission.id.in_(select(union_query.c.permission_id)),
                Permission.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_permission_strings_by_user(self, user_id: uuid.UUID) -> list[str]:
        permissions = await self.get_by_user(user_id)
        return [f"{p.resource}:{p.action}" for p in permissions]

    async def get_permission_strings_by_role(self, role_id: uuid.UUID) -> list[str]:
        permissions = await self.get_by_role(role_id)
        return [f"{p.resource}:{p.action}" for p in permissions]

    async def resource_exists(self, resource: str) -> bool:
        result = await self.db.execute(
            select(func.count(Permission.id)).where(
                Permission.resource == resource, Permission.deleted_at.is_(None)
            )
        )
        return (result.scalar() or 0) > 0


class PermissionGroupRepository(BaseRepository[PermissionGroup]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, PermissionGroup)

    async def find_by_slug(self, slug: str) -> PermissionGroup | None:
        result = await self.db.execute(
            select(PermissionGroup).where(
                PermissionGroup.slug == slug, PermissionGroup.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[PermissionGroup]:
        result = await self.db.execute(
            select(PermissionGroup)
            .where(PermissionGroup.deleted_at.is_(None))
            .order_by(PermissionGroup.sort_order.asc())
            .options(selectinload(PermissionGroup.permissions))
        )
        return list(result.scalars().all())

    async def count_permissions(self, group_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(Permission.id)).where(
                Permission.group_id == group_id, Permission.deleted_at.is_(None)
            )
        )
        return result.scalar() or 0


class UserRoleRepository(BaseRepository[UserRole]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserRole)

    async def find(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole | None:
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_roles(self, user_id: uuid.UUID) -> list[UserRole]:
        result = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id, UserRole.is_active.is_(True))
            .options(joinedload(UserRole.role))
        )
        return list(result.scalars().all())

    async def get_role_users(self, role_id: uuid.UUID, page: int = 1, page_size: int = 20) -> tuple[list[UserRole], int]:
        query = select(UserRole).where(
            UserRole.role_id == role_id, UserRole.is_active.is_(True)
        )
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        offset = (page - 1) * page_size
        result = await self.db.execute(query.offset(offset).limit(page_size))
        return list(result.scalars().all()), total

    async def bulk_assign(self, user_ids: list[uuid.UUID], role_id: uuid.UUID, assigned_by: uuid.UUID | None = None) -> int:
        count = 0
        for user_id in user_ids:
            existing = await self.find(user_id, role_id)
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    count += 1
            else:
                ur = UserRole(id=uuid.uuid4(), user_id=user_id, role_id=role_id, assigned_by=assigned_by)
                self.db.add(ur)
                count += 1
        await self.db.flush()
        return count

    async def bulk_remove(self, user_ids: list[uuid.UUID], role_id: uuid.UUID) -> int:
        count = 0
        for user_id in user_ids:
            existing = await self.find(user_id, role_id)
            if existing and existing.is_active:
                existing.is_active = False
                count += 1
        await self.db.flush()
        return count


class UserPermissionRepository(BaseRepository[UserPermission]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, UserPermission)

    async def find(self, user_id: uuid.UUID, permission_id: uuid.UUID) -> UserPermission | None:
        result = await self.db.execute(
            select(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_permissions(self, user_id: uuid.UUID) -> list[UserPermission]:
        result = await self.db.execute(
            select(UserPermission)
            .where(UserPermission.user_id == user_id)
            .options(joinedload(UserPermission.permission))
        )
        return list(result.scalars().all())


class RolePermissionRepository(BaseRepository[RolePermission]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, RolePermission)

    async def find(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> RolePermission | None:
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none()

    async def sync_role_permissions(self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]) -> None:
        existing = await self.db.execute(
            select(RolePermission).where(RolePermission.role_id == role_id)
        )
        existing_map = {rp.permission_id: rp for rp in existing.scalars().all()}

        for perm_id in permission_ids:
            if perm_id in existing_map:
                if not existing_map[perm_id].is_granted:
                    existing_map[perm_id].is_granted = True
            else:
                rp = RolePermission(id=uuid.uuid4(), role_id=role_id, permission_id=perm_id, is_granted=True)
                self.db.add(rp)

        for perm_id, rp in existing_map.items():
            if perm_id not in permission_ids and rp.is_granted:
                rp.is_granted = False

        await self.db.flush()


class FeatureFlagRepository(BaseRepository[FeatureFlag]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, FeatureFlag)

    async def find_by_slug(self, slug: str) -> FeatureFlag | None:
        result = await self.db.execute(
            select(FeatureFlag).where(
                FeatureFlag.slug == slug, FeatureFlag.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        is_enabled: bool | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[FeatureFlag], int]:
        query = select(FeatureFlag).where(FeatureFlag.deleted_at.is_(None))

        if is_enabled is not None:
            query = query.where(FeatureFlag.is_enabled == is_enabled)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(FeatureFlag.name.ilike(pattern), FeatureFlag.description.ilike(pattern))
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        if total == 0:
            return [], 0

        offset = (page - 1) * page_size
        result = await self.db.execute(query.order_by(FeatureFlag.name.asc()).offset(offset).limit(page_size))
        return list(result.scalars().all()), total

    async def get_enabled_flags(self) -> list[FeatureFlag]:
        result = await self.db.execute(
            select(FeatureFlag).where(
                FeatureFlag.is_enabled.is_(True), FeatureFlag.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())

    async def is_enabled(self, slug: str, user_id: uuid.UUID | None = None, role: str | None = None) -> bool:
        flag = await self.find_by_slug(slug)
        if not flag or not flag.is_enabled:
            return False
        if flag.is_global:
            return True
        if flag.roles and role and role in flag.roles:
            return True
        if flag.users and user_id and str(user_id) in flag.users:
            return True
        return False


class AuthorizationLogRepository(BaseRepository[AuthorizationLog]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, AuthorizationLog)

    async def list_all(
        self,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        resource: str | None = None,
        is_granted: bool | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuthorizationLog], int]:
        query = select(AuthorizationLog)

        if user_id:
            query = query.where(AuthorizationLog.user_id == user_id)
        if action:
            query = query.where(AuthorizationLog.action == action)
        if resource:
            query = query.where(AuthorizationLog.resource == resource)
        if is_granted is not None:
            query = query.where(AuthorizationLog.is_granted == is_granted)
        if from_date:
            query = query.where(AuthorizationLog.created_at >= from_date)
        if to_date:
            query = query.where(AuthorizationLog.created_at <= to_date)

        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        if total == 0:
            return [], 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(AuthorizationLog.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total
