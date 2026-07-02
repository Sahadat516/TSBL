from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.base_repository import BaseRepository
from app.modules.auth.domain.entities import Authentication, Session, User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, User)

    async def find_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_by_id_with_auth(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.authentication))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()


class AuthenticationRepository(BaseRepository[Authentication]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Authentication)

    async def find_by_user_id(self, user_id: uuid.UUID) -> Authentication | None:
        result = await self.db.execute(
            select(Authentication).where(
                Authentication.user_id == user_id,
                Authentication.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def update_password_changed_at(self, user_id: uuid.UUID) -> None:
        stmt = (
            sa_update(Authentication)
            .where(Authentication.user_id == user_id)
            .values(password_changed_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.flush()


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Session)

    async def find_by_token_hash(self, token_hash: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(
                Session.token_hash == token_hash,
                Session.is_revoked.is_(False),
                Session.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def find_active_by_user_id(self, user_id: uuid.UUID) -> list[Session]:
        result = await self.db.execute(
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.is_revoked.is_(False),
                Session.deleted_at.is_(None),
                Session.expires_at > datetime.now(timezone.utc),
            )
            .order_by(Session.last_activity_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def revoke_user_sessions(self, user_id: uuid.UUID) -> None:
        stmt = (
            sa_update(Session)
            .where(Session.user_id == user_id, Session.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.flush()
