from __future__ import annotations

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.dependencies import get_current_user
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5434/tsbl_test"


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    from app.core.security import create_access_token
    from app.modules.auth.domain.entities import User

    user = User(
        email="test@tsbl.com",
        username="testuser",
        password_hash="dummy",
    )
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(subject=str(user.id))

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    client.headers["Authorization"] = f"Bearer {token}"
    return client
