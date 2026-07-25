"""Case Relationship model — relational backing for Neo4j edges between cases."""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres.engine import Base

class CaseRelationship(Base):
    __tablename__ = "case_relationships"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    source_case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    target_case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False) # 'SIMILAR_MO', 'SHARED_ACCUSED', 'GEOGRAPHIC_PROXIMITY'
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True) # Used for AI-detected similarity (0.0 to 1.0)
    
    detected_by: Mapped[str] = mapped_column(String(50), nullable=False) # 'SYSTEM' or employee_id for manual
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    source_case: Mapped["Case"] = relationship("Case", foreign_keys=[source_case_id], back_populates="outgoing_relationships", lazy="select")
    target_case: Mapped["Case"] = relationship("Case", foreign_keys=[target_case_id], back_populates="incoming_relationships", lazy="select")
