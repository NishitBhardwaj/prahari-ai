"""Chargesheet and Court Proceeding ORM models."""

from datetime import date, datetime, timezone
from sqlalchemy import String, Float, Boolean, Date, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.postgres.engine import Base


class Chargesheet(Base):
    __tablename__ = "chargesheet_details"

    chargesheet_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, unique=True, index=True)
    chargesheet_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    filing_date: Mapped[date] = mapped_column(Date, nullable=True)
    investigating_officer_id: Mapped[str] = mapped_column(String(50), ForeignKey("employees.employee_id"), nullable=True)
    court_id: Mapped[str] = mapped_column(String(50), ForeignKey("courts.court_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=True)  # Accepted / Returned / Pending
    sections_invoked: Mapped[dict] = mapped_column(JSONB, nullable=True)
    document_url: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    case: Mapped["Case"] = relationship("Case", back_populates="chargesheet")


class Court(Base):
    __tablename__ = "courts"

    court_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    court_name: Mapped[str] = mapped_column(String(200), nullable=False)
    court_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Sessions / Magistrate / High Court
    district_id: Mapped[str] = mapped_column(String(50), ForeignKey("districts.district_id"), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    judge_name: Mapped[str] = mapped_column(String(200), nullable=True)


class CourtProceeding(Base):
    __tablename__ = "court_proceedings"

    proceeding_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    court_id: Mapped[str] = mapped_column(String(50), ForeignKey("courts.court_id"), nullable=True)
    hearing_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    proceeding_type: Mapped[str] = mapped_column(String(100), nullable=True)  # Evidence / Cross Exam / Judgment
    next_hearing_date: Mapped[date] = mapped_column(Date, nullable=True)
    judge_name: Mapped[str] = mapped_column(String(200), nullable=True)
    prosecutor_name: Mapped[str] = mapped_column(String(200), nullable=True)
    defense_counsel_name: Mapped[str] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=True)  # Adjourned / Judgement / Disposed
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    case: Mapped["Case"] = relationship("Case", back_populates="court_proceedings")
