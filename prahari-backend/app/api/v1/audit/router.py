"""Audit trail API."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.postgres.session import get_async_session
from app.db.postgres.models.gang import AuditLog
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse

router = APIRouter()

@router.get("", summary="Get audit trail")
async def get_audit_logs(
    resource_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.AUDIT_READ)),
):
    query = select(AuditLog).order_by(desc(AuditLog.created_at))
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    query = query.limit(page_size).offset((page - 1) * page_size)
    result = await session.execute(query)
    logs = result.scalars().all()
    return ApiResponse.ok(data=[{
        "id": l.id, "user_id": l.user_id, "action": l.action,
        "resource_type": l.resource_type, "resource_id": l.resource_id,
        "created_at": l.created_at.isoformat(),
    } for l in logs])
