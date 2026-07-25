"""
Mobility schemas.
Travel history, vehicle routes, and GPS track points.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import Field
from .base import AuditModel, generate_id


class TravelRecord(AuditModel):
    """A travel record for a person (daily movement)."""
    travel_id: str = Field(default_factory=lambda: generate_id("TRV-"))
    person_id: str
    travel_date: date
    origin_location: str = ""
    origin_latitude: float = 0.0
    origin_longitude: float = 0.0
    destination_location: str = ""
    destination_latitude: float = 0.0
    destination_longitude: float = 0.0
    departure_time: str = ""  # HH:MM
    arrival_time: str = ""
    mode_of_transport: str = ""  # Walk, Bus, Auto, Car, Bike, Train
    vehicle_id: str = ""
    distance_km: float = 0.0
    purpose: str = ""  # Commute, Errand, Leisure, Emergency
    route_type: str = ""  # Highway, City Road, Rural Road


class GPSTrackPoint(AuditModel):
    """A single GPS coordinate in a movement track."""
    point_id: str = Field(default_factory=lambda: generate_id("GPS-"))
    travel_id: str = ""
    person_id: str = ""
    vehicle_id: str = ""
    latitude: float
    longitude: float
    timestamp: datetime
    speed_kmph: float = 0.0
    heading: float = 0.0  # 0-360 degrees
    altitude: float = 0.0
    accuracy_meters: float = 10.0
    source: str = "GPS"  # GPS, Cell Tower, WiFi


class VehicleRoute(AuditModel):
    """A recorded vehicle route."""
    route_id: str = Field(default_factory=lambda: generate_id("RTE-"))
    vehicle_id: str
    driver_person_id: str = ""
    route_date: date
    start_location: str = ""
    start_latitude: float = 0.0
    start_longitude: float = 0.0
    end_location: str = ""
    end_latitude: float = 0.0
    end_longitude: float = 0.0
    start_time: str = ""
    end_time: str = ""
    distance_km: float = 0.0
    duration_minutes: int = 0
    waypoint_count: int = 0
    toll_crossings: int = 0
    speed_violations: int = 0
