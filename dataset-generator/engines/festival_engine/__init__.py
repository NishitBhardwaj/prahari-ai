"""
Festival Engine — generates the Karnataka festival and event calendar.
Includes religious festivals, public holidays, elections, and public events.
Depends on: master, time
"""

from typing import Dict, List
from datetime import date, timedelta
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine
from schemas.base import generate_id

# Real Karnataka festivals with approximate dates and affected areas
FESTIVAL_TEMPLATES = [
    # Religious Festivals
    {"name": "Ugadi", "type": "Religious", "month": 3, "day_range": (20, 30), "duration_days": 1,
     "crowd_level": "High", "scope": "State-wide", "affected_crimes": {"theft": 0.15, "assault": 0.05}},
    {"name": "Makara Sankranti", "type": "Religious", "month": 1, "day_range": (14, 15), "duration_days": 2,
     "crowd_level": "High", "scope": "State-wide", "affected_crimes": {"theft": 0.10}},
    {"name": "Ganesh Chaturthi", "type": "Religious", "month": 9, "day_range": (1, 15), "duration_days": 10,
     "crowd_level": "Very High", "scope": "State-wide",
     "affected_crimes": {"theft": 0.45, "assault": 0.08, "vehicle_theft": 0.18}},
    {"name": "Dasara (Mysuru)", "type": "Religious", "month": 10, "day_range": (1, 20), "duration_days": 10,
     "crowd_level": "Very High", "scope": "Mysuru",
     "affected_crimes": {"theft": 0.40, "assault": 0.10, "vehicle_theft": 0.15}},
    {"name": "Diwali", "type": "Religious", "month": 10, "day_range": (20, 31), "duration_days": 3,
     "crowd_level": "Very High", "scope": "State-wide",
     "affected_crimes": {"theft": 0.30, "burglary": 0.20, "fire_accident": 0.25}},
    {"name": "Eid ul-Fitr", "type": "Religious", "month": 4, "day_range": (1, 30), "duration_days": 3,
     "crowd_level": "High", "scope": "State-wide", "affected_crimes": {"theft": 0.10}},
    {"name": "Eid ul-Adha", "type": "Religious", "month": 6, "day_range": (10, 30), "duration_days": 3,
     "crowd_level": "High", "scope": "State-wide", "affected_crimes": {"theft": 0.10}},
    {"name": "Christmas", "type": "Religious", "month": 12, "day_range": (24, 26), "duration_days": 2,
     "crowd_level": "Medium", "scope": "State-wide", "affected_crimes": {"theft": 0.08}},
    {"name": "Hampi Utsav", "type": "Cultural", "month": 11, "day_range": (1, 5), "duration_days": 3,
     "crowd_level": "High", "scope": "Ballari",
     "affected_crimes": {"theft": 0.25, "assault": 0.05}},
    {"name": "Karaga Festival", "type": "Religious", "month": 4, "day_range": (1, 15), "duration_days": 3,
     "crowd_level": "High", "scope": "Bengaluru Urban",
     "affected_crimes": {"theft": 0.20, "assault": 0.06}},
    {"name": "Holi", "type": "Religious", "month": 3, "day_range": (8, 20), "duration_days": 2,
     "crowd_level": "Medium", "scope": "State-wide",
     "affected_crimes": {"assault": 0.15, "molestation": 0.10}},
    {"name": "Muharram", "type": "Religious", "month": 7, "day_range": (1, 30), "duration_days": 2,
     "crowd_level": "Medium", "scope": "State-wide",
     "affected_crimes": {"rioting": 0.05}},

    # National Holidays
    {"name": "Republic Day", "type": "National", "month": 1, "day_range": (26, 26), "duration_days": 1,
     "crowd_level": "Medium", "scope": "State-wide", "affected_crimes": {}},
    {"name": "Independence Day", "type": "National", "month": 8, "day_range": (15, 15), "duration_days": 1,
     "crowd_level": "Medium", "scope": "State-wide", "affected_crimes": {}},
    {"name": "Gandhi Jayanti", "type": "National", "month": 10, "day_range": (2, 2), "duration_days": 1,
     "crowd_level": "Low", "scope": "State-wide", "affected_crimes": {}},
    {"name": "Karnataka Rajyotsava", "type": "State", "month": 11, "day_range": (1, 1), "duration_days": 1,
     "crowd_level": "High", "scope": "State-wide", "affected_crimes": {"assault": 0.05}},

    # New Year
    {"name": "New Year", "type": "Cultural", "month": 12, "day_range": (31, 31), "duration_days": 2,
     "crowd_level": "Very High", "scope": "State-wide",
     "affected_crimes": {"assault": 0.20, "drunk_driving": 0.40, "molestation": 0.15}},

    # Elections (will be activated only in election years)
    {"name": "Election Period", "type": "Election", "month": 5, "day_range": (1, 15), "duration_days": 30,
     "crowd_level": "High", "scope": "State-wide",
     "affected_crimes": {"assault": 0.20, "rioting": 0.25, "intimidation": 0.30}},
]


class FestivalEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "festival"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "time"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating festival and event calendar...")

        time_ctx = self.store.get("time_context")
        districts = self.store.get("districts")

        start_year = self.config.years.start
        end_year = self.config.years.end
        election_years = self.config.evolution.election_years

        records = []

        for year in range(start_year, end_year + 1):
            for fest in FESTIVAL_TEMPLATES:
                # Skip elections in non-election years
                if fest["type"] == "Election" and year not in election_years:
                    continue

                # Calculate festival date
                month = fest["month"]
                day_low, day_high = fest["day_range"]
                try:
                    start_day = int(self.rng.integers(day_low, day_high + 1))
                    fest_start = date(year, month, min(start_day, 28))
                except ValueError:
                    fest_start = date(year, month, 28)

                fest_end = fest_start + timedelta(days=fest["duration_days"] - 1)

                # Affected districts
                scope = fest["scope"]
                if scope == "State-wide":
                    affected_districts = districts["district_name"].tolist()
                else:
                    affected_districts = [scope] if scope in districts["district_name"].values else districts["district_name"].tolist()[:5]

                # Crime probability modifiers
                crime_mods = fest.get("affected_crimes", {})
                crime_mods_str = str(crime_mods) if crime_mods else "{}"

                for dist_name in affected_districts:
                    dist_rows = districts[districts["district_name"] == dist_name]
                    dist_id = dist_rows.iloc[0]["district_id"] if not dist_rows.empty else ""

                    records.append({
                        "festival_id": generate_id("FEST-"),
                        "festival_name": fest["name"],
                        "festival_type": fest["type"],
                        "year": year,
                        "start_date": fest_start.isoformat(),
                        "end_date": fest_end.isoformat(),
                        "duration_days": fest["duration_days"],
                        "crowd_level": fest["crowd_level"],
                        "scope": scope,
                        "district_id": dist_id,
                        "district_name": dist_name,
                        "crime_probability_modifiers": crime_mods_str,
                        "is_public_holiday": fest["type"] in ["National", "State"],
                    })

        df = pd.DataFrame(records)
        self.logger.info(f"Generated {len(df)} festival/event entries")
        return {"festival_calendar": df}
