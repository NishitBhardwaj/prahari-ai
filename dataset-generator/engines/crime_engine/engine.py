"""
Crime Engine — generates realistic, event-driven crime records.
This is the core of the event-based simulation.
It uses time, weather, festival, and scenario modifiers to generate crimes.

Depends on: master, population, time, weather, festival, scenario
"""

from typing import Dict, List, Any
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np

import json

from engines.base_engine import BaseEngine
from schemas.base import generate_id
from engines.master_engine.reference_data import CRIME_HEAD_TO_SECTIONS, CRIME_HEAD_TO_ACTS


class CrimeEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "crime"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "population", "time", "weather", "festival", "scenario"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating event-based crimes...")

        # Load reference data
        stations = self.store.get("police_stations")
        crime_heads = self.store.get("crime_heads")
        crime_sub_heads = self.store.get("crime_sub_heads")
        sections = self.store.get("sections")
        acts = self.store.get("acts")
        case_categories = self.store.get("case_categories")
        case_statuses = self.store.get("case_statuses")

        # Load dynamic context
        time_ctx = self.store.get("time_context")
        hourly_dist = self.store.get("hourly_crime_distribution")
        scenarios = self.store.get("active_scenarios")
        modifiers = self.store.get("probability_modifiers")

        # Load population (split into male/female/age groups for faster sampling)
        persons = self.store.get("persons")

        target_cases = self.config.scale.cases

        # Prepare fast lookups
        crime_heads_list = crime_heads.to_dict("records")
        stations_list = stations.to_dict("records")

        # Calculate daily target to distribute cases across time
        days_total = len(time_ctx)
        cases_per_day_base = target_cases / max(1, days_total)

        cases = []
        victims = []
        accused = []
        complainants = []
        case_acts = []
        case_sections = []
        crime_events = []

        case_count = 0
        date_idx = 0

        self.logger.info(f"Distributing {target_cases} cases over {days_total} days...")

        for _, t_row in time_ctx.iterrows():
            current_date = t_row["date"]
            year = t_row["year"]
            base_mod = t_row["base_crime_modifier"]
            cyber_mod = t_row["cyber_multiplier"]

            # Adjust daily target based on time context and scenarios
            daily_target = cases_per_day_base * base_mod

            # Apply scenario modifiers for this date
            date_mods = modifiers[modifiers["date"] == current_date] if not modifiers.empty else pd.DataFrame()

            # We generate crimes station by station
            for stn in stations_list:
                stn_id = stn["station_id"]
                stn_name = stn["station_name"]
                stn_dist_id = stn["district_id"]

                # Find specific scenario modifiers for this district
                dist_mods = date_mods[date_mods["district_id"] == stn_dist_id] if not date_mods.empty else pd.DataFrame()
                
                # Determine how many crimes happen in this station today
                # Appx cases per day per station
                stn_daily = daily_target / len(stations_list)
                
                # Apply Poisson distribution for realistic day-to-day variance
                actual_crimes = self.rng.poisson(lam=max(0.1, stn_daily))
                
                for _ in range(actual_crimes):
                    if case_count >= target_cases:
                        break

                    # Pick a crime head, weighting by gravity (Non-Heinous > Less Heinous > Heinous)
                    # We can adjust probabilities based on dist_mods
                    ch_idx = int(self.rng.integers(0, len(crime_heads_list)))
                    ch = crime_heads_list[ch_idx]
                    
                    # If it's a cyber crime, apply cyber_mod
                    if ch["crime_head_name"] == "Cyber Crime" and self.rng.random() > cyber_mod:
                        continue  # Skip if cyber mod is low (early years)

                    # Determine time of day
                    probs = hourly_dist["probability"].values
                    hour_idx = int(self.rng.choice(24, p=probs / probs.sum()))
                    incident_time = f"{hour_idx:02d}:{self.rng.integers(0, 60):02d}"

                    # Find a sub-head
                    sub_heads = crime_sub_heads[crime_sub_heads["crime_head_id"] == ch["crime_head_id"]]
                    sub_head_id = ""
                    sub_head_name = ""
                    if not sub_heads.empty:
                        sh = sub_heads.sample(n=1, random_state=self.config.seed + case_count).iloc[0]
                        sub_head_id = sh["crime_sub_head_id"]
                        sub_head_name = sh["crime_sub_head_name"]

                    case_id = generate_id("CASE-")
                    fir_no = f"{case_count + 1:04d}/{year}"

                    # Status
                    status_row = case_statuses.sample(n=1).iloc[0]

                    # Location (jittered from station)
                    lat = stn["latitude"] + float(self.rng.uniform(-0.02, 0.02))
                    lon = stn["longitude"] + float(self.rng.uniform(-0.02, 0.02))

                    
                    # AI Ground Truth Labels
                    is_solved = status_row["status_name"] in ["Chargesheeted", "Convicted", "PT (Pending Trial)"]
                    is_cyber = ch["crime_head_name"] == "Cyber Crime"
                    is_gang = False # updated later in gang engine, but initialized here
                    
                    # Explainability Metadata
                    explainability = {
                        "severity_reasoning": "Heinous crime" if ch["crime_head_name"] in ["Murder", "Rape", "Dacoity"] else "Standard crime",
                        "time_factor": "Night crime" if hour_idx < 6 or hour_idx > 22 else "Day crime",
                        "location_factor": f"Occurred at {stn['subdivision']}"
                    }

                    cases.append({
                        "case_id": case_id,
                        "fir_number": fir_no,
                        "station_id": stn_id,
                        "station_name": stn_name,
                        "district_id": stn_dist_id,
                        "year": year,
                        "date_of_report": current_date,
                        "time_of_report": f"{min(23, hour_idx + int(self.rng.integers(1, 4))):02d}:{self.rng.integers(0, 60):02d}",
                        "date_of_incident_start": current_date,
                        "time_of_incident_start": incident_time,
                        "date_of_incident_end": current_date,
                        "time_of_incident_end": incident_time,
                        "category_id": case_categories.iloc[0]["category_id"],
                        "status_id": status_row["status_id"],
                        "status_name": status_row["status_name"],
                        "is_final_status": status_row["is_final"],
                        "crime_head_id": ch["crime_head_id"],
                        "crime_head_name": ch["crime_head_name"],
                        "crime_sub_head_id": sub_head_id,
                        "crime_sub_head_name": sub_head_name,
                        "latitude": round(lat, 6),
                        "longitude": round(lon, 6),
                        "place_of_occurrence": f"Near {stn['subdivision']}, Ward {self.rng.integers(1, 50)}",
                        "distance_from_station_km": round(float(self.rng.uniform(0.5, 15.0)), 2),
                        "direction_from_station": str(self.rng.choice(["North", "South", "East", "West", "NE", "NW", "SE", "SW"])),
                        "is_sensitive": self.rng.random() < 0.05,
                        "investigating_officer_id": "",  # Assigned later in timeline
                        # AI Labels
                        "label_is_solved": is_solved,
                        "label_is_cyber": is_cyber,
                        "label_is_gang_related": is_gang,
                        "explainability_metadata": json.dumps(explainability)
                    })
                    
                    # Graph Edge
                    self.store.add_edge(stn_id, "REGISTERED", case_id, {"date": current_date})

                    # Generate Event
                    crime_events.append({
                        "event_id": generate_id("EVT-"),
                        "case_id": case_id,
                        "event_date": current_date,
                        "event_time": incident_time,
                        "event_type": "Incident Occurred",
                        "latitude": lat,
                        "longitude": lon,
                        "description": f"{ch['crime_head_name']} occurred at {incident_time}",
                    })

                    # Map to Acts and Sections (crucial for real police data)
                    assigned_acts = set(CRIME_HEAD_TO_ACTS.get(ch["crime_head_name"], ["IPC"]))
                    if "IPC" in assigned_acts and year >= 2024:
                        assigned_acts.remove("IPC")
                        assigned_acts.add("BNS")

                    for act_code in assigned_acts:
                        act_rows = acts[acts["act_code"] == act_code]
                        if not act_rows.empty:
                            act_id = act_rows.iloc[0]["act_id"]
                            case_acts.append({
                                "case_id": case_id,
                                "act_id": act_id,
                                "act_name": act_rows.iloc[0]["act_name"],
                            })

                    assigned_secs = CRIME_HEAD_TO_SECTIONS.get(ch["crime_head_name"], [])
                    for sec_num in assigned_secs:
                        # Find matching section in db
                        sec_rows = sections[sections["section_number"] == sec_num]
                        # Filter by act if year >= 2024
                        if year >= 2024:
                            sec_rows = sec_rows[sec_rows["act_code"] != "IPC"]
                        if not sec_rows.empty:
                            sec_row = sec_rows.iloc[0]
                            case_sections.append({
                                "case_id": case_id,
                                "section_id": sec_row["section_id"],
                                "section_number": sec_row["section_number"],
                                "act_code": sec_row["act_code"],
                            })

                    # Sample persons for this case (local to the district if possible)
                    # For performance, we just sample randomly but prefer district matching
                    local_persons = persons[persons["district_id"] == stn_dist_id]
                    if local_persons.empty:
                        local_persons = persons

                    n_accused = int(self.rng.integers(1, 4))
                    accused_sample = local_persons.sample(n=n_accused, replace=True)
                    for _, acc in accused_sample.iterrows():
                        acc_id = acc["person_id"]
                        is_habitual = self.rng.random() < 0.2
                        acd_id = generate_id("ACD-")
                        accused.append({
                            "accused_id": acd_id,
                            "case_id": case_id,
                            "person_id": acc_id,
                            "arrest_status": "Arrested" if self.rng.random() < 0.7 else "Absconding",
                            "is_habitual_offender": is_habitual,
                            "modus_operandi_id": "",
                            "gang_id": "",
                            # AI labels
                            "label_repeat_offender": is_habitual,
                        })
                        
                        # Graph Edge
                        self.store.add_edge(acc_id, "ACCUSED_IN", case_id, {"role": "Primary" if len(accused) == 0 else "Co-accused"})

                    n_victims = int(self.rng.integers(0, 3))
                    if n_victims > 0:
                        victim_sample = local_persons.sample(n=n_victims, replace=True)
                        for _, vic in victim_sample.iterrows():
                            vic_id = vic["person_id"]
                            v_id = generate_id("VIC-")
                            victims.append({
                                "victim_id": v_id,
                                "case_id": case_id,
                                "person_id": vic_id,
                                "injury_type": str(self.rng.choice(["None", "Minor", "Grievous", "Fatal"])),
                                "victim_type": "Individual",
                            })
                            # Graph Edge
                            self.store.add_edge(vic_id, "VICTIM_IN", case_id, {"injury": victims[-1]["injury_type"]})

                            # One victim is often the complainant
                            if len(complainants) == case_count:
                                cmp_id = generate_id("CMP-")
                                complainants.append({
                                    "complainant_id": cmp_id,
                                    "case_id": case_id,
                                    "person_id": vic_id,
                                    "complainant_type": "Victim",
                                })
                                self.store.add_edge(vic_id, "COMPLAINANT_IN", case_id, {})

                    # If no complainant yet, add one
                    if len(complainants) == case_count:
                        comp_sample = local_persons.sample(n=1).iloc[0]
                        complainants.append({
                            "complainant_id": generate_id("CMP-"),
                            "case_id": case_id,
                            "person_id": comp_sample["person_id"],
                            "complainant_type": "Third Party",
                        })
                        self.store.add_edge(comp_sample["person_id"], "COMPLAINANT_IN", case_id, {})

                    case_count += 1

            if case_count >= target_cases:
                break
            date_idx += 1

        self.logger.info(f"Generated {len(cases)} cases, {len(accused)} accused, {len(victims)} victims.")
        
        return {
            "cases": pd.DataFrame(cases),
            "case_acts": pd.DataFrame(case_acts),
            "case_sections": pd.DataFrame(case_sections),
            "crime_events": pd.DataFrame(crime_events),
            "victims": pd.DataFrame(victims),
            "accused_records": pd.DataFrame(accused),
            "complainants": pd.DataFrame(complainants),
        }
