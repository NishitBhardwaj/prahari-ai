"""
Crime and Case schemas.
CaseMaster, FIR details, and all crime-related junction tables.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import Field
from .base import AuditModel, generate_id


class CaseMaster(AuditModel):
    """
    The central case entity. Every crime incident creates a CaseMaster record.
    Supports FIR, UDR, ZeroFIR, and PAR case types.
    """
    case_id: str = Field(default_factory=lambda: generate_id("CASE-"))
    crime_number: str  # Year/Number format e.g., "2024/0001"
    case_number: str = ""
    case_type: str  # FIR, UDR, ZeroFIR, PAR

    # Station & Jurisdiction
    station_id: str
    station_name: str = ""
    district_id: str
    district_name: str = ""

    # Crime Classification
    crime_head_id: str
    crime_head: str = ""
    crime_sub_head_id: str = ""
    crime_sub_head: str = ""
    gravity_id: str = ""
    gravity: str = ""  # Heinous, Less Heinous, Non-Heinous

    # Dates & Times
    incident_date: date
    incident_time: str = ""  # HH:MM format
    incident_datetime: Optional[datetime] = None
    report_date: date
    registration_date: date
    registration_datetime: Optional[datetime] = None

    # Location
    incident_location: str = ""
    incident_latitude: float = 0.0
    incident_longitude: float = 0.0
    incident_place_type: str = ""  # Road, Residence, Market, Office, Open Area, etc.

    # Status
    status_id: str = ""
    status: str = "Under Investigation"
    is_closed: bool = False
    closure_date: Optional[date] = None
    closure_reason: str = ""  # Chargesheeted, Undetected, Mistake of Fact, etc.

    # Officers
    investigating_officer_id: str = ""
    investigating_officer_name: str = ""
    sho_id: str = ""
    sho_name: str = ""

    # Court
    court_id: str = ""
    court_name: str = ""

    # Narrative
    brief_facts: str = ""
    detailed_narrative: str = ""

    # Links
    victim_count: int = 0
    accused_count: int = 0
    witness_count: int = 0
    evidence_count: int = 0
    property_value: float = 0.0
    property_recovered: float = 0.0

    # Scenario context
    scenario_id: str = ""
    scenario_type: str = ""
    trigger_event: str = ""

    # Digital crime fields
    is_cyber_crime: bool = False
    cyber_crime_type: str = ""  # UPI Fraud, Phishing, Identity Theft, etc.
    digital_evidence_count: int = 0


class CaseAct(AuditModel):
    """Junction table: Case ↔ Act (many-to-many)."""
    case_act_id: str = Field(default_factory=lambda: generate_id("CA-"))
    case_id: str
    act_id: str
    act_name: str = ""


class CaseSection(AuditModel):
    """Junction table: Case ↔ Section (many-to-many)."""
    case_section_id: str = Field(default_factory=lambda: generate_id("CS-"))
    case_id: str
    section_id: str
    section_number: str = ""
    act_id: str = ""
    act_name: str = ""
    is_primary: bool = False


class CrimeEvent(AuditModel):
    """
    The event chain that leads to a crime. Tracks the sequence:
    Activity → Trigger → Conflict → Crime.
    """
    event_id: str = Field(default_factory=lambda: generate_id("EVT-"))
    case_id: str
    event_sequence: int  # 1, 2, 3... order in chain
    event_type: str  # Activity, Trigger, Conflict, Opportunity, Crime
    event_description: str
    event_datetime: datetime
    location_latitude: float = 0.0
    location_longitude: float = 0.0
    involved_person_ids: List[str] = Field(default_factory=list)
    environmental_factor: str = ""  # Weather, Festival, Time-of-day, etc.
    probability_modifier: float = 1.0  # How much this event modified crime probability
