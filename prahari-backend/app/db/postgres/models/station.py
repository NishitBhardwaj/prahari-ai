"""District and Police Station ORM models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.db.postgres.engine import Base


class District(Base):
    __tablename__ = "districts"

    district_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    district_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    hq_city: Mapped[str] = mapped_column(String(100), nullable=True)
    total_area_sqkm: Mapped[float] = mapped_column(Float, nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    centroid: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    boundary: Mapped[str] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    sp_name: Mapped[str] = mapped_column(String(200), nullable=True)

    stations: Mapped[list["PoliceStation"]] = relationship("PoliceStation", back_populates="district")


class PoliceStation(Base):
    __tablename__ = "police_stations"

    station_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    station_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    district_id: Mapped[str] = mapped_column(String(50), ForeignKey("districts.district_id"), nullable=False, index=True)
    subdivision: Mapped[str] = mapped_column(String(100), nullable=True)
    station_type: Mapped[str] = mapped_column(String(50), nullable=True)  # City / Rural / Highway
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    location: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    sho_name: Mapped[str] = mapped_column(String(200), nullable=True)
    officer_strength: Mapped[int] = mapped_column(Integer, nullable=True)
    jurisdiction_area_sqkm: Mapped[float] = mapped_column(Float, nullable=True)

    district: Mapped["District"] = relationship("District", back_populates="stations")
