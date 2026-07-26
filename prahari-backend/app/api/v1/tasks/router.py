from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.db.postgres.session import get_async_session
from app.core.auth import get_current_user
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse
from app.db.postgres.models import InvestigationTask, TaskStatus, TaskPriority, TimelineEvent
import uuid

router = APIRouter()

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    remarks: Optional[str] = None
    assigned_to_id: Optional[str] = None

@router.get("/case/{case_id}", summary="Get all tasks for a case")
async def get_case_tasks(
    case_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_READ)),
):
    result = await session.execute(
        select(InvestigationTask).where(InvestigationTask.case_id == case_id)
    )
    tasks = result.scalars().all()
    
    return ApiResponse.ok(data=[{
        "task_id": t.task_id,
        "case_id": t.case_id,
        "task_type": t.task_type,
        "title": t.title,
        "description": t.description,
        "priority": t.priority.value if hasattr(t.priority, "value") else t.priority,
        "status": t.status.value if hasattr(t.status, "value") else t.status,
        "assigned_to_id": t.assigned_to_id,
        "assigned_by_id": t.assigned_by_id,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "remarks": t.remarks,
        "created_at": t.created_at.isoformat() if t.created_at else None
    } for t in tasks])


@router.patch("/{task_id}", summary="Update task status (Kanban drag)")
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_MANAGE)),
):
    result = await session.execute(
        select(InvestigationTask).where(InvestigationTask.task_id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = task.status
    
    update_data = payload.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED.value:
        update_data["completed_at"] = datetime.now(timezone.utc)
        
    await session.execute(
        update(InvestigationTask).where(InvestigationTask.task_id == task_id).values(**update_data)
    )
    
    # Log to Universal Timeline if status changed
    if "status" in update_data and update_data["status"] != old_status:
        event = TimelineEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:12]}",
            case_id=task.case_id,
            event_type="TASK_UPDATED",
            title=f"Task Status Updated: {task.title}",
            description=f"Moved from {old_status} to {update_data['status']}",
            actor_id=current_user.id,
            actor_name=current_user.full_name
        )
        session.add(event)

    await session.commit()
    return ApiResponse.ok(message="Task updated successfully")
