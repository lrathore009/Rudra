"""Application lifecycle and dependency injection."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from rudra.core.config import get_settings
from rudra.core.logging import get_logger, setup_logging

logger = get_logger(__name__)

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        url = settings.database_url
        connect_args: dict = {}
        # Supabase (and most hosted Postgres) require SSL; asyncpg needs this explicitly.
        if "supabase.co" in url or "supabase.com" in url:
            connect_args["ssl"] = "require"
            # Supabase poolers run pgbouncer in transaction mode → disable prepared-stmt cache.
            connect_args["statement_cache_size"] = 0
        _engine = create_async_engine(
            url,
            echo=settings.rudra_env == "development",
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.rudra_env)
    logger.info("rudra_starting", env=settings.rudra_env)

    # Initialize connections
    get_engine()

    yield

    if _engine:
        await _engine.dispose()
    logger.info("rudra_shutdown")
