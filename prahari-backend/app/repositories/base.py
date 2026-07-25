"""
Generic async repository base class.
Provides standard CRUD operations for all domain entities.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.engine import Base
from app.core.exceptions import NotFoundError, DatabaseError
from loguru import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id_value: Any, id_column: str = None) -> ModelType:
        """Retrieve a single record by primary key. Raises NotFoundError if missing."""
        col_name = id_column or f"{self.model.__tablename__[:-1]}_id"
        col = getattr(self.model, col_name, None)
        if col is None:
            # Fallback: try first primary key column
            pk_cols = [c for c in self.model.__table__.primary_key]
            if pk_cols:
                col = getattr(self.model, pk_cols[0].name)
            else:
                raise DatabaseError(f"Cannot determine PK for {self.model.__name__}")

        result = await self.session.execute(select(self.model).where(col == id_value))
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundError(resource=self.model.__name__, identifier=id_value)
        return obj

    async def list(
        self,
        filters: Optional[List] = None,
        order_by: Optional[Any] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> tuple[List[ModelType], int]:
        """Return a paginated list of records and total count."""
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if filters:
            for f in filters:
                query = query.where(f)
                count_query = count_query.where(f)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record from a dict of field values."""
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id_value: Any, data: Dict[str, Any], id_column: str = None) -> ModelType:
        """Update a record by ID."""
        obj = await self.get_by_id(id_value, id_column)
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id_value: Any, id_column: str = None) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        obj = await self.get_by_id(id_value, id_column)
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def exists(self, **kwargs) -> bool:
        """Check if a record exists with the given field values."""
        query = select(func.count()).select_from(self.model)
        for field, value in kwargs.items():
            col = getattr(self.model, field, None)
            if col is not None:
                query = query.where(col == value)
        result = await self.session.execute(query)
        return result.scalar_one() > 0
