"""
Base Pydantic models with audit trail fields.
Every entity in the simulation inherits from AuditModel.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class AuditModel(BaseModel):
    """
    Base model with enterprise audit trail fields.
    Every record in the Crime Simulation Laboratory inherits these fields
    for full traceability, versioning, and soft-delete support.
    """

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft-delete timestamp")
    modified_by: str = Field(default="system", description="User or system that last modified")
    record_version: int = Field(default=1, description="Record version number")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix (e.g., 'PER-', 'CASE-')."""
    uid = uuid4().hex[:12].upper()
    if prefix:
        return f"{prefix}{uid}"
    return uid
