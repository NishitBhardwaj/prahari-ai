"""
Intelligence and Feature schemas.
Risk scores, hotspots, anomalies — all computed, never randomly generated.
"""

from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import Field
from .base import AuditModel, generate_id


class RiskScore(AuditModel):
    """Computed risk score for a person (accused/repeat offender)."""
    score_id: str = Field(default_factory=lambda: generate_id("RSK-"))
    person_id: str
    risk_score: float  # 0.0 to 1.0
    risk_level: str = "Low"  # Low, Medium, High, Critical
    criminal_career_length_years: float = 0.0
    total_cases: int = 0
    conviction_count: int = 0
    gang_affiliation: bool = False
    network_centrality: float = 0.0
    recidivism_probability: float = 0.0
    last_offence_date: Optional[date] = None
    escalation_trend: str = ""  # Stable, Escalating, De-escalating
    computation_date: date
    factors: str = ""  # JSON string of contributing factors
    model_version: str = "1.0"


class HotspotScore(AuditModel):
    """Computed hotspot score for a geographic area."""
    hotspot_id: str = Field(default_factory=lambda: generate_id("HOT-"))
    latitude: float
    longitude: float
    grid_id: str = ""  # H3 or custom grid cell ID
    district_id: str = ""
    station_id: str = ""
    hotspot_score: float  # 0.0 to 1.0
    hotspot_level: str = "Low"  # Low, Medium, High, Critical
    crime_count_30d: int = 0
    crime_count_90d: int = 0
    crime_count_365d: int = 0
    dominant_crime_type: str = ""
    temporal_peak_hour: int = 0  # 0-23
    population_density: float = 0.0
    cctv_coverage: float = 0.0  # 0.0 to 1.0
    patrol_frequency: float = 0.0
    environmental_vulnerability: float = 0.0
    computation_date: date
    model_version: str = "1.0"


class RepeatOffenderScore(AuditModel):
    """Computed repeat offender likelihood score."""
    repeat_score_id: str = Field(default_factory=lambda: generate_id("RPT-"))
    person_id: str
    repeat_score: float  # 0.0 to 1.0
    total_offences: int = 0
    first_offence_date: Optional[date] = None
    last_offence_date: Optional[date] = None
    offence_frequency: float = 0.0  # offences per year
    escalation_index: float = 0.0
    time_since_last: int = 0  # days
    gang_member: bool = False
    bail_violations: int = 0
    absconding_count: int = 0
    computation_date: date
    model_version: str = "1.0"


class NetworkScore(AuditModel):
    """Computed criminal network influence score."""
    network_score_id: str = Field(default_factory=lambda: generate_id("NET-"))
    person_id: str
    network_score: float  # 0.0 to 1.0
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    closeness_centrality: float = 0.0
    community_id: str = ""
    community_size: int = 0
    criminal_connections: int = 0
    total_connections: int = 0
    criminal_connection_ratio: float = 0.0
    influence_level: str = "Low"  # Low, Medium, High, Leader
    computation_date: date
    model_version: str = "1.0"


class AnomalyScore(AuditModel):
    """Statistical anomaly detection result."""
    anomaly_id: str = Field(default_factory=lambda: generate_id("ANM-"))
    entity_type: str  # Person, Area, Station, CrimeType
    entity_id: str
    anomaly_score: float  # Higher = more anomalous
    anomaly_type: str = ""  # Frequency, Pattern, Financial, Temporal, Spatial
    baseline_value: float = 0.0
    observed_value: float = 0.0
    z_score: float = 0.0
    description: str = ""
    detection_date: date
    model_version: str = "1.0"


class InvestigationPriority(AuditModel):
    """Computed investigation priority for a case."""
    priority_id: str = Field(default_factory=lambda: generate_id("PRI-"))
    case_id: str
    priority_score: float  # 0.0 to 1.0
    priority_level: str = "Medium"  # Low, Medium, High, Urgent, Critical
    gravity_weight: float = 0.0
    evidence_strength: float = 0.0
    public_interest: float = 0.0
    media_attention: float = 0.0
    victim_vulnerability: float = 0.0
    suspect_flight_risk: float = 0.0
    officer_workload: float = 0.0
    time_elapsed_days: int = 0
    computation_date: date
    model_version: str = "1.0"


class CrimeCluster(AuditModel):
    """A detected crime cluster (spatial or temporal)."""
    cluster_id: str = Field(default_factory=lambda: generate_id("CLU-"))
    cluster_type: str  # Spatial, Temporal, Spatio-Temporal
    center_latitude: float = 0.0
    center_longitude: float = 0.0
    radius_km: float = 0.0
    crime_type: str = ""
    case_count: int = 0
    case_ids: List[str] = Field(default_factory=list)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    district_id: str = ""
    station_id: str = ""
    detection_method: str = ""  # DBSCAN, KMeans, HDBSCAN
    silhouette_score: float = 0.0
    computation_date: date
    model_version: str = "1.0"


class MOSimilarity(AuditModel):
    """Modus Operandi similarity between two cases."""
    similarity_id: str = Field(default_factory=lambda: generate_id("MOS-"))
    case_id_1: str
    case_id_2: str
    similarity_score: float  # 0.0 to 1.0
    matching_factors: str = ""  # JSON: weapon, time, location, target, method
    is_series: bool = False
    series_id: str = ""
    computation_date: date
    model_version: str = "1.0"
