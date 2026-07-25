"""Cases API — full CRUD, progressive drafts, timeline engine, and search."""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.postgres.session import get_async_session
from app.repositories.case_repository import CaseRepository
from app.workflows.fir_registration import FIRRegistrationWorkflow
from app.core.auth import get_current_user
from app.core.permissions import require_permissions, Permission
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.response import ApiResponse
from app.config import get_settings
from app.api.v1.cases.schemas import (
    DraftCaseCreate, DraftCaseResponse, CaseUpdate, VictimCreate, AccusedCreate,
    TimelineEventResponse
)
from app.db.postgres.models import CaseState, TaskStatus, TaskPriority
from app.workflows.ai_worker import async_sync_case_to_graph, async_calculate_risk_score

router = APIRouter()
settings = get_settings()


@router.post("/draft", summary="Initialize a Draft FIR", status_code=201)
async def create_draft_fir(
    payload: DraftCaseCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_CREATE)),
):
    """
    Step 1 of the progressive FIR wizard.
    Creates a new case with status DRAFT.
    """
    case_id = f"FIR_{uuid.uuid4().hex[:8].upper()}"
    fir_number = f"DRAFT/{payload.year}/{case_id[-4:]}"
    
    from app.db.postgres.models import Case, TimelineEvent
    new_case = Case(
        case_id=case_id,
        fir_number=fir_number,
        station_id=payload.station_id,
        station_name=payload.station_name,
        district_id=payload.district_id,
        date_of_report=payload.date_of_report,
        year=payload.year,
        current_state=CaseState.DRAFT,
        created_by=current_user.id
    )
    session.add(new_case)
    
    # Universal Timeline Event
    event = TimelineEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        event_type="FIR_DRAFT_CREATED",
        title="FIR Draft Initialized",
        actor_id=current_user.id,
        actor_name=current_user.full_name
    )
    session.add(event)
    await session.commit()
    
    return ApiResponse.ok(
        data=DraftCaseResponse(
            case_id=case_id,
            fir_number=fir_number,
            current_state=CaseState.DRAFT.value
        ).model_dump(),
        message="Draft FIR created."
    )


@router.patch("/{case_id}", summary="Update a draft case (Autosave)")
async def update_draft_case(
    case_id: str,
    payload: CaseUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_UPDATE)),
):
    """Autosave endpoint for updating Incident Details, Location, etc."""
    repo = CaseRepository(session)
    case = await repo.get_by_id(case_id, id_column="case_id")
    
    if not case:
        raise NotFoundError("Case not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return ApiResponse.ok(data=_case_to_dict(case))
        
    case = await repo.update(case_id, update_data, id_column="case_id")
    return ApiResponse.ok(data=_case_to_dict(case), message="Case updated.")


@router.post("/{case_id}/victims", summary="Add a victim to a case")
async def add_case_victim(
    case_id: str,
    payload: VictimCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_UPDATE)),
):
    """Add a victim. Triggers background duplication check and timeline event."""
    from app.db.postgres.models import Victim, TimelineEvent
    repo = CaseRepository(session)
    case = await repo.get_by_id(case_id, id_column="case_id")
    if not case:
        raise NotFoundError("Case not found")
        
    victim = Victim(
        victim_id=f"VIC_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        gender=payload.gender,
        age=payload.age,
        injury_type=payload.injury_type
    )
    session.add(victim)
    
    event = TimelineEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        event_type="VICTIM_ADDED",
        title=f"Victim Added: {payload.first_name}",
        actor_id=current_user.id,
        actor_name=current_user.full_name
    )
    session.add(event)
    await session.commit()
    
    # Trigger background AI workflows
    background_tasks.add_task(async_sync_case_to_graph, case_id)
    background_tasks.add_task(async_calculate_risk_score, case_id)
    
    return ApiResponse.ok(data={"victim_id": victim.victim_id}, message="Victim added successfully.")


@router.post("/{case_id}/accused", summary="Add an accused to a case")
async def add_case_accused(
    case_id: str,
    payload: AccusedCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_UPDATE)),
):
    """Add an accused. Triggers background duplication check and timeline event."""
    from app.db.postgres.models import AccusedRecord, TimelineEvent
    repo = CaseRepository(session)
    case = await repo.get_by_id(case_id, id_column="case_id")
    if not case:
        raise NotFoundError("Case not found")
        
    accused = AccusedRecord(
        accused_id=f"ACC_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        gender=payload.gender,
        age=payload.age,
        is_arrested=payload.is_arrested
    )
    session.add(accused)
    
    event = TimelineEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        event_type="ACCUSED_ADDED",
        title=f"Accused Added: {payload.first_name}",
        actor_id=current_user.id,
        actor_name=current_user.full_name
    )
    session.add(event)
    await session.commit()
    
    # Trigger AI workflows
    background_tasks.add_task(async_sync_case_to_graph, case_id)
    background_tasks.add_task(async_calculate_risk_score, case_id)
    
    return ApiResponse.ok(data={"accused_id": accused.accused_id}, message="Accused added successfully.")


@router.get("/{case_id}/timeline", summary="Get Universal Case Timeline")
async def get_universal_timeline(
    case_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_READ)),
):
    """Retrieve all universal timeline events in chronological order."""
    from sqlalchemy import select
    from app.db.postgres.models import TimelineEvent
    
    result = await session.execute(
        select(TimelineEvent)
        .where(TimelineEvent.case_id == case_id)
        .order_by(TimelineEvent.timestamp)
    )
    events = result.scalars().all()
    
    data = [
        TimelineEventResponse(
            event_id=e.event_id,
            case_id=e.case_id,
            event_type=e.event_type,
            title=e.title,
            description=e.description,
            actor_name=e.actor_name,
            timestamp=e.timestamp.isoformat()
        ).model_dump()
        for e in events
    ]
    return ApiResponse.ok(data=data)


@router.post("/{case_id}/tasks", summary="Create an investigation task")
async def create_investigation_task(
    case_id: str,
    payload: dict,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_WRITE)),
):
    """Create a new task in the Investigation Workspace."""
    from app.db.postgres.models import InvestigationTask, TimelineEvent
    repo = CaseRepository(session)
    case = await repo.get_by_id(case_id, id_column="case_id")
    if not case:
        raise NotFoundError("Case not found")
        
    task_id = f"TSK_{uuid.uuid4().hex[:12]}"
    task = InvestigationTask(
        task_id=task_id,
        case_id=case_id,
        task_type=payload.get("task_type"),
        title=payload.get("title"),
        description=payload.get("description"),
        priority=TaskPriority(payload.get("priority", "MEDIUM")),
        assigned_to_id=payload.get("assigned_to_id"),
        assigned_by_id=current_user.id
    )
    session.add(task)
    
    event = TimelineEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        event_type="TASK_CREATED",
        title=f"Task Assigned: {task.title}",
        actor_id=current_user.id,
        actor_name=current_user.full_name
    )
    session.add(event)
    await session.commit()
    
    return ApiResponse.ok(data={"task_id": task_id}, message="Task created.")


@router.get("", summary="List cases with search and filter")
async def list_cases(
    q: Optional[str] = Query(None, description="Search FIR number, crime, place"),
    district_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None),
    crime_head: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    is_gang_related: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_READ)),
):
    """Paginated case list with full-text search and filtering."""
    repo = CaseRepository(session)
    offset = (page - 1) * page_size
    cases, total = await repo.search(
        q=q, district_id=district_id, station_id=station_id,
        crime_head=crime_head, status=status, year=year,
        date_from=date_from, date_to=date_to,
        is_gang_related=is_gang_related, limit=page_size, offset=offset,
    )
    return ApiResponse.paginated(data=[_case_to_dict(c) for c in cases], total=total, page=page, page_size=page_size)


@router.get("/{case_id}", summary="Get full case detail")
async def get_case(
    case_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_READ)),
):
    repo = CaseRepository(session)
    case = await repo.get_by_id(case_id, id_column="case_id")
    return ApiResponse.ok(data=_case_to_dict(case))


def _case_to_dict(case) -> dict:
    return {
        "case_id": case.case_id,
        "fir_number": case.fir_number,
        "station_id": case.station_id,
        "station_name": case.station_name,
        "district_id": case.district_id,
        "crime_head_name": case.crime_head_name,
        "crime_sub_head_name": case.crime_sub_head_name,
        "date_of_report": str(case.date_of_report),
        "current_state": case.current_state.value if hasattr(case.current_state, "value") else case.current_state,
        "is_sensitive": case.is_sensitive,
        "place_of_occurrence": case.place_of_occurrence,
        "latitude": case.latitude,
        "longitude": case.longitude,
        "investigating_officer_id": case.investigating_officer_id,
        "year": case.year,
        "label_is_solved": case.label_is_solved,
        "label_is_gang_related": case.label_is_gang_related,
        "label_is_cyber": case.label_is_cyber,
        "ai_risk_score": case.ai_risk_score,
        "ai_severity_label": case.ai_severity_label,
        "created_at": case.created_at.isoformat() if case.created_at else None,
    }
