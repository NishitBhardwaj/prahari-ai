"""Evidence and Investigation Diary ORM models."""

from datetime import date, datetime, timezone
from sqlalchemy import String, Float, Boolean, Date, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.postgres.engine import Base


class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)       # Physical / Digital / Biological / Financial
    sub_category: Mapped[str] = mapped_column(String(100), nullable=True)   # Weapon / Narcotics / Device / Document
    description: Mapped[str] = mapped_column(Text, nullable=True)
    seizure_date: Mapped[date] = mapped_column(Date, nullable=True)
    seizure_location: Mapped[str] = mapped_column(String(500), nullable=True)
    seized_by_officer_id: Mapped[str] = mapped_column(String(50), ForeignKey("employees.employee_id"), nullable=True)
    chain_of_custody: Mapped[dict] = mapped_column(JSONB, nullable=True)     # Audit trail of handlers
    fsl_report_id: Mapped[str] = mapped_column(String(50), nullable=True)
    storage_location: Mapped[str] = mapped_column(String(200), nullable=True)
    media_url: Mapped[str] = mapped_column(String(500), nullable=True)       # Photo of the evidence
    is_produced_in_court: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ────────────────────────────────────────────────────
    case: Mapped["Case"] = relationship("Case", back_populates="evidence_items", lazy="select")
    versions: Mapped[list["EvidenceVersion"]] = relationship("EvidenceVersion", back_populates="evidence", lazy="select")


class FSLReport(Base):
    __tablename__ = "fsl_reports"

    report_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(50), ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)   # Ballistics / Digital / Biological
    findings: Mapped[str] = mapped_column(Text, nullable=True)
    result_status: Mapped[str] = mapped_column(String(50), nullable=True)   # Positive / Negative / Inconclusive
    submitted_date: Mapped[date] = mapped_column(Date, nullable=True)
    received_date: Mapped[date] = mapped_column(Date, nullable=True)
    examiner_name: Mapped[str] = mapped_column(String(200), nullable=True)
    report_url: Mapped[str] = mapped_column(String(500), nullable=True)


class InvestigationDiary(Base):
    __tablename__ = "investigation_diaries"

    diary_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    officer_id: Mapped[str] = mapped_column(String(50), ForeignKey("employees.employee_id"), nullable=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    entry_time: Mapped[str] = mapped_column(String(10), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    case: Mapped["Case"] = relationship("Case", back_populates="investigation_diaries")


class CrimeEvent(Base):
    __tablename__ = "crime_events"

    event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    event_time: Mapped[str] = mapped_column(String(10), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="crime_events")
