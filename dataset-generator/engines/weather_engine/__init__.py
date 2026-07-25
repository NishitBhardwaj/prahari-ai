"""
Weather Engine — generates district-level historical weather aligned with simulation dates.
Depends on: master (districts), time (time_context)
"""

from typing import Dict, List
from datetime import date
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine
from schemas.base import generate_id


# Base climate profiles for Karnataka regions
CLIMATE_PROFILES = {
    "Coastal": {"temp_base": 28, "temp_range": 4, "rain_monsoon": 350, "rain_dry": 20, "humidity_base": 80},
    "Malnad": {"temp_base": 24, "temp_range": 6, "rain_monsoon": 400, "rain_dry": 30, "humidity_base": 75},
    "Plains": {"temp_base": 30, "temp_range": 8, "rain_monsoon": 100, "rain_dry": 10, "humidity_base": 55},
    "North": {"temp_base": 32, "temp_range": 10, "rain_monsoon": 80, "rain_dry": 8, "humidity_base": 50},
    "Urban": {"temp_base": 28, "temp_range": 6, "rain_monsoon": 150, "rain_dry": 15, "humidity_base": 60},
}

# Map districts to climate zones
DISTRICT_CLIMATE = {
    "Dakshina Kannada": "Coastal", "Udupi": "Coastal", "Uttara Kannada": "Coastal",
    "Kodagu": "Malnad", "Chikkamagaluru": "Malnad", "Hassan": "Malnad",
    "Shivamogga": "Malnad",
    "Bengaluru Urban": "Urban", "Mysuru": "Plains",
    "Bengaluru Rural": "Plains", "Ramanagara": "Plains", "Mandya": "Plains",
    "Tumakuru": "Plains", "Kolar": "Plains", "Chikkaballapur": "Plains",
    "Chamarajanagar": "Plains", "Davanagere": "Plains", "Chitradurga": "Plains",
    "Belagavi": "North", "Dharwad": "North", "Gadag": "North", "Haveri": "North",
    "Bagalkot": "North", "Vijayapura": "North",
    "Kalaburagi": "North", "Bidar": "North", "Raichur": "North", "Yadgir": "North",
    "Koppal": "North", "Ballari": "North", "Vijayanagara": "North",
}


class WeatherEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "weather"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "time"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating weather data...")

        districts = self.store.get("districts")
        time_ctx = self.store.get("time_context")

        records = []
        dates = time_ctx["date"].unique()

        for _, dist_row in districts.iterrows():
            dist_name = dist_row["district_name"]
            climate_zone = DISTRICT_CLIMATE.get(dist_name, "Plains")
            profile = CLIMATE_PROFILES[climate_zone]

            for d in dates:
                parsed = date.fromisoformat(d) if isinstance(d, str) else d
                month = parsed.month if hasattr(parsed, 'month') else int(str(d).split("-")[1])

                # Temperature: seasonal variation
                seasonal_offset = self._seasonal_temp_offset(month)
                temp_mean = profile["temp_base"] + seasonal_offset
                temp = round(float(temp_mean + self.rng.normal(0, 2)), 1)
                temp_max = round(temp + float(self.rng.uniform(2, 6)), 1)
                temp_min = round(temp - float(self.rng.uniform(2, 6)), 1)

                # Rainfall: heavy in monsoon months
                is_monsoon = month in [6, 7, 8, 9]
                is_pre_monsoon = month in [4, 5]
                if is_monsoon:
                    rain_mean = profile["rain_monsoon"] / 30  # daily
                    rainfall = round(max(0, float(self.rng.exponential(rain_mean))), 1)
                elif is_pre_monsoon:
                    rainfall = round(max(0, float(self.rng.exponential(2))), 1)
                else:
                    rainfall = round(max(0, float(self.rng.exponential(profile["rain_dry"] / 30))), 1)

                # Humidity
                humidity = profile["humidity_base"]
                if is_monsoon:
                    humidity += int(self.rng.integers(5, 15))
                else:
                    humidity -= int(self.rng.integers(0, 10))
                humidity = max(20, min(100, humidity))

                # Wind
                wind_speed = round(float(self.rng.uniform(5, 25)), 1)

                # Visibility
                if rainfall > 30:
                    visibility = "Very Poor"
                elif rainfall > 10:
                    visibility = "Poor"
                elif rainfall > 2:
                    visibility = "Moderate"
                else:
                    visibility = "Good"

                # Weather condition
                if rainfall > 50:
                    condition = "Heavy Rain"
                elif rainfall > 20:
                    condition = "Rain"
                elif rainfall > 5:
                    condition = "Light Rain"
                elif rainfall > 0:
                    condition = "Drizzle"
                elif temp_max > 40:
                    condition = "Extreme Heat"
                elif temp_max > 35:
                    condition = "Hot"
                else:
                    condition = "Clear"

                # Extreme event flags
                is_flood = rainfall > 80 and is_monsoon
                is_heatwave = temp_max > 42 and month in [3, 4, 5]

                records.append({
                    "weather_id": generate_id("WTH-"),
                    "date": d,
                    "district_id": dist_row["district_id"],
                    "district_name": dist_name,
                    "climate_zone": climate_zone,
                    "temperature_avg": temp,
                    "temperature_max": temp_max,
                    "temperature_min": temp_min,
                    "rainfall_mm": rainfall,
                    "humidity_percent": humidity,
                    "wind_speed_kmph": wind_speed,
                    "visibility": visibility,
                    "condition": condition,
                    "is_monsoon": is_monsoon,
                    "is_flood": is_flood,
                    "is_heatwave": is_heatwave,
                })

        df = pd.DataFrame(records)
        self.logger.info(f"Generated {len(df)} weather records across {len(districts)} districts")
        return {"weather_records": df}

    def _seasonal_temp_offset(self, month: int) -> float:
        """Return temperature offset based on month (Karnataka climate)."""
        offsets = {
            1: -3, 2: -1, 3: 2, 4: 4, 5: 5,
            6: 1, 7: -1, 8: -1, 9: 0,
            10: -1, 11: -2, 12: -3,
        }
        return offsets.get(month, 0)
