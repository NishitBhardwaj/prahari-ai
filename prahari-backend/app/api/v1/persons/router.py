"""Persons API — manage person records."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.postgres.session import get_async_session
from app.db.postgres.models.person import Person
from app.repositories.base import BaseRepository
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse

router = APIRouter()

@router.get("", summary="Search persons")
async def list_persons(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.PERSON_READ)),
):
    repo = BaseRepository(Person, session)
    filters = []
    if q:
        filters.append(or_(
            Person.full_name.ilike(f"%{q}%"),
            Person.phone_primary.ilike(f"%{q}%"),
            Person.aadhaar_number.ilike(f"%{q}%"),
        ))
    persons, total = await repo.list(filters=filters, limit=page_size, offset=(page-1)*page_size)
    return ApiResponse.paginated(
        data=[{"person_id": p.person_id, "full_name": p.full_name, "phone": p.phone_primary,
               "city": p.city, "age": p.age, "gender": p.gender} for p in persons],
        total=total, page=page, page_size=page_size
    )

@router.get("/{person_id}", summary="Get person detail")
async def get_person(
    person_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.PERSON_READ)),
):
    repo = BaseRepository(Person, session)
    p = await repo.get_by_id(person_id, id_column="person_id")
    return ApiResponse.ok(data={k: getattr(p, k, None) for k in Person.__table__.columns.keys()})
