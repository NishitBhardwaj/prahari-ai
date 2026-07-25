"""Gang, Vehicle, Device, CDR, Financial Transaction, Narrative, Audit Log models."""

from datetime import date, datetime, timezone
from sqlalchemy import String, Float, Boolean, Date, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.postgres.engine import Base


class Gang(Base):
    __tablename__ = "gangs"

    gang_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    gang_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    syndicate_type: Mapped[str] = mapped_column(String(100), nullable=True)
    threat_level: Mapped[str] = mapped_column(String(20), nullable=True)  # HIGH / MEDIUM / LOW
    operational_base_district: Mapped[str] = mapped_column(String(100), nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    known_associates: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=True)
    badge_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    rank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rank_code: Mapped[str] = mapped_column(String(20), nullable=True)
    station_id: Mapped[str] = mapped_column(String(50), ForeignKey("police_stations.station_id"), nullable=True, index=True)
    district_id: Mapped[str] = mapped_column(String(50), ForeignKey("districts.district_id"), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    posting_date: Mapped[date] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    registration_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Car / Bike / Truck
    make: Mapped[str] = mapped_column(String(100), nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    color: Mapped[str] = mapped_column(String(50), nullable=True)
    year_of_manufacture: Mapped[int] = mapped_column(Integer, nullable=True)
    engine_number: Mapped[str] = mapped_column(String(100), nullable=True)
    chassis_number: Mapped[str] = mapped_column(String(100), nullable=True)
    owner_person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=True, index=True)
    is_stolen: Mapped[bool] = mapped_column(Boolean, default=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)


class MobileDevice(Base):
    __tablename__ = "mobile_devices"

    device_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    imei: Mapped[str] = mapped_column(String(50), unique=True, nullable=True, index=True)
    imsi: Mapped[str] = mapped_column(String(50), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=True)  # Smartphone / Feature Phone
    is_seized: Mapped[bool] = mapped_column(Boolean, default=False)


class CallDetailRecord(Base):
    __tablename__ = "call_detail_records"

    cdr_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    caller_device_id: Mapped[str] = mapped_column(String(50), ForeignKey("mobile_devices.device_id"), nullable=True, index=True)
    receiver_device_id: Mapped[str] = mapped_column(String(50), ForeignKey("mobile_devices.device_id"), nullable=True, index=True)
    caller_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    receiver_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    call_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    call_type: Mapped[str] = mapped_column(String(20), nullable=True)  # Voice / SMS / Data
    caller_tower_id: Mapped[str] = mapped_column(String(50), nullable=True)
    caller_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    caller_longitude: Mapped[float] = mapped_column(Float, nullable=True)


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    account_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(50), ForeignKey("persons.person_id"), nullable=True, index=True)
    account_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=True)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=True)
    account_type: Mapped[str] = mapped_column(String(50), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=False)


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    transaction_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    sender_account_id: Mapped[str] = mapped_column(String(50), ForeignKey("bank_accounts.account_id"), nullable=True, index=True)
    receiver_account_id: Mapped[str] = mapped_column(String(50), ForeignKey("bank_accounts.account_id"), nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    transaction_time: Mapped[str] = mapped_column(String(10), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=True)  # UPI / IMPS / NEFT
    status: Mapped[str] = mapped_column(String(20), nullable=True)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    remarks: Mapped[str] = mapped_column(String(500), nullable=True)


class NarrativeDocument(Base):
    __tablename__ = "narrative_documents"

    doc_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.case_id"), nullable=False, index=True)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Complaint / FIR Narrative / Witness Statement
    content: Mapped[str] = mapped_column(Text, nullable=True)
    author_id: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    case: Mapped["Case"] = relationship("Case", back_populates="narrative_documents")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    user_email: Mapped[str] = mapped_column(String(200), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)         # CREATE / UPDATE / DELETE / VIEW
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Case / Evidence / Person...
    resource_id: Mapped[str] = mapped_column(String(50), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    request_id: Mapped[str] = mapped_column(String(50), nullable=True)
    old_value: Mapped[dict] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
