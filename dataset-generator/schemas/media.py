"""
Media and CCTV schemas.
Structured media assets, CCTV cameras, recordings, frames, and detections.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field
from .base import AuditModel, generate_id


class MediaAsset(AuditModel):
    """A media asset linked to an entity (person, vehicle, evidence, case)."""
    media_id: str = Field(default_factory=lambda: generate_id("MED-"))
    entity_type: str  # Person, Vehicle, Weapon, Evidence, Case, CrimeScene, CCTV
    entity_id: str
    media_type: str  # Image, Video, Audio, Document
    media_sub_type: str = ""  # Profile Photo, Vehicle Photo, Crime Scene, Forensic, Fingerprint, DNA Report
    file_name: str = ""
    storage_path: str = ""
    thumbnail_path: str = ""
    file_size_bytes: int = 0
    file_format: str = ""  # jpg, png, mp4, mp3, pdf
    resolution: str = ""  # 1920x1080, etc.
    duration_seconds: int = 0  # For video/audio
    geotag_latitude: float = 0.0
    geotag_longitude: float = 0.0
    capture_datetime: Optional[datetime] = None
    camera_id: str = ""
    description: str = ""
    is_evidence: bool = False
    evidence_id: str = ""
    case_id: str = ""
    hash_md5: str = ""
    hash_sha256: str = ""


class CCTVCamera(AuditModel):
    """A CCTV camera in the surveillance network."""
    camera_id: str = Field(default_factory=lambda: generate_id("CAM-"))
    camera_name: str
    location_description: str = ""
    latitude: float
    longitude: float
    station_id: str = ""  # Nearest police station
    district_id: str = ""
    camera_type: str = "Fixed"  # Fixed, PTZ, Dome, Bullet
    resolution: str = "1080p"
    manufacturer: str = ""
    model: str = ""
    installation_date: Optional[date] = None
    is_active: bool = True
    coverage_angle: int = 90  # degrees
    coverage_range_meters: int = 50
    has_night_vision: bool = True
    has_audio: bool = False
    ip_address: str = ""
    storage_days: int = 30


class CCTVRecording(AuditModel):
    """A recording session from a CCTV camera."""
    recording_id: str = Field(default_factory=lambda: generate_id("REC-"))
    camera_id: str
    start_datetime: datetime
    end_datetime: datetime
    duration_seconds: int = 0
    storage_path: str = ""
    file_size_bytes: int = 0
    quality: str = "Good"  # Good, Fair, Poor
    has_motion: bool = False
    is_archived: bool = False
    linked_case_id: str = ""


class CCTVFrame(AuditModel):
    """A specific frame extracted from a CCTV recording."""
    frame_id: str = Field(default_factory=lambda: generate_id("FRM-"))
    recording_id: str
    camera_id: str
    frame_number: int
    timestamp: datetime
    storage_path: str = ""
    has_detection: bool = False
    detected_persons: int = 0
    detected_vehicles: int = 0
    detected_weapons: int = 0
    linked_case_id: str = ""


class CCTVDetection(AuditModel):
    """An object detected in a CCTV frame."""
    detection_id: str = Field(default_factory=lambda: generate_id("DET-"))
    frame_id: str
    recording_id: str
    camera_id: str
    detection_type: str  # Person, Vehicle, Weapon, Object
    confidence: float = 0.0  # 0.0 to 1.0
    bounding_box: str = ""  # x1,y1,x2,y2
    linked_person_id: str = ""
    linked_vehicle_id: str = ""
    linked_weapon_id: str = ""
    timestamp: datetime
    description: str = ""
