from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import MFAType
from app.core.config import settings
from app.core.logging import SecurityLogger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.domain.entities import Authentication, Session, User
from app.modules.auth.domain.events import (
    AllSessionsRevoked,
    EmailVerificationRequested,
    EmailVerified,
    MFAEnabled,
    MFADisabled,
    MFAVerified,
    PasswordChanged,
    PasswordResetCompleted,
    PasswordResetRequested,
    ProfileUpdated,
    SessionRevoked,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)
from app.modules.auth.domain.interfaces import EventPublisher, MFACodeGenerator, RateLimiter
from app.modules.auth.infrastructure.auth_repository import (
    AuthenticationRepository,
    SessionRepository,
    UserRepository,
)
from app.modules.auth.schemas.auth_schema import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.schemas.identity_schema import (
    MFAEnableResponse,
    MFAStatusResponse,
    SessionListResponse,
    SessionResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
)


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        event_publisher: EventPublisher,
        mfa_code_generator: MFACodeGenerator,
        rate_limiter: RateLimiter,
    ) -> None:
        self.db = db
        self.event_publisher = event_publisher
        self.mfa = mfa_code_generator
        self.rate_limiter = rate_limiter
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthenticationRepository(db)
        self.session_repo = SessionRepository(db)

    async def register(self, request: RegisterRequest) -> AuthResponse:
        existing_email = await self.user_repo.find_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        existing_username = await self.user_repo.find_by_username(request.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
            )

        if request.password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Passwords do not match"
            )

        password_hash_value = hash_password(request.password)

        user = User(
            id=uuid.uuid4(),
            email=request.email,
            username=request.username,
            password_hash=password_hash_value,
        )
        await self.user_repo.create(user)

        auth = Authentication(
            id=uuid.uuid4(),
            user_id=user.id,
            password_changed_at=datetime.now(timezone.utc),
        )
        await self.auth_repo.create(auth)

        tokens = await self._create_tokens(user)
        await self.event_publisher.publish(
            UserRegistered(user_id=str(user.id), email=user.email, username=user.username).event_name,
            {"user_id": str(user.id), "email": user.email, "username": user.username},
        )
        SecurityLogger.log(event="USER_REGISTERED", user_id=str(user.id))

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def login(self, request: LoginRequest, ip_address: str, user_agent: str | None = None) -> AuthResponse:
        if not await self.rate_limiter.check_rate_limit(
            f"login:{request.email}", 5, 300
        ):
            SecurityLogger.log(
                event="LOGIN_RATE_LIMIT_EXCEEDED",
                details={"email": request.email, "ip": ip_address},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )

        user = await self.user_repo.find_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        if user.status == "banned":
            SecurityLogger.log(event="BANNED_USER_LOGIN_ATTEMPT", user_id=str(user.id))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is banned"
            )

        if user.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked until {user.locked_until.isoformat()}",
            )

        if not verify_password(request.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.max_login_attempts:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.login_lockout_minutes
                )
                SecurityLogger.log(
                    event="ACCOUNT_LOCKED",
                    user_id=str(user.id),
                    details={"failed_attempts": user.failed_login_attempts},
                )
            await self.db.flush()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
            )

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_active_at = datetime.now(timezone.utc)
        await self.db.flush()

        auth = await self.auth_repo.find_by_user_id(user.id)
        if auth:
            auth.last_login_at = datetime.now(timezone.utc)
            await self.db.flush()

        tokens = await self._create_tokens(user, ip_address, user_agent)

        await self.event_publisher.publish(
            UserLoggedIn(user_id=str(user.id), ip_address=ip_address).event_name,
            {"user_id": str(user.id), "ip_address": ip_address},
        )
        SecurityLogger.log(event="USER_LOGIN_SUCCESS", user_id=str(user.id))

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            SecurityLogger.log(event="INVALID_REFRESH_TOKEN_ATTEMPT")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        user_id = uuid.UUID(sub)
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        if user.status in ("banned", "deleted"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not active"
            )

        return await self._create_tokens(user)

    async def logout(self, user_id: uuid.UUID, token_hash: str, session_id: uuid.UUID | None = None) -> None:
        if session_id:
            session = await self.session_repo.get(session_id)
        else:
            session = await self.session_repo.find_by_token_hash(token_hash)

        if not session:
            return

        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Session does not belong to user"
            )

        await self.session_repo.soft_delete(session.id)

        await self.event_publisher.publish(
            UserLoggedOut(user_id=str(user_id), session_id=str(session.id)).event_name,
            {"user_id": str(user_id), "session_id": str(session.id)},
        )

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        user_uuid = uuid.UUID(user_id)
        user = await self.user_repo.get(user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
            )

        user.password_hash = hash_password(new_password)
        await self.db.flush()

        await self.auth_repo.update_password_changed_at(user_uuid)
        await self.session_repo.revoke_user_sessions(user_uuid)

        await self.event_publisher.publish(
            PasswordChanged(user_id=user_id).event_name,
            {"user_id": user_id},
        )
        SecurityLogger.log(event="PASSWORD_CHANGED", user_id=user_id)

    async def forgot_password(self, email: str) -> None:
        user = await self.user_repo.find_by_email(email)
        if not user:
            return

        auth = await self.auth_repo.find_by_user_id(user.id)
        if not auth:
            return

        reset_token = create_access_token(
            subject=str(user.id),
            extra_claims={"purpose": "password_reset"},
        )
        auth.reset_token = reset_token
        auth.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.db.flush()

        await self.event_publisher.publish(
            PasswordResetRequested(user_id=str(user.id), email=user.email).event_name,
            {"user_id": str(user.id), "email": user.email},
        )

    async def reset_password(self, token: str, password: str, confirm_password: str) -> None:
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Passwords do not match"
            )

        payload = decode_token(token)
        if not payload or payload.get("purpose") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
            )

        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
            )

        user_id = uuid.UUID(sub)
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        auth = await self.auth_repo.find_by_user_id(user_id)
        if auth and auth.reset_token != token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
            )

        if auth and auth.reset_token_expires_at:
            if auth.reset_token_expires_at < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired"
                )

        user.password_hash = hash_password(password)
        await self.db.flush()

        if auth:
            auth.reset_token = None
            auth.reset_token_expires_at = None
            await self.db.flush()

        await self.session_repo.revoke_user_sessions(user_id)

        await self.event_publisher.publish(
            PasswordResetCompleted(user_id=str(user_id)).event_name,
            {"user_id": str(user_id)},
        )
        SecurityLogger.log(event="PASSWORD_RESET_COMPLETED", user_id=str(user_id))

    async def get_sessions(self, user_id: uuid.UUID, current_token_hash: str) -> SessionListResponse:
        sessions = await self.session_repo.find_active_by_user_id(user_id)
        session_list: list[SessionResponse] = []
        for s in sessions:
            session_list.append(
                SessionResponse(
                    id=str(s.id),
                    device_name=s.device_name,
                    device_id=s.device_id,
                    ip_address=s.ip_address,
                    location=s.location,
                    user_agent=s.user_agent,
                    is_current=s.token_hash == current_token_hash,
                    last_activity_at=s.last_activity_at,
                    created_at=s.created_at,
                    expires_at=s.expires_at,
                )
            )
        return SessionListResponse(sessions=session_list, total=len(session_list))

    async def revoke_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        session = await self.session_repo.get(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Session does not belong to user"
            )
        await self.session_repo.soft_delete(session.id)

        await self.event_publisher.publish(
            SessionRevoked(user_id=str(user_id), session_id=str(session_id)).event_name,
            {"user_id": str(user_id), "session_id": str(session_id)},
        )

    async def revoke_all_sessions_except(
        self, user_id: uuid.UUID, current_token_hash: str | None = None
    ) -> None:
        current_session_id: uuid.UUID | None = None
        if current_token_hash:
            current_session = await self.session_repo.find_by_token_hash(current_token_hash)
            if current_session:
                current_session_id = current_session.id

        sessions = await self.session_repo.find_active_by_user_id(user_id)
        for session in sessions:
            if current_session_id and session.id == current_session_id:
                continue
            await self.session_repo.soft_delete(session.id)

        await self.event_publisher.publish(
            AllSessionsRevoked(
                user_id=str(user_id),
                except_session_id=str(current_session_id) if current_session_id else None,
            ).event_name,
            {"user_id": str(user_id), "except_session_id": str(current_session_id) if current_session_id else None},
        )

    async def enable_mfa(self, user_id: uuid.UUID, mfa_type: str = "totp") -> MFAEnableResponse:
        auth = await self.auth_repo.find_by_user_id(user_id)
        if not auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Authentication record not found"
            )

        if auth.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="MFA is already enabled"
            )

        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        secret = self.mfa.generate_secret()
        qr_code_url = self.mfa.generate_qr_code_url(secret, user.email)
        backup_codes = self.mfa.generate_backup_codes(8)

        auth.mfa_secret = secret
        auth.mfa_type = MFAType(mfa_type)
        auth.mfa_backup_codes = {
            "codes": [{"code": bc, "used": False} for bc in backup_codes],
        }
        await self.db.flush()

        hashed_codes = [
            hashlib.sha256(bc.encode()).hexdigest() for bc in backup_codes
        ]
        auth.mfa_backup_codes = {
            "codes": [{"hash": hc, "used": False} for hc in hashed_codes],
        }
        await self.db.flush()

        return MFAEnableResponse(
            secret=secret,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes,
        )

    async def verify_mfa(self, user_id: uuid.UUID, code: str) -> None:
        auth = await self.auth_repo.find_by_user_id(user_id)
        if not auth or not auth.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not configured"
            )

        if not self.mfa.verify_code(auth.mfa_secret, code):
            if auth.mfa_backup_codes:
                code_hash = hashlib.sha256(code.encode()).hexdigest()
                for entry in auth.mfa_backup_codes.get("codes", []):
                    if entry.get("hash") == code_hash and not entry.get("used"):
                        entry["used"] = True
                        await self.db.flush()
                        auth.mfa_enabled = True
                        await self.db.flush()
                        await self.event_publisher.publish(
                            MFAVerified(user_id=str(user_id)).event_name,
                            {"user_id": str(user_id)},
                        )
                        return

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid verification code"
            )

        auth.mfa_enabled = True
        await self.db.flush()

        await self.event_publisher.publish(
            MFAEnabled(user_id=str(user_id), mfa_type=auth.mfa_type.value if auth.mfa_type else "totp").event_name,
            {"user_id": str(user_id), "mfa_type": str(auth.mfa_type.value) if auth.mfa_type else "totp"},
        )

    async def disable_mfa(self, user_id: uuid.UUID, code: str) -> None:
        auth = await self.auth_repo.find_by_user_id(user_id)
        if not auth or not auth.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled"
            )

        if auth.mfa_secret and not self.mfa.verify_code(auth.mfa_secret, code):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid verification code"
            )

        auth.mfa_enabled = False
        auth.mfa_secret = None
        auth.mfa_type = None
        auth.mfa_backup_codes = None
        await self.db.flush()

        await self.event_publisher.publish(
            MFADisabled(user_id=str(user_id)).event_name,
            {"user_id": str(user_id)},
        )

    async def get_mfa_status(self, user_id: uuid.UUID) -> MFAStatusResponse:
        auth = await self.auth_repo.find_by_user_id(user_id)
        if not auth:
            return MFAStatusResponse(mfa_enabled=False, mfa_type=None)
        return MFAStatusResponse(
            mfa_enabled=auth.mfa_enabled,
            mfa_type=auth.mfa_type.value if auth.mfa_type else None,
        )

    async def send_email_verification(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already verified"
            )

        auth = await self.auth_repo.find_by_user_id(user_id)
        if not auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Authentication record not found"
            )

        verification_token = create_access_token(
            subject=str(user.id),
            extra_claims={"purpose": "email_verification", "email": user.email},
        )
        auth.email_verification_token = verification_token
        auth.email_verification_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        await self.db.flush()

        await self.event_publisher.publish(
            EmailVerificationRequested(user_id=str(user.id), email=user.email).event_name,
            {"user_id": str(user.id), "email": user.email, "token": verification_token},
        )

    async def verify_email(self, token: str) -> None:
        payload = decode_token(token)
        if not payload or payload.get("purpose") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token"
            )

        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token"
            )

        user_id = uuid.UUID(sub)
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            return

        user.is_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        await self.db.flush()

        auth = await self.auth_repo.find_by_user_id(user_id)
        if auth:
            auth.email_verification_token = None
            auth.email_verification_expires_at = None
            await self.db.flush()

        await self.event_publisher.publish(
            EmailVerified(user_id=str(user.id), email=user.email).event_name,
            {"user_id": str(user.id), "email": user.email},
        )

    async def update_profile(
        self, user_id: uuid.UUID, request: UpdateProfileRequest
    ) -> UpdateProfileResponse:
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        changes: dict[str, Any] = {}

        if request.username is not None and request.username != user.username:
            existing = await self.user_repo.find_by_username(request.username)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
                )
            user.username = request.username
            changes["username"] = request.username

        if request.phone is not None and request.phone != user.phone:
            user.phone = request.phone
            changes["phone"] = request.phone

        if request.locale is not None:
            user.locale = request.locale
            changes["locale"] = request.locale

        if request.timezone is not None:
            user.timezone = request.timezone
            changes["timezone"] = request.timezone

        if changes:
            await self.db.flush()
            await self.event_publisher.publish(
                ProfileUpdated(user_id=str(user_id), changes=changes).event_name,
                {"user_id": str(user_id), "changes": changes},
            )

        return UpdateProfileResponse.model_validate(user)

    async def _create_tokens(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_id: str | None = None,
        device_name: str | None = None,
    ) -> TokenResponse:
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value if hasattr(user.role, "value") else user.role, "email": user.email},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        session = Session(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hashlib.sha256(access_token.encode()).hexdigest(),
            refresh_token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            device_name=device_name,
            last_activity_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.jwt_refresh_token_expire_days),
        )
        await self.session_repo.create(session)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_hash=session.token_hash,
            session_id=str(session.id),
        )
