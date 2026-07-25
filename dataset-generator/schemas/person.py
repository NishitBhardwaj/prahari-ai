"""
Person, Household, and Family schemas.
Models every synthetic person with full demographic, household,
family relationships, education, occupation, income, and contact details.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import Field
from .base import AuditModel, generate_id


class Household(AuditModel):
    """A household is a physical dwelling with one or more family members."""
    household_id: str = Field(default_factory=lambda: generate_id("HH-"))
    address_line1: str
    address_line2: str = ""
    village_or_ward: str
    taluk: str
    district: str
    district_id: str
    taluk_id: str
    pincode: str
    latitude: float
    longitude: float
    household_type: str = "Nuclear"  # Nuclear, Joint, Single
    income_bracket: str = "Middle"  # BPL, Lower, Middle, Upper-Middle, Upper
    num_members: int = 1
    head_person_id: str = ""


class Person(AuditModel):
    """
    A synthetic person in the simulation. Used as the base for
    Victim, Accused, Complainant, and Witness roles.
    """
    person_id: str = Field(default_factory=lambda: generate_id("PER-"))
    first_name: str
    last_name: str
    full_name: str = ""
    father_name: str = ""
    mother_name: str = ""
    date_of_birth: date
    age: int
    gender: str  # Male, Female, Other
    aadhaar_id: str = ""  # Synthetic 12-digit
    pan_id: str = ""  # Synthetic ABCDE1234F format

    # Demographics
    religion_id: str = ""
    religion: str = ""
    caste_id: str = ""
    caste: str = ""
    caste_category: str = ""  # General, OBC, SC, ST
    education: str = ""  # Illiterate, Primary, Secondary, Graduate, Post-Graduate, Professional
    occupation_id: str = ""
    occupation: str = ""
    income_monthly: float = 0.0

    # Household
    household_id: str = ""
    family_group_id: str = ""
    relationship_to_head: str = ""  # Self, Spouse, Son, Daughter, Father, Mother, etc.

    # Location
    address: str = ""
    village_or_ward: str = ""
    taluk: str = ""
    district: str = ""
    district_id: str = ""
    taluk_id: str = ""
    pincode: str = ""
    latitude: float = 0.0
    longitude: float = 0.0

    # Contact
    phone_primary: str = ""
    phone_secondary: str = ""
    email: str = ""

    # Flags for simulation
    is_criminal: bool = False
    is_victim: bool = False
    is_witness: bool = False
    is_police: bool = False
    risk_score: float = 0.0


class FamilyRelationship(AuditModel):
    """Explicit family relationship between two persons."""
    relationship_id: str = Field(default_factory=lambda: generate_id("FREL-"))
    person_id: str
    related_person_id: str
    relationship_type: str  # Parent, Child, Sibling, Spouse, In-Law, Grandparent, Uncle, Aunt, Cousin
    household_id: str
    family_group_id: str


class Victim(AuditModel):
    """A person who is a victim in one or more cases."""
    victim_id: str = Field(default_factory=lambda: generate_id("VIC-"))
    person_id: str
    case_id: str
    victim_type: str = "Direct"  # Direct, Indirect
    injury_type: str = ""  # None, Minor, Grievous, Fatal
    injury_description: str = ""
    hospitalized: bool = False
    hospital_name: str = ""
    death: bool = False
    death_date: Optional[date] = None
    compensation_amount: float = 0.0
    compensation_paid: bool = False
    statement_recorded: bool = False
    statement_date: Optional[date] = None


class Accused(AuditModel):
    """A person who is an accused in one or more cases."""
    accused_id: str = Field(default_factory=lambda: generate_id("ACC-"))
    person_id: str
    case_id: str
    role: str = "Principal"  # Principal, Accomplice, Abettor, Conspirator
    status: str = "Wanted"  # Wanted, Arrested, On Bail, Absconding, Convicted, Acquitted
    arrest_date: Optional[date] = None
    bail_date: Optional[date] = None
    bail_type: str = ""  # Regular, Anticipatory, Default
    surrender_date: Optional[date] = None
    modus_operandi: str = ""
    previous_cases_count: int = 0
    is_repeat_offender: bool = False
    is_gang_member: bool = False
    gang_id: str = ""
    criminal_career_id: str = ""


class Complainant(AuditModel):
    """A person who files a complaint/FIR."""
    complainant_id: str = Field(default_factory=lambda: generate_id("CMP-"))
    person_id: str
    case_id: str
    complaint_date: date
    complaint_type: str = "Written"  # Written, Oral, Online, Phone
    relation_to_victim: str = ""  # Self, Parent, Spouse, Friend, Neighbour, Stranger, Police
    statement: str = ""
    is_anonymous: bool = False


class Witness(AuditModel):
    """A person who witnesses an incident."""
    witness_id: str = Field(default_factory=lambda: generate_id("WIT-"))
    person_id: str
    case_id: str
    witness_type: str = "Eye"  # Eye, Ear, Expert, Official, Panch, Hostile
    relation_to_victim: str = ""
    relation_to_accused: str = ""
    reliability_score: float = 0.8  # 0.0 to 1.0
    proximity_to_incident: str = ""  # At scene, Nearby, Remote
    statement: str = ""
    statement_date: Optional[date] = None
    available_for_court: bool = True
    hostile: bool = False
    protection_needed: bool = False
