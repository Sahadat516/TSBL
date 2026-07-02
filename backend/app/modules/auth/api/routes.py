import hashlib

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, security_scheme
from app.modules.auth.application.auth_service import AuthService
from app.modules.auth.domain.entities import User
from app.modules.auth.schemas.auth_schema import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.register(request)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    request_obj: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    ip_address = request_obj.client.host if request_obj.client else "unknown"
    return await auth_service.login(request, ip_address)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_token(request.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    await auth_service.logout(current_user.id, token_hash)
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=204)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.change_password(str(current_user.id), request.current_password, request.new_password)
    return None


@router.post("/forgot-password", status_code=204)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.forgot_password(request.email)
    return None


@router.post("/reset-password", status_code=204)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.reset_password(request.token, request.password, request.confirm_password)
    return None
