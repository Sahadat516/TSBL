from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_redis
from app.core.dependencies import get_current_user, security_scheme
from app.modules.auth.application.auth_service import AuthService
from app.modules.auth.domain.entities import User
from app.modules.auth.infrastructure.event_publisher import get_event_publisher
from app.modules.auth.infrastructure.mfa_service import get_mfa_code_generator
from app.modules.auth.infrastructure.rate_limiter import get_rate_limiter
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
from app.modules.auth.schemas.identity_schema import (
    MFAEnableResponse,
    MFAStatusResponse,
    MFAVerifyRequest,
    SendEmailVerificationResponse,
    SessionListResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(
        db=db,
        event_publisher=get_event_publisher(redis),
        mfa_code_generator=get_mfa_code_generator(),
        rate_limiter=get_rate_limiter(redis),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return await auth_service.register(request)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    request_obj: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    ip_address = request_obj.client.host if request_obj.client else "unknown"
    user_agent = request_obj.headers.get("user-agent")
    return await auth_service.login(request, ip_address, user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.refresh_token(request.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    await auth_service.logout(
        user_id=current_user.id,
        token_hash=token_hash,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UpdateProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UpdateProfileResponse:
    return await auth_service.update_profile(current_user.id, request)


@router.post("/change-password", status_code=204)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.change_password(
        str(current_user.id), request.current_password, request.new_password
    )


@router.post("/forgot-password", status_code=204)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.forgot_password(request.email)


@router.post("/reset-password", status_code=204)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.reset_password(
        request.token, request.password, request.confirm_password
    )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionListResponse:
    current_token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    return await auth_service.get_sessions(current_user.id, current_token_hash)


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.revoke_session(current_user.id, uuid.UUID(session_id))


@router.delete("/sessions", status_code=204)
async def revoke_all_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    await auth_service.revoke_all_sessions_except(current_user.id, current_token_hash=token_hash)


@router.post("/mfa/enable", response_model=MFAEnableResponse)
async def enable_mfa(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MFAEnableResponse:
    return await auth_service.enable_mfa(current_user.id)


@router.post("/mfa/verify", status_code=204)
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.verify_mfa(current_user.id, request.code)


@router.post("/mfa/disable", status_code=204)
async def disable_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.disable_mfa(current_user.id, request.code)


@router.get("/mfa/status", response_model=MFAStatusResponse)
async def mfa_status(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MFAStatusResponse:
    return await auth_service.get_mfa_status(current_user.id)


@router.post("/send-email-verification", response_model=SendEmailVerificationResponse)
async def send_email_verification(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SendEmailVerificationResponse:
    await auth_service.send_email_verification(current_user.id)
    return SendEmailVerificationResponse()


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> VerifyEmailResponse:
    await auth_service.verify_email(request.token)
    return VerifyEmailResponse()
