"""
PostgreSQL Async Engine — SQLAlchemy 2.0 with asyncpg and PostGIS support.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from app.config import get_settings

settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── Declarative Base ──────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def init_db():
    """Create all tables (for dev). In production, use Alembic migrations."""
    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            # Import all models to ensure they're registered with Base.metadata
            from app.db.postgres.models import (  # noqa: F401
                user, case, person, accused, evidence, chargesheet,
                station, gang, case_relationship, case_state_transition,
                evidence_version, investigation_task, timeline_event
            )
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified.")


async def close_db():
    """Dispose the engine and close all connections."""
    await engine.dispose()
    logger.info("Database engine disposed.")
