"""
Async PostgreSQL database connection using SQLAlchemy 2.0 + asyncpg.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config.settings import get_settings

settings = get_settings()

engine: AsyncEngine | None = None
async_session_factory: sessionmaker | None = None


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    global engine, async_session_factory
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(
        db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=settings.DEBUG,
    )
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_session() -> AsyncSession:
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with async_session_factory() as session:
        yield session
