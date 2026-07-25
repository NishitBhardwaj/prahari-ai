"""
Time Engine — provides temporal context for the simulation.
Generates daily/weekly/monthly cycles, seasons, and multi-year evolution modifiers.
Depends on: master (for year range from config)
"""

from typing import Dict, List
from datetime import date, timedelta, datetime
import pandas as pd
import numpy as np
import math

from engines.base_engine import BaseEngine
from schemas.base import generate_id


class TimeEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "time"

    @property
    def dependencies(self) -> List[str]:
        return ["master"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating temporal context data...")

        start_year = self.config.years.start
        end_year = self.config.years.end

        records = []
        current = date(start_year, 1, 1)
        end = date(end_year, 12, 31)

        while current <= end:
            # Season
            month = current.month
            if month in [6, 7, 8, 9]:
                season = "Monsoon"
            elif month in [10, 11]:
                season = "Post-Monsoon"
            elif month in [12, 1, 2]:
                season = "Winter"
            else:
                season = "Summer"

            # Day type
            dow = current.weekday()  # 0=Monday
            is_weekend = dow >= 5
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][dow]

            # Pay day effects (around 1st and 15th)
            is_pay_period = current.day <= 5 or (13 <= current.day <= 17)

            # Month end effects
            is_month_end = current.day >= 27

            # Pandemic flag
            is_pandemic = current.year in self.config.evolution.pandemic_years

            # Election flag
            is_election_year = current.year in self.config.evolution.election_years

            # Crime probability modifiers by time-of-day (hourly distribution for the day)
            # We'll store a daily baseline modifier; hour-level is computed on-the-fly by crime engine
            base_crime_modifier = 1.0
            if is_weekend:
                base_crime_modifier *= 1.15  # Weekends slightly higher
            if season == "Summer":
                base_crime_modifier *= 1.10  # Heat increases aggression
            if season == "Monsoon":
                base_crime_modifier *= 0.90  # Rain reduces outdoor crime
            if is_pandemic:
                base_crime_modifier *= 0.60  # Lockdown reduces crime
            if is_election_year and month in [3, 4, 5, 10, 11]:
                base_crime_modifier *= 1.20  # Election season tension
            if is_pay_period:
                base_crime_modifier *= 1.08  # More money = more transactions = more fraud

            # Cyber crime evolution (grows year over year)
            year_offset = current.year - start_year
            cyber_multiplier = self.config.cyber_crime_growth ** year_offset

            # Urbanization effect
            urbanization_factor = 1.0 + (self.config.evolution.urbanization_rate * year_offset)

            records.append({
                "date": current.isoformat(),
                "year": current.year,
                "month": month,
                "day": current.day,
                "day_of_week": dow,
                "day_name": day_name,
                "is_weekend": is_weekend,
                "season": season,
                "is_pay_period": is_pay_period,
                "is_month_end": is_month_end,
                "is_pandemic": is_pandemic,
                "is_election_year": is_election_year,
                "base_crime_modifier": round(base_crime_modifier, 4),
                "cyber_multiplier": round(cyber_multiplier, 4),
                "urbanization_factor": round(urbanization_factor, 4),
            })

            current += timedelta(days=1)

        df = pd.DataFrame(records)
        self.logger.info(f"Generated {len(df)} daily time context records ({start_year}-{end_year})")

        # Hourly crime probability distribution (stored as reference)
        hourly_probs = self._generate_hourly_distribution()

        return {
            "time_context": df,
            "hourly_crime_distribution": hourly_probs,
        }

    def _generate_hourly_distribution(self) -> pd.DataFrame:
        """
        Generate the probability of crime occurring at each hour of the day.
        Based on real-world patterns:
        - Low: 3am-6am
        - Rising: 7am-11am
        - Moderate: 12pm-4pm
        - Peak: 5pm-11pm
        - Declining: 12am-2am
        """
        hours = list(range(24))
        # Normalized probabilities summing to 1.0
        raw_probs = [
            0.025,  # 0:00 - midnight
            0.020,  # 1:00
            0.015,  # 2:00
            0.010,  # 3:00
            0.008,  # 4:00
            0.010,  # 5:00
            0.015,  # 6:00
            0.025,  # 7:00
            0.035,  # 8:00
            0.040,  # 9:00
            0.045,  # 10:00
            0.050,  # 11:00
            0.055,  # 12:00 - noon
            0.050,  # 13:00
            0.048,  # 14:00
            0.050,  # 15:00
            0.055,  # 16:00
            0.060,  # 17:00
            0.065,  # 18:00 - peak evening
            0.070,  # 19:00
            0.068,  # 20:00
            0.060,  # 21:00
            0.050,  # 22:00
            0.035,  # 23:00
        ]
        # Normalize
        total = sum(raw_probs)
        probs = [p / total for p in raw_probs]

        records = []
        for h, p in zip(hours, probs):
            period = "Night" if h < 6 or h >= 22 else "Morning" if h < 12 else "Afternoon" if h < 17 else "Evening"
            records.append({
                "hour": h,
                "probability": round(p, 6),
                "period": period,
                "label": f"{h:02d}:00",
            })

        return pd.DataFrame(records)
