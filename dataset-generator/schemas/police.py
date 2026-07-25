"""
Police Employee schemas.
Models every police personnel with rank, designation, posting history, and assignments.
"""

from datetime import date
from typing import Optional
from pydantic import Field
from .base import AuditModel, generate_id


class Employee(AuditModel):
    """A police employee assigned to a station."""
    employee_id: str = Field(default_factory=lambda: generate_id("EMP-"))
    kgid: str = ""  # Karnataka Government ID
    first_name: str
    last_name: str
    full_name: str = ""
    date_of_birth: date
    age: int = 0
    gender: str  # Male, Female
    rank_id: str
    rank_name: str = ""
    designation_id: str = ""
    designation_name: str = ""
    station_id: str
    station_name: str = ""
    district_id: str
    district_name: str = ""
    badge_number: str = ""
    phone: str = ""
    email: str = ""
    joining_date: date
    retirement_date: Optional[date] = None
    is_active: bool = True
    education: str = ""
    specialization: str = ""  # Cyber, Forensics, Traffic, etc.
    cases_handled: int = 0
    current_workload: int = 0


class Posting(AuditModel):
    """Posting history for an employee."""
    posting_id: str = Field(default_factory=lambda: generate_id("POST-"))
    employee_id: str
    station_id: str
    station_name: str = ""
    district_id: str = ""
    rank_id: str = ""
    rank_name: str = ""
    designation_id: str = ""
    from_date: date
    to_date: Optional[date] = None
    is_current: bool = True
    order_number: str = ""
    posting_type: str = "Regular"  # Regular, Transfer, Promotion, Deputation
