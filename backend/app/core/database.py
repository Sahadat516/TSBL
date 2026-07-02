from __future__ import annotations

from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug,
    hide_parameters=not settings.debug,
)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

redis_pool: ConnectionPool | None = None


class Base(DeclarativeBase):
    pass


async def get_redis() -> Redis:
    global redis_pool
    if redis_pool is None:
        redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=50,
            decode_responses=True,
        )
    return Redis(connection_pool=redis_pool)


async def close_redis() -> None:
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
