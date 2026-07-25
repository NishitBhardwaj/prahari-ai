"""Case (FIR) ORM model — the central entity of Prahari AI."""

import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Float, Boolean, Date, DateTime, Text, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry

from app.db.postgres.engine import Base
from app.db.postgres.models.case_state_transition import CaseState


class Case(Base):
    __tablename__ = "cases"

    # ── Identity ────────────────────────────────────────────────────────
    case_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    fir_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # ── Station / District ───────────────────────────────────────────────
    station_id: Mapped[str] = mapped_column(String(50), ForeignKey("police_stations.station_id"), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    district_id: Mapped[str] = mapped_column(String(50), ForeignKey("districts.district_id"), nullable=False, index=True)

    # ── Crime Classification ─────────────────────────────────────────────
    crime_head_id: Mapped[str] = mapped_column(String(50), nullable=False)
    crime_head_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    crime_sub_head_id: Mapped[str] = mapped_column(String(50), nullable=True)
    crime_sub_head_name: Mapped[str] = mapped_column(String(200), nullable=True)

    # ── Dates & Times ────────────────────────────────────────────────────
    date_of_report: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    time_of_report: Mapped[str] = mapped_column(String(10), nullable=True)
    date_of_incident_start: Mapped[date] = mapped_column(Date, nullable=False)
    time_of_incident_start: Mapped[str] = mapped_column(String(10), nullable=True)
    date_of_incident_end: Mapped[date] = mapped_column(Date, nullable=True)
    time_of_incident_end: Mapped[str] = mapped_column(String(10), nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # ── Location ─────────────────────────────────────────────────────────
    place_of_occurrence: Mapped[str] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    location: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    distance_from_station_km: Mapped[float] = mapped_column(Float, nullable=True)
    direction_from_station: Mapped[str] = mapped_column(String(20), nullable=True)

    # ── Status ───────────────────────────────────────────────────────────
    status_id: Mapped[str] = mapped_column(String(50), nullable=True)
    status_name: Mapped[str] = mapped_column(String(100), nullable=True, index=True) # Retained for legacy/dataset compatibility
    current_state: Mapped[CaseState] = mapped_column(Enum(CaseState), default=CaseState.DRAFT, index=True)
    is_final_status: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Investigation ─────────────────────────────────────────────────────
    investigating_officer_id: Mapped[str] = mapped_column(String(50), ForeignKey("employees.employee_id"), nullable=True)

    # ── AI Labels (Ground Truth) ─────────────────────────────────────────
    label_is_solved: Mapped[bool] = mapped_column(Boolean, nullable=True)
    label_is_gang_related: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    label_is_cyber: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # ── Explainability Metadata ──────────────────────────────────────────
    explainability_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True)
    ai_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    ai_severity_label: Mapped[str] = mapped_column(String(20), nullable=True)  # HIGH / MEDIUM / LOW

    # ── Audit ────────────────────────────────────────────────────────────
    created_by: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ────────────────────────────────────────────────────
    accused_records: Mapped[list["AccusedRecord"]] = relationship("AccusedRecord", back_populates="case", lazy="select")
    victims: Mapped[list["Victim"]] = relationship("Victim", back_populates="case", lazy="select")
    complainants: Mapped[list["Complainant"]] = relationship("Complainant", back_populates="case", lazy="select")
    witnesses: Mapped[list["Witness"]] = relationship("Witness", back_populates="case", lazy="select")
    evidence_items: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="case", lazy="select")
    investigation_diaries: Mapped[list["InvestigationDiary"]] = relationship("InvestigationDiary", back_populates="case", lazy="select")
    crime_events: Mapped[list["CrimeEvent"]] = relationship("CrimeEvent", back_populates="case", lazy="select")
    chargesheet: Mapped["Chargesheet"] = relationship("Chargesheet", back_populates="case", uselist=False, lazy="select")
    court_proceedings: Mapped[list["CourtProceeding"]] = relationship("CourtProceeding", back_populates="case", lazy="select")
    narrative_documents: Mapped[list["NarrativeDocument"]] = relationship("NarrativeDocument", back_populates="case", lazy="select")
    
    # New Backend v1.1 Relationships
    state_transitions: Mapped[list["CaseStateTransition"]] = relationship("CaseStateTransition", back_populates="case", lazy="select")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship("TimelineEvent", back_populates="case", lazy="select")
    tasks: Mapped[list["InvestigationTask"]] = relationship("InvestigationTask", back_populates="case", lazy="select")
    outgoing_relationships: Mapped[list["CaseRelationship"]] = relationship("CaseRelationship", foreign_keys="CaseRelationship.source_case_id", back_populates="source_case", lazy="select")
    incoming_relationships: Mapped[list["CaseRelationship"]] = relationship("CaseRelationship", foreign_keys="CaseRelationship.target_case_id", back_populates="target_case", lazy="select")
