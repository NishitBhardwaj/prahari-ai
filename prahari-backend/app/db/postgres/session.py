"""
Database session dependency for FastAPI routes.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.engine import AsyncSessionFactory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
