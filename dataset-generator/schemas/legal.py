"""
Legal process schemas.
Chargesheet, Arrest, Court Proceedings, Bail, and Conviction records.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import Field
from .base import AuditModel, generate_id


class Arrest(AuditModel):
    """Arrest record linked to an accused and a case."""
    arrest_id: str = Field(default_factory=lambda: generate_id("ARR-"))
    case_id: str
    accused_id: str
    person_id: str
    arrest_type: str = "Arrest"  # Arrest, Surrender, Remand
    arrest_date: date
    arrest_time: str = ""
    arrest_datetime: Optional[datetime] = None
    arrest_location: str = ""
    arrest_latitude: float = 0.0
    arrest_longitude: float = 0.0
    arresting_officer_id: str = ""
    arresting_officer_name: str = ""
    station_id: str = ""
    district_id: str = ""
    is_nbw: bool = False  # Non-Bailable Warrant
    remand_type: str = ""  # Police Custody, Judicial Custody
    remand_days: int = 0
    remand_court_id: str = ""
    produced_before_court: bool = False
    production_date: Optional[date] = None


class Bail(AuditModel):
    """Bail record linked to an arrest."""
    bail_id: str = Field(default_factory=lambda: generate_id("BAIL-"))
    arrest_id: str
    case_id: str
    accused_id: str
    person_id: str
    bail_type: str  # Regular, Anticipatory, Default, Interim
    bail_date: date
    bail_court_id: str = ""
    bail_court_name: str = ""
    bail_amount: float = 0.0
    surety_amount: float = 0.0
    conditions: str = ""
    granted: bool = True
    rejection_reason: str = ""


class ChargesheetDetails(AuditModel):
    """Chargesheet (final report) filed by police to the court."""
    chargesheet_id: str = Field(default_factory=lambda: generate_id("CHG-"))
    case_id: str
    chargesheet_number: str = ""
    chargesheet_date: date
    court_id: str
    court_name: str = ""
    filing_officer_id: str = ""
    filing_officer_name: str = ""
    station_id: str = ""
    final_report_type: str = "Chargesheet"  # Chargesheet, Referred, Undetected, Mistake of Fact
    total_accused: int = 0
    total_witnesses: int = 0
    total_evidence_items: int = 0
    sections_charged: str = ""  # Comma-separated section numbers
    summary: str = ""
    is_supplementary: bool = False
    supplementary_number: int = 0


class CourtProceeding(AuditModel):
    """A single court hearing/proceeding for a case."""
    proceeding_id: str = Field(default_factory=lambda: generate_id("PROC-"))
    case_id: str
    court_id: str
    court_name: str = ""
    hearing_date: date
    hearing_number: int = 1
    hearing_type: str = ""  # Remand, Bail, Charge Framing, Evidence, Arguments, Judgement
    judge_name: str = ""
    prosecution_present: bool = True
    defense_present: bool = True
    accused_present: bool = True
    witnesses_examined: int = 0
    next_hearing_date: Optional[date] = None
    order_summary: str = ""
    order_text: str = ""


class Judgement(AuditModel):
    """Final judgement for a case."""
    judgement_id: str = Field(default_factory=lambda: generate_id("JDG-"))
    case_id: str
    court_id: str
    judgement_date: date
    judge_name: str = ""
    verdict: str = ""  # Convicted, Acquitted, Discharged, Compounded
    sentence: str = ""  # Life imprisonment, 7 years RI, Fine, etc.
    fine_amount: float = 0.0
    imprisonment_years: float = 0.0
    is_appealed: bool = False
    appeal_court_id: str = ""
    judgement_text: str = ""
