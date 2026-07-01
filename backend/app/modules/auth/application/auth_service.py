import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.domain.entities import Authentication, Session, User
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


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthenticationRepository(db)
        self.session_repo = SessionRepository(db)

    async def register(self, request: RegisterRequest) -> AuthResponse:
        existing_email = await self.user_repo.find_by_email(request.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        existing_username = await self.user_repo.find_by_username(request.username)
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

        if request.password != request.confirm_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Passwords do not match")

        password_hash = hash_password(request.password)

        user = User(
            id=uuid.uuid4(),
            email=request.email,
            username=request.username,
            password_hash=password_hash,
        )
        await self.user_repo.create(user)

        auth = Authentication(
            id=uuid.uuid4(),
            user_id=user.id,
            password_changed_at=datetime.now(timezone.utc),
        )
        await self.auth_repo.create(auth)

        tokens = await self._create_tokens(user)
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def login(self, request: LoginRequest, ip_address: str) -> AuthResponse:
        user = await self.user_repo.find_by_email(request.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if user.status == "banned":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is banned")

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked until {user.locked_until.isoformat()}",
            )

        if not verify_password(request.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.max_login_attempts:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.login_lockout_minutes)
            await self.db.flush()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_active_at = datetime.now(timezone.utc)
        await self.db.flush()

        auth = await self.auth_repo.find_by_user_id(user.id)
        if auth:
            auth.last_login_at = datetime.now(timezone.utc)
            await self.db.flush()

        tokens = await self._create_tokens(user, ip_address)
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return await self._create_tokens(user)

    async def logout(self, user_id: str, token_hash: str):
        session = await self.session_repo.find_by_token_hash(token_hash)
        if session:
            await self.session_repo.soft_delete(session.id)

    async def change_password(self, user_id: str, current_password: str, new_password: str):
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        user.password_hash = hash_password(new_password)
        await self.db.flush()

        await self.session_repo.revoke_user_sessions(user_id)

    async def forgot_password(self, email: str):
        user = await self.user_repo.find_by_email(email)
        if not user:
            return

        auth = await self.auth_repo.find_by_user_id(user.id)
        if auth:
            reset_token = create_access_token(subject=str(user.id), extra_claims={"purpose": "password_reset"})
            auth.reset_token = reset_token
            auth.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            await self.db.flush()

    async def reset_password(self, token: str, password: str, confirm_password: str):
        if password != confirm_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Passwords do not match")

        payload = decode_token(token)
        if not payload or payload.get("purpose") != "password_reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

        user_id = payload.get("sub")
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.password_hash = hash_password(password)
        await self.db.flush()
        await self.session_repo.revoke_user_sessions(user_id)

    async def _create_tokens(self, user: User, ip_address: str | None = None) -> TokenResponse:
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role, "email": user.email},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        session = Session(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=access_token[-50:],
            refresh_token_hash=refresh_token[-50:],
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days),
        )
        await self.session_repo.create(session)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
