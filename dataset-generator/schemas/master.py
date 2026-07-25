"""
Master lookup table schemas.
Includes all reference/lookup entities: Ranks, Designations, Acts, Sections,
CrimeHead, CrimeSubHead, Occupation, Religion, Caste, CaseCategory, CaseStatus,
GravityOffence, UnitType, and legal codes (BNS, BNSS, BSA, POCSO, NDPS, etc.).
"""

from typing import Optional, List
from pydantic import Field
from .base import AuditModel, generate_id


class State(AuditModel):
    state_id: str = Field(default_factory=lambda: generate_id("ST-"))
    state_name: str
    state_code: str
    capital: str


class District(AuditModel):
    district_id: str = Field(default_factory=lambda: generate_id("DIS-"))
    district_name: str
    district_code: str
    state_id: str
    headquarters: str
    population: int = 0
    area_sq_km: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0


class Taluk(AuditModel):
    taluk_id: str = Field(default_factory=lambda: generate_id("TLK-"))
    taluk_name: str
    taluk_code: str
    district_id: str
    headquarters: str
    population: int = 0
    latitude: float = 0.0
    longitude: float = 0.0


class Village(AuditModel):
    village_id: str = Field(default_factory=lambda: generate_id("VIL-"))
    village_name: str
    village_code: str
    taluk_id: str
    district_id: str
    population: int = 0
    latitude: float = 0.0
    longitude: float = 0.0


class Ward(AuditModel):
    ward_id: str = Field(default_factory=lambda: generate_id("WRD-"))
    ward_name: str
    ward_number: int
    city: str
    district_id: str
    population: int = 0
    latitude: float = 0.0
    longitude: float = 0.0


class UnitType(AuditModel):
    unit_type_id: str = Field(default_factory=lambda: generate_id("UT-"))
    unit_type_name: str  # Police Station, Traffic PS, Cyber PS, Women PS, etc.
    description: str = ""


class PoliceStation(AuditModel):
    station_id: str = Field(default_factory=lambda: generate_id("PS-"))
    station_name: str
    station_code: str
    unit_type_id: str
    district_id: str
    taluk_id: str
    subdivision: str = ""
    address: str = ""
    phone: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    jurisdiction_area_sq_km: float = 0.0
    officer_strength: int = 0


class Court(AuditModel):
    court_id: str = Field(default_factory=lambda: generate_id("CRT-"))
    court_name: str
    court_type: str  # JMFC, CJM, Sessions, High Court, etc.
    district_id: str
    taluk_id: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    presiding_judge: str = ""


class Rank(AuditModel):
    rank_id: str = Field(default_factory=lambda: generate_id("RNK-"))
    rank_name: str
    rank_code: str
    rank_level: int  # 1=Constable, 2=HC, ..., 11=DGP
    pay_grade: str = ""


class Designation(AuditModel):
    designation_id: str = Field(default_factory=lambda: generate_id("DSG-"))
    designation_name: str
    rank_id: str
    description: str = ""


class Occupation(AuditModel):
    occupation_id: str = Field(default_factory=lambda: generate_id("OCC-"))
    occupation_name: str
    occupation_category: str  # Government, Private, Self-Employed, Student, Unemployed, etc.


class Religion(AuditModel):
    religion_id: str = Field(default_factory=lambda: generate_id("REL-"))
    religion_name: str


class Caste(AuditModel):
    caste_id: str = Field(default_factory=lambda: generate_id("CST-"))
    caste_name: str
    caste_category: str  # General, OBC, SC, ST


class CaseCategory(AuditModel):
    category_id: str = Field(default_factory=lambda: generate_id("CAT-"))
    category_name: str  # FIR, UDR, ZeroFIR, PAR
    description: str = ""


class CaseStatus(AuditModel):
    status_id: str = Field(default_factory=lambda: generate_id("STS-"))
    status_name: str  # Under Investigation, Chargesheeted, Convicted, Acquitted, Closed, etc.
    status_code: str
    is_final: bool = False


class GravityOffence(AuditModel):
    gravity_id: str = Field(default_factory=lambda: generate_id("GRV-"))
    gravity_name: str  # Heinous, Less Heinous, Non-Heinous
    gravity_level: int  # 1=Non-Heinous, 2=Less Heinous, 3=Heinous
    description: str = ""


class CrimeHead(AuditModel):
    crime_head_id: str = Field(default_factory=lambda: generate_id("CH-"))
    crime_head_name: str  # Murder, Theft, Robbery, Cyber Crime, etc.
    crime_head_code: str
    gravity_id: str
    description: str = ""


class CrimeSubHead(AuditModel):
    crime_sub_head_id: str = Field(default_factory=lambda: generate_id("CSH-"))
    crime_sub_head_name: str
    crime_sub_head_code: str
    crime_head_id: str
    description: str = ""


class Act(AuditModel):
    act_id: str = Field(default_factory=lambda: generate_id("ACT-"))
    act_name: str  # Indian Penal Code, BNS, BNSS, BSA, POCSO, NDPS, IT Act, etc.
    act_code: str  # IPC, BNS, BNSS, BSA, POCSO, NDPS, ITA, MVA, AA
    act_year: int
    is_active: bool = True
    replaced_by: Optional[str] = None  # BNS replaces IPC


class Section(AuditModel):
    section_id: str = Field(default_factory=lambda: generate_id("SEC-"))
    section_number: str  # "302", "420", "376", etc.
    section_title: str
    act_id: str
    description: str = ""
    is_bailable: bool = False
    is_cognizable: bool = True
    max_punishment: str = ""
    gravity_id: str = ""
    replaced_by_section: Optional[str] = None  # New BNS section number


class PoliceCommissionerate(AuditModel):
    commissionerate_id: str = Field(default_factory=lambda: generate_id("COM-"))
    commissionerate_name: str
    district_id: str
    commissioner: str = ""
    headquarters: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
