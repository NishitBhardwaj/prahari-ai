"""User and authentication ORM model."""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.postgres.engine import Base


class UserRole(str, PyEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SYS_ADMIN = "SYS_ADMIN"
    SCRB_ANALYST = "SCRB_ANALYST"
    AI_ANALYST = "AI_ANALYST"
    DIST_ADMIN = "DIST_ADMIN"
    SHO = "SHO"
    IO = "IO"
    DEO = "DEO"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    badge_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.DEO)
    station_id: Mapped[str] = mapped_column(String(50), ForeignKey("police_stations.station_id"), nullable=True)
    district_id: Mapped[str] = mapped_column(String(50), ForeignKey("districts.district_id"), nullable=True)
    catalyst_user_id: Mapped[str] = mapped_column(String(200), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
