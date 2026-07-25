"""Case State Transition model — records the state machine transitions for a case."""

import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres.engine import Base

class CaseState(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    EVIDENCE_COLLECTION = "EVIDENCE_COLLECTION"
    CHARGESHEET_PREPARATION = "CHARGESHEET_PREPARATION"
    CHARGESHEET_FILED = "CHARGESHEET_FILED"
    COURT_PROCEEDINGS = "COURT_PROCEEDINGS"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"

class CaseStateTransition(Base):
    __tablename__ = "case_state_transitions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    
    from_state: Mapped[CaseState] = mapped_column(Enum(CaseState), nullable=True)
    to_state: Mapped[CaseState] = mapped_column(Enum(CaseState), nullable=False)
    
    changed_by_user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    remarks: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="state_transitions", lazy="select")
