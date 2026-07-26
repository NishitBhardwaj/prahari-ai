from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from app.db.postgres.session import get_async_session
from app.core.auth import get_current_user
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse
from app.db.postgres.models import Evidence, EvidenceVersion, TimelineEvent, Case

router = APIRouter()

class EvidenceCreate(BaseModel):
    evidence_type: str
    description: Optional[str] = None
    location_found: Optional[str] = None

@router.get("/case/{case_id}", summary="Get evidence for a case")
async def get_case_evidence(
    case_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_READ)),
):
    """Retrieve all evidence items along with their chain-of-custody versions."""
    from sqlalchemy.orm import selectinload
    
    result = await session.execute(
        select(Evidence)
        .where(Evidence.case_id == case_id)
        .options(selectinload(Evidence.versions))
    )
    evidence_list = result.scalars().all()
    
    data = []
    for ev in evidence_list:
        data.append({
            "evidence_id": ev.evidence_id,
            "evidence_number": ev.evidence_number,
            "evidence_type": ev.evidence_type,
            "description": ev.description,
            "location_found": ev.location_found,
            "seized_by": ev.seized_by,
            "seizure_date": ev.seizure_date.isoformat() if ev.seizure_date else None,
            "versions": [
                {
                    "version_number": v.version_number,
                    "file_path": v.file_path,
                    "uploaded_by": v.uploaded_by,
                    "uploaded_at": v.uploaded_at.isoformat() if v.uploaded_at else None,
                    "remarks": v.remarks
                }
                for v in ev.versions
            ]
        })
        
    return ApiResponse.ok(data=data)

@router.post("/case/{case_id}", summary="Add new evidence record")
async def add_evidence(
    case_id: str,
    payload: EvidenceCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_MANAGE)),
):
    """Logs a new piece of evidence and adds a timeline event."""
    evidence_id = f"EVD_{uuid.uuid4().hex[:12]}"
    
    # Auto-generate evidence number
    result = await session.execute(select(Case).where(Case.case_id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Example num: FIR/2026/001-EV01
    ev_num = f"{case.fir_number}-EVD-{uuid.uuid4().hex[:4].upper()}"
    
    new_ev = Evidence(
        evidence_id=evidence_id,
        case_id=case_id,
        evidence_number=ev_num,
        evidence_type=payload.evidence_type,
        description=payload.description,
        location_found=payload.location_found,
        seized_by=current_user.id
    )
    session.add(new_ev)
    
    event = TimelineEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        event_type="EVIDENCE_ADDED",
        title=f"Evidence Logged: {ev_num}",
        description=payload.description,
        actor_id=current_user.id,
        actor_name=current_user.full_name
    )
    session.add(event)
    
    await session.commit()
    return ApiResponse.ok(data={"evidence_id": evidence_id}, message="Evidence logged")

@router.post("/{evidence_id}/versions", summary="Upload evidence file/version")
async def upload_evidence_version(
    evidence_id: str,
    file: UploadFile = File(...),
    remarks: str = Form(None),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.INVESTIGATION_MANAGE)),
):
    """Chain of Custody: Append a new version of the file (e.g. enhanced image, signed report)."""
    result = await session.execute(select(Evidence).where(Evidence.evidence_id == evidence_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    # Get max version
    v_result = await session.execute(
        select(EvidenceVersion).where(EvidenceVersion.evidence_id == evidence_id)
    )
    versions = v_result.scalars().all()
    next_version = len(versions) + 1
    
    # Mock file upload to Stratus storage
    file_path = f"stratus/cases/{ev.case_id}/evidence/{evidence_id}_v{next_version}_{file.filename}"
    
    new_version = EvidenceVersion(
        version_id=f"EVV_{uuid.uuid4().hex[:12]}",
        evidence_id=evidence_id,
        version_number=next_version,
        file_path=file_path,
        uploaded_by=current_user.id,
        remarks=remarks
    )
    session.add(new_version)
    
    event = TimelineEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        case_id=ev.case_id,
        event_type="EVIDENCE_VERSION_ADDED",
        title=f"Evidence Version {next_version} Uploaded",
        description=f"File: {file.filename}",
        actor_id=current_user.id,
        actor_name=current_user.full_name
    )
    session.add(event)
    
    await session.commit()
    return ApiResponse.ok(message=f"Version {next_version} uploaded")
