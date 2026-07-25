from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class DraftCaseCreate(BaseModel):
    station_id: str
    station_name: str
    district_id: str
    date_of_report: date
    year: int

class DraftCaseResponse(BaseModel):
    case_id: str
    fir_number: str
    current_state: str

class CaseUpdate(BaseModel):
    crime_head_id: Optional[str] = None
    crime_head_name: Optional[str] = None
    crime_sub_head_id: Optional[str] = None
    crime_sub_head_name: Optional[str] = None
    date_of_incident_start: Optional[date] = None
    time_of_incident_start: Optional[str] = None
    date_of_incident_end: Optional[date] = None
    time_of_incident_end: Optional[str] = None
    place_of_occurrence: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_from_station_km: Optional[float] = None
    direction_from_station: Optional[str] = None

class VictimCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    injury_type: Optional[str] = None
    
class AccusedCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    is_arrested: bool = False
    
class TimelineEventResponse(BaseModel):
    event_id: str
    case_id: str
    event_type: str
    title: str
    description: Optional[str] = None
    actor_name: Optional[str] = None
    timestamp: str
