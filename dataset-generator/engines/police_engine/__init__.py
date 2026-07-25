"""
Police Engine — generates police personnel with ranks, designations, and station assignments.
Depends on: master (ranks, designations, police_stations, districts)
"""

from typing import Dict, List
from datetime import date
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine
from schemas.base import generate_id
from engines.master_engine.reference_data import MALE_FIRST_NAMES, FEMALE_FIRST_NAMES, LAST_NAMES


class PoliceEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "police"

    @property
    def dependencies(self) -> List[str]:
        return ["master"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating police personnel...")

        ranks = self.store.get("ranks")
        designations = self.store.get("designations")
        stations = self.store.get("police_stations")
        districts = self.store.get("districts")

        target_employees = self.config.scale.employees

        employees = []
        postings = []

        # Rank distribution: most are constables, fewer at higher ranks
        rank_names = ranks["rank_name"].tolist()
        rank_ids = ranks["rank_id"].tolist()
        rank_distribution = np.array([
            0.35,  # Constable
            0.20,  # Head Constable
            0.12,  # ASI
            0.12,  # SI
            0.08,  # Inspector
            0.04,  # DYSP
            0.03,  # ACP
            0.02,  # DCP
            0.02,  # SP
            0.01,  # DIG
            0.005, # IG
            0.003, # ADGP
            0.002, # DGP
        ])
        # Trim or pad to match actual rank count
        if len(rank_distribution) > len(rank_names):
            rank_distribution = rank_distribution[:len(rank_names)]
        elif len(rank_distribution) < len(rank_names):
            extra = np.full(len(rank_names) - len(rank_distribution), 0.001)
            rank_distribution = np.concatenate([rank_distribution, extra])
        rank_distribution = rank_distribution / rank_distribution.sum()

        station_ids = stations["station_id"].tolist()
        station_names = stations["station_name"].tolist()
        station_dist_ids = stations["district_id"].tolist()
        station_dist_names = stations.get("district_name", pd.Series([""] * len(stations))).tolist()

        for i in range(target_employees):
            # Gender: ~85% male, 15% female in Indian police
            gender = "Male" if self.rng.random() < 0.85 else "Female"
            if gender == "Male":
                first_name = str(self.rng.choice(MALE_FIRST_NAMES))
            else:
                first_name = str(self.rng.choice(FEMALE_FIRST_NAMES))
            last_name = str(self.rng.choice(LAST_NAMES))

            rank_idx = int(self.rng.choice(len(rank_names), p=rank_distribution))
            rank_name = rank_names[rank_idx]
            rank_id = rank_ids[rank_idx]

            # Age based on rank
            rank_level = ranks.iloc[rank_idx]["rank_level"]
            min_age = 21 + (rank_level * 3)
            max_age = min(58, 25 + (rank_level * 5))
            age = int(self.rng.integers(min_age, max_age + 1))

            dob_year = 2024 - age
            dob = f"{dob_year}-{int(self.rng.integers(1,13)):02d}-{int(self.rng.integers(1,29)):02d}"

            # Assign to a station
            stn_idx = int(self.rng.integers(0, len(station_ids)))
            station_id = station_ids[stn_idx]
            station_name = station_names[stn_idx]
            dist_id = station_dist_ids[stn_idx]
            dist_name = station_dist_names[stn_idx] if stn_idx < len(station_dist_names) else ""

            # Joining date based on age
            service_years = max(1, age - 21 - int(self.rng.integers(0, 5)))
            joining_year = 2024 - service_years
            joining_date = f"{joining_year}-{int(self.rng.integers(1,13)):02d}-01"

            retirement_year = dob_year + 60
            retirement_date = f"{retirement_year}-{int(self.rng.integers(1,13)):02d}-28"

            kgid = f"KG{self.rng.integers(100000, 999999)}"
            badge = f"KP{self.rng.integers(10000, 99999)}"
            phone = f"+91{self.rng.integers(7000000000, 9999999999)}"
            email = f"{first_name.lower()}.{last_name.lower()}{self.rng.integers(1,99)}@kapolice.gov.in"

            employee_id = generate_id("EMP-")

            employees.append({
                "employee_id": employee_id,
                "kgid": kgid,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "date_of_birth": dob,
                "age": age,
                "gender": gender,
                "rank_id": rank_id,
                "rank_name": rank_name,
                "designation_id": "",
                "designation_name": "",
                "station_id": station_id,
                "station_name": station_name,
                "district_id": dist_id,
                "district_name": dist_name,
                "badge_number": badge,
                "phone": phone,
                "email": email,
                "joining_date": joining_date,
                "retirement_date": retirement_date,
                "is_active": True,
                "education": str(self.rng.choice(["Graduate", "Post-Graduate", "Higher Secondary (11-12)", "Professional (Engineering/Medical/Law)"])),
                "specialization": str(self.rng.choice(["General", "Cyber", "Traffic", "Forensics", "Intelligence", "Women & Child"])),
                "cases_handled": int(self.rng.integers(0, 200)),
                "current_workload": int(self.rng.integers(0, 30)),
            })

            # Current posting
            postings.append({
                "posting_id": generate_id("POST-"),
                "employee_id": employee_id,
                "station_id": station_id,
                "station_name": station_name,
                "district_id": dist_id,
                "rank_id": rank_id,
                "rank_name": rank_name,
                "designation_id": "",
                "from_date": joining_date,
                "to_date": None,
                "is_current": True,
                "order_number": f"GO/{self.rng.integers(1000,9999)}/{joining_year}",
                "posting_type": "Regular",
            })

        employees_df = pd.DataFrame(employees)
        postings_df = pd.DataFrame(postings)

        self.logger.info(f"Generated {len(employees_df)} employees with {len(postings_df)} postings")
        return {
            "employees": employees_df,
            "postings": postings_df,
        }
