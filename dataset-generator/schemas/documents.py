"""
RAG Document schemas.
Schemas for AI-ready textual documents generated per case.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import Field
from .base import AuditModel, generate_id


class FIRNarrative(AuditModel):
    """Full FIR narrative text for a case."""
    narrative_id: str = Field(default_factory=lambda: generate_id("FIRN-"))
    case_id: str
    station_id: str = ""
    fir_number: str = ""
    narrative_text: str
    word_count: int = 0
    language: str = "English"
    generated_date: date


class ComplaintStatement(AuditModel):
    """Complainant's statement text."""
    statement_id: str = Field(default_factory=lambda: generate_id("CMPS-"))
    case_id: str
    complainant_id: str
    person_id: str = ""
    statement_text: str
    statement_date: date
    word_count: int = 0
    language: str = "English"
    recorded_by_officer_id: str = ""


class WitnessStatementDoc(AuditModel):
    """A witness's statement document."""
    statement_id: str = Field(default_factory=lambda: generate_id("WITS-"))
    case_id: str
    witness_id: str
    person_id: str = ""
    statement_text: str
    statement_date: date
    word_count: int = 0
    language: str = "English"
    recorded_by_officer_id: str = ""
    is_161_crpc: bool = True  # Statement under 161 CrPC / 180 BNSS
    is_164_crpc: bool = False  # Statement before Magistrate


class InvestigationDiary(AuditModel):
    """Day-by-day investigation diary entry."""
    diary_id: str = Field(default_factory=lambda: generate_id("INVD-"))
    case_id: str
    entry_date: date
    entry_number: int = 1
    officer_id: str = ""
    officer_name: str = ""
    diary_text: str
    word_count: int = 0
    actions_taken: str = ""
    evidence_collected: str = ""
    persons_examined: str = ""
    places_visited: str = ""
    next_steps: str = ""


class OfficerNotes(AuditModel):
    """Investigating officer's personal notes/observations."""
    note_id: str = Field(default_factory=lambda: generate_id("NOTE-"))
    case_id: str
    officer_id: str
    note_date: date
    note_text: str
    word_count: int = 0
    note_type: str = "Observation"  # Observation, Analysis, Lead, Suspicion


class ForensicReport(AuditModel):
    """Forensic laboratory report."""
    report_id: str = Field(default_factory=lambda: generate_id("FORR-"))
    case_id: str
    evidence_id: str
    lab_name: str = ""
    lab_reference: str = ""
    report_date: date
    analyst_name: str = ""
    examination_type: str = ""  # DNA, Fingerprint, Ballistic, Chemical, Digital Forensics
    findings: str = ""
    conclusion: str = ""
    report_text: str
    word_count: int = 0


class EvidenceReport(AuditModel):
    """Evidence description and analysis report."""
    report_id: str = Field(default_factory=lambda: generate_id("EVDR-"))
    case_id: str
    evidence_id: str
    report_text: str
    report_date: date
    word_count: int = 0
    prepared_by_officer_id: str = ""


class ChargesheetSummary(AuditModel):
    """Chargesheet summary document."""
    summary_id: str = Field(default_factory=lambda: generate_id("CHGS-"))
    case_id: str
    chargesheet_id: str
    summary_text: str
    summary_date: date
    word_count: int = 0
    sections_summary: str = ""
    evidence_summary: str = ""
    accused_summary: str = ""
    witness_summary: str = ""


class CourtOrderDoc(AuditModel):
    """Court order document text."""
    order_id: str = Field(default_factory=lambda: generate_id("CORD-"))
    case_id: str
    court_id: str
    proceeding_id: str = ""
    order_date: date
    order_type: str = ""  # Remand, Bail, Charge, Acquittal, Conviction, Sentence
    order_text: str
    word_count: int = 0
    judge_name: str = ""
