"""Timeline Event model — the Universal Timeline Engine for a case."""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.postgres.engine import Base

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., 'FIR_DRAFT_CREATED', 'EVIDENCE_UPLOADED', 'AI_SCORE_UPDATED'
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Context (who/what caused it)
    actor_id: Mapped[str] = mapped_column(String(50), nullable=True)  # User ID or 'SYSTEM'
    actor_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Optional metadata linking to specific entities (e.g., {"victim_id": "V123", "evidence_id": "E456"})
    metadata_payload: Mapped[dict] = mapped_column(JSONB, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="timeline_events", lazy="select")
