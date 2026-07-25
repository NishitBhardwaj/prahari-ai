"""
Scenario Engine — the core differentiator of the Crime Simulation Laboratory.
Generates cascading event chains that modify crime probabilities based on
environmental, social, and temporal factors.

Example cascades:
  Ganesh Festival → Crowds → Pickpocket +45% → Vehicle Theft +18%
  Heavy Rain → Power Outage → CCTV Down → Burglary +20%

Depends on: master, time, weather, festival
"""

from typing import Dict, List, Tuple
from datetime import date, timedelta
import pandas as pd
import numpy as np
import json

from engines.base_engine import BaseEngine
from schemas.base import generate_id


# Scenario definitions with cascading effects
SCENARIO_DEFINITIONS = [
    {
        "id": "festival_crowd",
        "name": "Festival Crowd Scenario",
        "trigger_type": "festival",
        "trigger_condition": "crowd_level in ['Very High', 'High']",
        "cascade": [
            {"step": 1, "event": "Crowd Density Increase", "modifier_type": "crowd_density", "value": 2.5},
            {"step": 2, "event": "Police Patrol Stretched", "modifier_type": "patrol_reduction", "value": 0.6},
            {"step": 3, "event": "Pickpocket Probability Increase", "crime_type": "theft", "modifier": 0.45},
            {"step": 4, "event": "Mobile Theft Increase", "crime_type": "theft", "modifier": 0.30},
            {"step": 5, "event": "Vehicle Theft Increase", "crime_type": "vehicle_theft", "modifier": 0.18},
            {"step": 6, "event": "Crowd Assault", "crime_type": "assault", "modifier": 0.08},
            {"step": 7, "event": "CCTV Overloaded", "modifier_type": "cctv_effectiveness", "value": 0.5},
        ],
    },
    {
        "id": "heavy_rain",
        "name": "Heavy Monsoon Rain Scenario",
        "trigger_type": "weather",
        "trigger_condition": "rainfall_mm > 50",
        "cascade": [
            {"step": 1, "event": "Low Visibility", "modifier_type": "visibility", "value": 0.3},
            {"step": 2, "event": "Power Outage Probability", "modifier_type": "power_outage", "value": 0.40},
            {"step": 3, "event": "CCTV Coverage Reduced", "modifier_type": "cctv_effectiveness", "value": 0.4},
            {"step": 4, "event": "Burglary Probability Increase", "crime_type": "burglary", "modifier": 0.20},
            {"step": 5, "event": "Road Accident Increase", "crime_type": "traffic_accident", "modifier": 0.35},
            {"step": 6, "event": "Police Response Time Increase", "modifier_type": "response_time", "value": 1.40},
        ],
    },
    {
        "id": "flood",
        "name": "Flooding Scenario",
        "trigger_type": "weather",
        "trigger_condition": "is_flood == True",
        "cascade": [
            {"step": 1, "event": "Evacuation Required", "modifier_type": "evacuation", "value": 1.0},
            {"step": 2, "event": "Property Crime Increase", "crime_type": "burglary", "modifier": 0.35},
            {"step": 3, "event": "Looting Increase", "crime_type": "robbery", "modifier": 0.25},
            {"step": 4, "event": "Police Diverted to Rescue", "modifier_type": "patrol_reduction", "value": 0.3},
            {"step": 5, "event": "Traffic Disruption", "crime_type": "traffic_accident", "modifier": 0.45},
        ],
    },
    {
        "id": "heatwave",
        "name": "Heatwave Scenario",
        "trigger_type": "weather",
        "trigger_condition": "is_heatwave == True",
        "cascade": [
            {"step": 1, "event": "Aggression Increase", "modifier_type": "aggression", "value": 1.3},
            {"step": 2, "event": "Assault Increase", "crime_type": "assault", "modifier": 0.15},
            {"step": 3, "event": "Domestic Violence Increase", "crime_type": "domestic_violence", "modifier": 0.20},
            {"step": 4, "event": "Water Disputes", "crime_type": "assault", "modifier": 0.10},
        ],
    },
    {
        "id": "election",
        "name": "Election Period Scenario",
        "trigger_type": "festival",
        "trigger_condition": "festival_type == 'Election'",
        "cascade": [
            {"step": 1, "event": "Political Tension", "modifier_type": "tension", "value": 1.5},
            {"step": 2, "event": "Rioting Increase", "crime_type": "assault", "modifier": 0.20},
            {"step": 3, "event": "Intimidation Cases", "crime_type": "cheating", "modifier": 0.15},
            {"step": 4, "event": "Illegal Arms", "crime_type": "arms_act", "modifier": 0.30},
            {"step": 5, "event": "Liquor Distribution", "crime_type": "narcotics", "modifier": 0.20},
        ],
    },
    {
        "id": "cyber_campaign",
        "name": "Cyber Attack Campaign",
        "trigger_type": "periodic",
        "trigger_condition": "random_monthly_probability == 0.08",
        "cascade": [
            {"step": 1, "event": "Phishing SMS Surge", "modifier_type": "digital_activity", "value": 10.0},
            {"step": 2, "event": "UPI Fraud Increase", "crime_type": "upi_fraud", "modifier": 0.60},
            {"step": 3, "event": "Fake App Downloads", "crime_type": "cyber_fraud", "modifier": 0.25},
            {"step": 4, "event": "Identity Theft Increase", "crime_type": "cyber_fraud", "modifier": 0.15},
        ],
    },
    {
        "id": "pandemic_lockdown",
        "name": "Pandemic Lockdown Scenario",
        "trigger_type": "config",
        "trigger_condition": "is_pandemic == True",
        "cascade": [
            {"step": 1, "event": "Movement Restriction", "modifier_type": "mobility", "value": 0.3},
            {"step": 2, "event": "Street Crime Decrease", "crime_type": "theft", "modifier": -0.40},
            {"step": 3, "event": "Domestic Violence Increase", "crime_type": "domestic_violence", "modifier": 0.45},
            {"step": 4, "event": "Cyber Crime Surge", "crime_type": "cyber_fraud", "modifier": 0.50},
            {"step": 5, "event": "Lockdown Violations", "crime_type": "other", "modifier": 0.30},
        ],
    },
    {
        "id": "new_year_celebration",
        "name": "New Year Celebration Scenario",
        "trigger_type": "festival",
        "trigger_condition": "festival_name == 'New Year'",
        "cascade": [
            {"step": 1, "event": "Large Gatherings", "modifier_type": "crowd_density", "value": 3.0},
            {"step": 2, "event": "Alcohol Consumption High", "modifier_type": "intoxication", "value": 2.5},
            {"step": 3, "event": "Drunk Driving", "crime_type": "traffic_accident", "modifier": 0.40},
            {"step": 4, "event": "Assault Increase", "crime_type": "assault", "modifier": 0.20},
            {"step": 5, "event": "Sexual Harassment", "crime_type": "sexual_offence", "modifier": 0.15},
            {"step": 6, "event": "Noise Complaints", "crime_type": "other", "modifier": 0.10},
        ],
    },
    {
        "id": "economic_downturn",
        "name": "Economic Downturn Scenario",
        "trigger_type": "periodic",
        "trigger_condition": "quarterly_probability == 0.05",
        "cascade": [
            {"step": 1, "event": "Job Losses", "modifier_type": "unemployment", "value": 1.5},
            {"step": 2, "event": "Theft Increase", "crime_type": "theft", "modifier": 0.25},
            {"step": 3, "event": "Robbery Increase", "crime_type": "robbery", "modifier": 0.15},
            {"step": 4, "event": "Fraud Increase", "crime_type": "cheating", "modifier": 0.20},
            {"step": 5, "event": "Domestic Tension", "crime_type": "domestic_violence", "modifier": 0.15},
        ],
    },
]


class ScenarioEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "scenario"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "time", "weather", "festival"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Running scenario simulation engine...")

        time_ctx = self.store.get("time_context")
        weather = self.store.get("weather_records")
        festivals = self.store.get("festival_calendar")
        districts = self.store.get("districts")

        active_scenarios = []
        probability_modifiers = []

        dates = time_ctx["date"].unique()
        district_ids = districts["district_id"].tolist()
        district_names = districts["district_name"].tolist()

        for d in dates:
            date_str = str(d)

            for dist_idx, dist_id in enumerate(district_ids):
                dist_name = district_names[dist_idx]

                # Check weather triggers
                weather_day = weather[
                    (weather["date"] == date_str) & (weather["district_id"] == dist_id)
                ]

                # Check festival triggers
                fest_day = festivals[
                    (festivals["start_date"] <= date_str) &
                    (festivals["end_date"] >= date_str) &
                    (festivals["district_id"] == dist_id)
                ]

                # Time context for this date
                time_row = time_ctx[time_ctx["date"] == date_str]
                is_pandemic = False
                if not time_row.empty:
                    is_pandemic = bool(time_row.iloc[0].get("is_pandemic", False))

                # Evaluate each scenario definition
                for scenario_def in SCENARIO_DEFINITIONS:
                    activated = False

                    if scenario_def["trigger_type"] == "weather" and not weather_day.empty:
                        w = weather_day.iloc[0]
                        if "rainfall_mm > 50" in scenario_def["trigger_condition"] and w.get("rainfall_mm", 0) > 50:
                            activated = True
                        elif "is_flood" in scenario_def["trigger_condition"] and w.get("is_flood", False):
                            activated = True
                        elif "is_heatwave" in scenario_def["trigger_condition"] and w.get("is_heatwave", False):
                            activated = True

                    elif scenario_def["trigger_type"] == "festival" and not fest_day.empty:
                        for _, f in fest_day.iterrows():
                            if "crowd_level" in scenario_def["trigger_condition"]:
                                if f.get("crowd_level", "") in ["Very High", "High"]:
                                    activated = True
                                    break
                            if "festival_type == 'Election'" in scenario_def["trigger_condition"]:
                                if f.get("festival_type", "") == "Election":
                                    activated = True
                                    break
                            if "festival_name == 'New Year'" in scenario_def["trigger_condition"]:
                                if f.get("festival_name", "") == "New Year":
                                    activated = True
                                    break

                    elif scenario_def["trigger_type"] == "config":
                        if "is_pandemic" in scenario_def["trigger_condition"] and is_pandemic:
                            activated = True

                    elif scenario_def["trigger_type"] == "periodic":
                        # Random periodic events
                        if "monthly" in scenario_def["trigger_condition"]:
                            prob = 0.08
                            if self.rng.random() < prob / 30:  # Daily chance
                                activated = True
                        elif "quarterly" in scenario_def["trigger_condition"]:
                            prob = 0.05
                            if self.rng.random() < prob / 90:
                                activated = True

                    if activated:
                        scenario_id = generate_id("SCN-")
                        active_scenarios.append({
                            "scenario_id": scenario_id,
                            "scenario_def_id": scenario_def["id"],
                            "scenario_name": scenario_def["name"],
                            "date": date_str,
                            "district_id": dist_id,
                            "district_name": dist_name,
                            "trigger_type": scenario_def["trigger_type"],
                            "cascade_steps": len(scenario_def["cascade"]),
                        })

                        # Generate probability modifiers from cascade
                        for step in scenario_def["cascade"]:
                            mod_record = {
                                "modifier_id": generate_id("MOD-"),
                                "scenario_id": scenario_id,
                                "scenario_name": scenario_def["name"],
                                "date": date_str,
                                "district_id": dist_id,
                                "district_name": dist_name,
                                "step_number": step["step"],
                                "event_description": step["event"],
                            }

                            if "crime_type" in step:
                                mod_record["modifier_target"] = step["crime_type"]
                                mod_record["modifier_value"] = step["modifier"]
                                mod_record["modifier_type"] = "crime_probability"
                            else:
                                mod_record["modifier_target"] = step.get("modifier_type", "")
                                mod_record["modifier_value"] = step.get("value", 1.0)
                                mod_record["modifier_type"] = "environmental"

                            probability_modifiers.append(mod_record)

        scenarios_df = pd.DataFrame(active_scenarios) if active_scenarios else pd.DataFrame(
            columns=["scenario_id", "scenario_def_id", "scenario_name", "date",
                     "district_id", "district_name", "trigger_type", "cascade_steps"]
        )

        modifiers_df = pd.DataFrame(probability_modifiers) if probability_modifiers else pd.DataFrame(
            columns=["modifier_id", "scenario_id", "scenario_name", "date",
                     "district_id", "district_name", "step_number", "event_description",
                     "modifier_target", "modifier_value", "modifier_type"]
        )

        self.logger.info(
            f"Scenario engine: {len(scenarios_df)} active scenarios, "
            f"{len(modifiers_df)} probability modifiers generated"
        )

        return {
            "active_scenarios": scenarios_df,
            "probability_modifiers": modifiers_df,
        }
