"""
Evidence and Chain of Custody schemas.
Every evidence item tracks its full lifecycle: Collection → Lab → Court → Archive.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import Field
from .base import AuditModel, generate_id


class Evidence(AuditModel):
    """An evidence item linked to a case."""
    evidence_id: str = Field(default_factory=lambda: generate_id("EVD-"))
    case_id: str
    evidence_type: str  # Weapon, Fingerprint, DNA, Mobile, Laptop, HardDisk, USB, Cash, Drug, Document, Photo, Video, Audio
    evidence_sub_type: str = ""  # e.g., for Weapon: Knife, Pistol, Rifle
    description: str = ""
    quantity: int = 1
    unit: str = ""  # pieces, grams, litres, etc.
    estimated_value: float = 0.0
    collection_date: date
    collection_time: str = ""
    collection_location: str = ""
    collection_latitude: float = 0.0
    collection_longitude: float = 0.0
    collected_by_officer_id: str = ""
    collected_by_officer_name: str = ""
    station_id: str = ""
    seizure_memo_number: str = ""
    current_status: str = "Collected"  # Collected, In Lab, Court Exhibit, Archived, Returned, Destroyed
    storage_location: str = ""
    storage_path: str = ""  # For digital evidence / media
    thumbnail_path: str = ""
    is_digital: bool = False
    is_forensic: bool = False
    forensic_lab_id: str = ""
    forensic_result: str = ""
    forensic_report_date: Optional[date] = None
    court_exhibit_number: str = ""
    linked_person_ids: List[str] = Field(default_factory=list)
    linked_vehicle_id: str = ""
    linked_weapon_id: str = ""


class ChainOfCustody(AuditModel):
    """
    A single step in the evidence chain of custody.
    Multiple entries per evidence item create the full custody timeline.
    """
    custody_id: str = Field(default_factory=lambda: generate_id("COC-"))
    evidence_id: str
    case_id: str
    step_number: int  # 1, 2, 3, ...
    action: str  # Collected, Sealed, Transferred, Received, Analyzed, Presented, Archived, Returned, Destroyed
    action_date: date
    action_time: str = ""
    action_datetime: Optional[datetime] = None
    from_location: str = ""
    to_location: str = ""
    from_person_id: str = ""
    from_person_name: str = ""
    to_person_id: str = ""
    to_person_name: str = ""
    notes: str = ""
    seal_number: str = ""
    condition: str = "Good"  # Good, Damaged, Tampered
    verification_signature: str = ""


class Weapon(AuditModel):
    """A weapon associated with a crime."""
    weapon_id: str = Field(default_factory=lambda: generate_id("WPN-"))
    weapon_type: str  # Knife, Pistol, Rifle, Improvised, Iron Rod, Acid, Explosives, Blunt Object
    weapon_sub_type: str = ""
    make: str = ""
    model: str = ""
    serial_number: str = ""
    caliber: str = ""
    is_licensed: bool = False
    license_number: str = ""
    owner_person_id: str = ""
    case_id: str = ""
    evidence_id: str = ""
    recovery_date: Optional[date] = None
    recovery_location: str = ""
    recovery_latitude: float = 0.0
    recovery_longitude: float = 0.0
    condition: str = ""  # New, Used, Damaged, Modified
    description: str = ""
