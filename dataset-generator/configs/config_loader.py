"""
Configuration loader for the Crime Simulation Laboratory.
Loads YAML configuration, validates it with Pydantic, and provides
a singleton-like access pattern for all engines to consume.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class YearsConfig(BaseModel):
    start: int = 2020
    end: int = 2026

    @validator("end")
    def end_after_start(cls, v, values):
        if "start" in values and v < values["start"]:
            raise ValueError("end year must be >= start year")
        return v


class ScaleConfig(BaseModel):
    population: int = 50000
    households: int = 12000
    cases: int = 1000
    victims: int = 1600
    accused: int = 700
    complainants: int = 1200
    witnesses: int = 2000
    employees: int = 3000
    vehicles: int = 8000
    gangs: int = 50
    cctv_cameras: int = 500


class CrimeDistributionConfig(BaseModel):
    theft: float = 0.32
    robbery: float = 0.06
    burglary: float = 0.08
    murder: float = 0.012
    attempt_to_murder: float = 0.015
    assault: float = 0.10
    sexual_offence: float = 0.04
    cyber_fraud: float = 0.10
    upi_fraud: float = 0.04
    cheating: float = 0.05
    narcotics: float = 0.03
    traffic_accident: float = 0.07
    kidnapping: float = 0.015
    arms_act: float = 0.008
    domestic_violence: float = 0.04
    other: float = 0.02

    def as_dict(self) -> Dict[str, float]:
        return self.model_dump()

    def types(self) -> List[str]:
        return list(self.model_dump().keys())

    def probabilities(self) -> List[float]:
        return list(self.model_dump().values())


class CaseTypeDistributionConfig(BaseModel):
    FIR: float = 0.70
    UDR: float = 0.15
    ZeroFIR: float = 0.05
    PAR: float = 0.10


class FestivalEffectConfig(BaseModel):
    crowd_density_multiplier: float = 2.5
    pickpocket_increase: float = 0.45
    vehicle_theft_increase: float = 0.18
    assault_increase: float = 0.08


class HeavyRainEffectConfig(BaseModel):
    accident_increase: float = 0.35
    burglary_increase: float = 0.20
    response_time_increase: float = 0.40


class ExtremeHeatEffectConfig(BaseModel):
    assault_increase: float = 0.15


class WeatherEffectConfig(BaseModel):
    heavy_rain: HeavyRainEffectConfig = Field(default_factory=HeavyRainEffectConfig)
    extreme_heat: ExtremeHeatEffectConfig = Field(default_factory=ExtremeHeatEffectConfig)


class EvolutionConfig(BaseModel):
    urbanization_rate: float = 0.03
    cyber_crime_trend: str = "exponential"
    vehicle_growth: float = 0.05
    pandemic_years: List[int] = Field(default_factory=lambda: [2020, 2021])
    election_years: List[int] = Field(default_factory=lambda: [2023, 2024])


class SimulationConfig(BaseModel):
    batch_size: int = 10000
    parallel_engines: bool = True
    log_level: str = "INFO"


class ExportsConfig(BaseModel):
    csv: bool = True
    parquet: bool = True
    json: bool = True
    geojson: bool = True
    postgresql: bool = True
    postgis: bool = True
    neo4j: bool = True
    qdrant: bool = True
    elasticsearch: bool = True


class DistrictsConfig(BaseModel):
    all: bool = True
    selected: Optional[List[str]] = None


class PlatformConfig(BaseModel):
    """Master configuration for the entire Crime Simulation Laboratory."""

    seed: int = 42
    version: str = "1.0.0"
    years: YearsConfig = Field(default_factory=YearsConfig)
    districts: DistrictsConfig = Field(default_factory=DistrictsConfig)
    scale: ScaleConfig = Field(default_factory=ScaleConfig)
    crime_distribution: CrimeDistributionConfig = Field(default_factory=CrimeDistributionConfig)
    case_type_distribution: CaseTypeDistributionConfig = Field(default_factory=CaseTypeDistributionConfig)
    repeat_offender_rate: float = 0.18
    gang_probability: float = 0.08
    recidivism_rate: float = 0.35
    bail_grant_rate: float = 0.55
    conviction_rate: float = 0.28
    chargesheet_rate: float = 0.72
    cyber_crime_growth: float = 1.25
    festival_effect: FestivalEffectConfig = Field(default_factory=FestivalEffectConfig)
    weather_effect: WeatherEffectConfig = Field(default_factory=WeatherEffectConfig)
    evolution: EvolutionConfig = Field(default_factory=EvolutionConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    exports: ExportsConfig = Field(default_factory=ExportsConfig)


def load_config(config_path: Optional[str] = None) -> PlatformConfig:
    """
    Load and validate the platform configuration from a YAML file.
    Falls back to defaults if no file is provided or file is missing.
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "configs",
            "config.yaml",
        )

    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return PlatformConfig(**raw)
    else:
        return PlatformConfig()


# Module-level singleton for easy imports
_config: Optional[PlatformConfig] = None


def get_config(config_path: Optional[str] = None) -> PlatformConfig:
    """Get or create the singleton platform configuration."""
    global _config
    if _config is None:
        _config = load_config(config_path)
    return _config


def reset_config():
    """Reset the singleton (useful for testing)."""
    global _config
    _config = None
