from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_default: bool = False
    priority: int = 0
    metadata: dict | None = None


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_default: bool | None = None
    priority: int | None = None
    metadata: dict | None = None


class RoleResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    is_system: bool
    is_default: bool
    priority: int
    permission_count: int = 0
    user_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleListResponse(BaseModel):
    items: list[RoleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PermissionCreateRequest(BaseModel):
    resource: str = Field(min_length=2, max_length=100)
    action: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    group_id: UUID | None = None
    conditions: dict | None = None


class PermissionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    group_id: UUID | None = None
    conditions: dict | None = None


class PermissionResponse(BaseModel):
    id: UUID
    resource: str
    action: str
    name: str
    description: str | None
    group_id: UUID | None
    group_name: str | None = None
    is_system: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PermissionListResponse(BaseModel):
    items: list[PermissionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PermissionGroupCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int = 0


class PermissionGroupResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    sort_order: int
    permission_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class AssignRoleRequest(BaseModel):
    user_id: UUID
    role_id: UUID
    expires_at: datetime | None = None


class RemoveRoleRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class AssignPermissionRequest(BaseModel):
    user_id: UUID
    permission_id: UUID
    is_granted: bool = True
    expires_at: datetime | None = None


class RemovePermissionRequest(BaseModel):
    user_id: UUID
    permission_id: UUID


class UserPermissionResponse(BaseModel):
    id: UUID
    user_id: UUID
    permission_id: UUID
    resource: str
    action: str
    permission_name: str
    is_granted: bool
    source: str = "direct"
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    role_name: str
    role_slug: str
    is_active: bool
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_enabled: bool = False
    is_global: bool = True
    roles: list[str] | None = None
    users: list[UUID] | None = None
    percentage: int | None = Field(default=None, ge=0, le=100)
    metadata: dict | None = None


class FeatureFlagUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_enabled: bool | None = None
    is_global: bool | None = None
    roles: list[str] | None = None
    users: list[UUID] | None = None
    percentage: int | None = Field(default=None, ge=0, le=100)
    metadata: dict | None = None


class FeatureFlagResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    is_enabled: bool
    is_global: bool
    roles: list[str] | None
    users: list[UUID] | None
    percentage: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagListResponse(BaseModel):
    items: list[FeatureFlagResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuthorizationLogResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    action: str
    resource: str
    resource_id: str | None
    permission: str | None
    is_granted: bool
    reason: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthorizationLogListResponse(BaseModel):
    items: list[AuthorizationLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PermissionEvaluateRequest(BaseModel):
    user_id: UUID
    permission: str = Field(min_length=1, max_length=200)
    resource_id: str | None = None
    context: dict | None = None


class PermissionEvaluateResponse(BaseModel):
    is_granted: bool
    source: str | None = None
    reason: str | None = None


class PermissionCheckResponse(BaseModel):
    permissions: list[str]


class BulkAssignRoleRequest(BaseModel):
    user_ids: list[UUID] = Field(min_length=1, max_length=100)
    role_id: UUID


class BulkRemoveRoleRequest(BaseModel):
    user_ids: list[UUID] = Field(min_length=1, max_length=100)
    role_id: UUID


class SyncRolePermissionsRequest(BaseModel):
    permission_ids: list[UUID] = Field(min_length=0, max_length=500)
