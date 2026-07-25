"""
Communication schemas.
Phone calls (CDR), SMS, Email metadata, and Social media links.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import Field
from .base import AuditModel, generate_id


class PhoneCall(AuditModel):
    """A phone call detail record (CDR)."""
    call_id: str = Field(default_factory=lambda: generate_id("CALL-"))
    caller_person_id: str
    caller_phone: str
    receiver_person_id: str
    receiver_phone: str
    call_datetime: datetime
    duration_seconds: int = 0
    call_type: str = "Outgoing"  # Outgoing, Incoming, Missed
    caller_tower_id: str = ""
    caller_tower_lat: float = 0.0
    caller_tower_lon: float = 0.0
    receiver_tower_id: str = ""
    receiver_tower_lat: float = 0.0
    receiver_tower_lon: float = 0.0
    imei_caller: str = ""
    imei_receiver: str = ""
    is_suspicious: bool = False
    linked_case_id: str = ""


class SMS(AuditModel):
    """SMS metadata record."""
    sms_id: str = Field(default_factory=lambda: generate_id("SMS-"))
    sender_person_id: str
    sender_phone: str
    receiver_person_id: str
    receiver_phone: str
    sms_datetime: datetime
    sms_type: str = "Sent"  # Sent, Received
    sender_tower_id: str = ""
    is_suspicious: bool = False
    linked_case_id: str = ""
    content_hash: str = ""  # Hash of content (no real content stored)


class EmailMetadata(AuditModel):
    """Email metadata (no content stored)."""
    email_meta_id: str = Field(default_factory=lambda: generate_id("EMAL-"))
    sender_person_id: str
    sender_email: str
    receiver_person_id: str
    receiver_email: str
    email_datetime: datetime
    subject_hash: str = ""
    has_attachment: bool = False
    attachment_count: int = 0
    is_suspicious: bool = False
    linked_case_id: str = ""


class SocialLink(AuditModel):
    """A social media connection between two persons."""
    link_id: str = Field(default_factory=lambda: generate_id("SOC-"))
    person_id: str
    connected_person_id: str
    platform: str  # Facebook, Instagram, WhatsApp, Telegram, Twitter/X, LinkedIn
    connection_type: str = "Friend"  # Friend, Follower, Group Member, Contact
    interaction_frequency: str = "Medium"  # Low, Medium, High, Very High
    connection_since: Optional[date] = None
    is_active: bool = True
    same_group: bool = False
    group_name: str = ""
