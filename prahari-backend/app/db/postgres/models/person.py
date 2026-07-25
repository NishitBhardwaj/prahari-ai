"""Person (Population) ORM model — shared base for accused, victims, complainants, witnesses."""

import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry

from app.db.postgres.engine import Base


class Person(Base):
    __tablename__ = "persons"

    person_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    nationality: Mapped[str] = mapped_column(String(100), nullable=True, default="Indian")
    religion: Mapped[str] = mapped_column(String(50), nullable=True)
    caste: Mapped[str] = mapped_column(String(100), nullable=True)
    occupation: Mapped[str] = mapped_column(String(200), nullable=True)
    education: Mapped[str] = mapped_column(String(100), nullable=True)
    marital_status: Mapped[str] = mapped_column(String(50), nullable=True)

    # Identity documents
    aadhaar_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=True, index=True)
    pan_number: Mapped[str] = mapped_column(String(20), nullable=True)
    voter_id: Mapped[str] = mapped_column(String(30), nullable=True)
    passport_number: Mapped[str] = mapped_column(String(20), nullable=True)
    driving_license: Mapped[str] = mapped_column(String(30), nullable=True)

    # Contact
    phone_primary: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    phone_secondary: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(200), nullable=True)

    # Address
    address_line1: Mapped[str] = mapped_column(String(500), nullable=True)
    address_line2: Mapped[str] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    district_id: Mapped[str] = mapped_column(String(50), ForeignKey("districts.district_id"), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str] = mapped_column(String(10), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    home_location: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=True)

    # Physical description
    height_cm: Mapped[float] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    complexion: Mapped[str] = mapped_column(String(50), nullable=True)
    build: Mapped[str] = mapped_column(String(50), nullable=True)
    identifying_marks: Mapped[str] = mapped_column(String(500), nullable=True)

    # Media
    profile_image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
