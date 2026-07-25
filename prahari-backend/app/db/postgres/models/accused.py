"""Accused, Victim, Complainant, Witness ORM models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.postgres.engine import Base


class AccusedRecord(Base):
    __tablename__ = "accused_records"

    accused_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=False, index=True)
    arrest_status: Mapped[str] = mapped_column(String(50), nullable=True)  # Arrested / Absconding / Bailed
    arrest_date: Mapped[str] = mapped_column(String(30), nullable=True)
    is_habitual_offender: Mapped[bool] = mapped_column(Boolean, default=False)
    modus_operandi_id: Mapped[str] = mapped_column(String(50), nullable=True)
    gang_id: Mapped[str] = mapped_column(String(50), ForeignKey("gangs.gang_id"), nullable=True, index=True)
    role_in_crime: Mapped[str] = mapped_column(String(100), nullable=True)  # Principal / Accomplice

    # AI Labels
    label_repeat_offender: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    label_is_gang_related: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # Risk scores (populated by AI engine)
    violence_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    flight_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_explainability: Mapped[dict] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    case: Mapped["Case"] = relationship("Case", back_populates="accused_records")
    person: Mapped["Person"] = relationship("Person")
    gang: Mapped["Gang"] = relationship("Gang", foreign_keys=[gang_id])


class Victim(Base):
    __tablename__ = "victims"

    victim_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=False, index=True)
    injury_type: Mapped[str] = mapped_column(String(50), nullable=True)  # None / Minor / Grievous / Fatal
    victim_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Individual / Organization
    description: Mapped[str] = mapped_column(Text, nullable=True)
    medical_report_url: Mapped[str] = mapped_column(String(500), nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="victims")
    person: Mapped["Person"] = relationship("Person")


class Complainant(Base):
    __tablename__ = "complainants"

    complainant_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=False, index=True)
    complainant_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Victim / Third Party / Officer
    complaint_text: Mapped[str] = mapped_column(Text, nullable=True)
    signature_url: Mapped[str] = mapped_column(String(500), nullable=True)

    case: Mapped["Case"] = relationship("Case", back_populates="complainants")
    person: Mapped["Person"] = relationship("Person")


class Witness(Base):
    __tablename__ = "witnesses"

    witness_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=False, index=True)
    witness_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Eye Witness / Character / Expert
    statement: Mapped[str] = mapped_column(Text, nullable=True)
    statement_date: Mapped[str] = mapped_column(String(30), nullable=True)
    is_hostile: Mapped[bool] = mapped_column(Boolean, default=False)

    case: Mapped["Case"] = relationship("Case", back_populates="witnesses")
    person: Mapped["Person"] = relationship("Person")
