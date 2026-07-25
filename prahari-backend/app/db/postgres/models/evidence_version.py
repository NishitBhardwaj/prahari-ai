"""Evidence Version model — Evidence chain of custody and file versioning."""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres.engine import Base

class EvidenceVersion(Base):
    __tablename__ = "evidence_versions"

    version_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(50), ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    file_path: Mapped[str] = mapped_column(String(500), nullable=True) # Catalyst Stratus path
    file_hash: Mapped[str] = mapped_column(String(64), nullable=True) # SHA-256 Checksum
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    
    uploaded_by: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    remarks: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    evidence: Mapped["Evidence"] = relationship("Evidence", back_populates="versions", lazy="select")
