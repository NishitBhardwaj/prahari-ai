"""Investigation Task model — Task management module for cases."""

import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres.engine import Base

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class InvestigationTask(Base):
    __tablename__ = "investigation_tasks"

    task_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    
    task_type: Mapped[str] = mapped_column(String(100), nullable=False) # 'WITNESS_INTERVIEW', 'CCTV_COLLECTION', 'FORENSIC_EXAM'
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO)
    
    assigned_to_id: Mapped[str] = mapped_column(String(50), ForeignKey("employees.employee_id"), nullable=True)
    assigned_by_id: Mapped[str] = mapped_column(String(50), nullable=False)
    
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    remarks: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="tasks", lazy="select")
