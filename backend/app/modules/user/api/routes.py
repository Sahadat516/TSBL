from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.domain.entities import User
from app.modules.user.application.user_service import UserService
from app.modules.user.schemas.user_schema import ProfileResponse, UpdateProfileRequest, UserDetailResponse, UserPublicResponse

router = APIRouter(prefix="/users", tags=["User Management"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_detail(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    return await service.get_user(current_user.id)


@router.patch("/me", response_model=ProfileResponse)
async def update_current_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> ProfileResponse:
    return await service.update_profile(current_user.id, request)


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_by_id(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserPublicResponse:
    return await service.get_user_by_id(uuid.UUID(user_id))
