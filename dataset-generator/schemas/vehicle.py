"""
Vehicle schemas.
Registration, ownership, insurance, and case linkage.
"""

from datetime import date
from typing import Optional
from pydantic import Field
from .base import AuditModel, generate_id


class Vehicle(AuditModel):
    """A vehicle in the simulation, potentially linked to crimes."""
    vehicle_id: str = Field(default_factory=lambda: generate_id("VEH-"))
    registration_number: str  # KA-XX-XX-XXXX format
    vehicle_type: str  # Car, Bike, Auto, Truck, Bus, Van, SUV
    manufacturer: str = ""
    model: str = ""
    year: int = 2020
    color: str = ""
    fuel_type: str = ""  # Petrol, Diesel, Electric, CNG
    engine_number: str = ""
    chassis_number: str = ""
    vin: str = ""

    # Ownership
    owner_person_id: str = ""
    owner_name: str = ""
    owner_address: str = ""
    registration_date: date
    registration_rto: str = ""  # RTO office code
    district_id: str = ""

    # Insurance
    insurance_company: str = ""
    insurance_policy_number: str = ""
    insurance_valid_from: Optional[date] = None
    insurance_valid_to: Optional[date] = None
    insurance_type: str = ""  # Third Party, Comprehensive

    # Status
    status: str = "Active"  # Active, Stolen, Seized, Scrapped, Recovered
    stolen_date: Optional[date] = None
    stolen_case_id: str = ""
    seized_date: Optional[date] = None
    seized_case_id: str = ""
    recovery_date: Optional[date] = None
    recovery_location: str = ""

    # For simulation
    latitude: float = 0.0
    longitude: float = 0.0
