"""
Master Engine — generates all lookup/reference tables from real Karnataka data.
This engine has NO dependencies and MUST run first in the pipeline.
Every downstream engine depends on master data.
"""

from typing import Dict, List
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine, DataStore
from configs.config_loader import PlatformConfig
from schemas.base import generate_id
from .reference_data import (
    KARNATAKA_DISTRICTS, KARNATAKA_TALUKS, RANKS, DESIGNATIONS,
    UNIT_TYPES, OCCUPATIONS, RELIGIONS, RELIGION_DISTRIBUTION,
    CASTES, CASTE_DISTRIBUTION, CASE_CATEGORIES, CASE_STATUSES,
    GRAVITY_OFFENCES, CRIME_HEADS, CRIME_SUB_HEADS, ACTS, SECTIONS,
    COURT_TYPES, EDUCATION_LEVELS, EDUCATION_DISTRIBUTION,
    INCOME_BRACKETS, INCOME_DISTRIBUTION, BANKS,
    WEAPON_TYPES, VEHICLE_MANUFACTURERS, VEHICLE_COLORS,
    KARNATAKA_RTO_CODES, MALE_FIRST_NAMES, FEMALE_FIRST_NAMES,
    LAST_NAMES, CRIME_HEAD_TO_SECTIONS, CRIME_HEAD_TO_ACTS,
    UPI_APPS,
)


class MasterEngine(BaseEngine):
    """
    Generates all master/lookup tables from real Karnataka reference data.
    No external dependencies. This is always the first engine in the pipeline.
    """

    @property
    def name(self) -> str:
        return "master"

    @property
    def dependencies(self) -> List[str]:
        return []  # No dependencies — runs first

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating master lookup tables...")

        results = {}

        # 1. State
        results["states"] = self._generate_state()

        # 2. Districts
        results["districts"] = self._generate_districts()

        # 3. Taluks
        results["taluks"] = self._generate_taluks(results["districts"])

        # 4. Unit Types
        results["unit_types"] = self._generate_unit_types()

        # 5. Police Stations
        results["police_stations"] = self._generate_police_stations(
            results["districts"], results["taluks"], results["unit_types"]
        )

        # 6. Courts
        results["courts"] = self._generate_courts(results["districts"], results["taluks"])

        # 7. Ranks
        results["ranks"] = self._generate_ranks()

        # 8. Designations
        results["designations"] = self._generate_designations(results["ranks"])

        # 9. Occupations
        results["occupations"] = self._generate_occupations()

        # 10. Religions
        results["religions"] = self._generate_religions()

        # 11. Castes
        results["castes"] = self._generate_castes()

        # 12. Case Categories
        results["case_categories"] = self._generate_case_categories()

        # 13. Case Statuses
        results["case_statuses"] = self._generate_case_statuses()

        # 14. Gravity Offences
        results["gravity_offences"] = self._generate_gravity_offences()

        # 15. Crime Heads
        results["crime_heads"] = self._generate_crime_heads(results["gravity_offences"])

        # 16. Crime Sub Heads
        results["crime_sub_heads"] = self._generate_crime_sub_heads(results["crime_heads"])

        # 17. Acts
        results["acts"] = self._generate_acts()

        # 18. Sections
        results["sections"] = self._generate_sections(results["acts"], results["gravity_offences"])

        self.logger.info(
            f"Master generation complete: {len(results)} tables, "
            f"{sum(len(df) for df in results.values())} total records"
        )
        return results

    # ─── State ────────────────────────────────────────────
    def _generate_state(self) -> pd.DataFrame:
        return pd.DataFrame([{
            "state_id": generate_id("ST-"),
            "state_name": "Karnataka",
            "state_code": "KA",
            "capital": "Bengaluru",
        }])

    # ─── Districts ────────────────────────────────────────
    def _generate_districts(self) -> pd.DataFrame:
        state_id = generate_id("ST-")  # Reference to state
        records = []
        for d in KARNATAKA_DISTRICTS:
            records.append({
                "district_id": generate_id("DIS-"),
                "district_name": d["name"],
                "district_code": d["code"],
                "state_id": state_id,
                "headquarters": d["hq"],
                "population": d["pop"],
                "area_sq_km": d["area"],
                "latitude": d["lat"],
                "longitude": d["lon"],
            })
        return pd.DataFrame(records)

    # ─── Taluks ───────────────────────────────────────────
    def _generate_taluks(self, districts_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for _, dist_row in districts_df.iterrows():
            dist_name = dist_row["district_name"]
            dist_id = dist_row["district_id"]
            taluks = KARNATAKA_TALUKS.get(dist_name, [])
            for t in taluks:
                records.append({
                    "taluk_id": generate_id("TLK-"),
                    "taluk_name": t["name"],
                    "taluk_code": t["code"],
                    "district_id": dist_id,
                    "district_name": dist_name,
                    "headquarters": t["name"],
                    "latitude": t["lat"],
                    "longitude": t["lon"],
                    "population": 0,  # Will be proportionally distributed
                })

        df = pd.DataFrame(records)

        # Distribute district population proportionally across taluks
        for dist_id in df["district_id"].unique():
            mask = df["district_id"] == dist_id
            n_taluks = mask.sum()
            if n_taluks > 0:
                dist_pop = districts_df.loc[
                    districts_df["district_id"] == dist_id, "population"
                ].values[0]
                # Assign using Dirichlet distribution for realistic uneven split
                proportions = self.rng.dirichlet(np.ones(n_taluks) * 2)
                df.loc[mask, "population"] = (proportions * dist_pop).astype(int)

        return df

    # ─── Unit Types ───────────────────────────────────────
    def _generate_unit_types(self) -> pd.DataFrame:
        records = []
        for ut in UNIT_TYPES:
            records.append({
                "unit_type_id": generate_id("UT-"),
                "unit_type_name": ut["name"],
                "description": ut["desc"],
            })
        return pd.DataFrame(records)

    # ─── Police Stations ──────────────────────────────────
    def _generate_police_stations(
        self,
        districts_df: pd.DataFrame,
        taluks_df: pd.DataFrame,
        unit_types_df: pd.DataFrame,
    ) -> pd.DataFrame:
        records = []
        regular_ut_id = unit_types_df.loc[
            unit_types_df["unit_type_name"] == "Police Station", "unit_type_id"
        ].values[0]

        special_types = unit_types_df.loc[
            unit_types_df["unit_type_name"] != "Police Station"
        ]

        station_counter = 0
        for _, taluk_row in taluks_df.iterrows():
            taluk_pop = taluk_row.get("population", 50000)
            # Number of stations proportional to population (1 per ~25,000)
            n_stations = max(1, int(taluk_pop / 25000))
            n_stations = min(n_stations, 15)  # Cap at 15 per taluk

            for i in range(n_stations):
                station_counter += 1
                # Offset coordinates slightly for each station
                lat_offset = self.rng.uniform(-0.05, 0.05)
                lon_offset = self.rng.uniform(-0.05, 0.05)

                station_name = f"{taluk_row['taluk_name']} PS {i + 1}" if i > 0 else f"{taluk_row['taluk_name']} Town PS"

                records.append({
                    "station_id": generate_id("PS-"),
                    "station_name": station_name,
                    "station_code": f"PS-{station_counter:04d}",
                    "unit_type_id": regular_ut_id,
                    "district_id": taluk_row["district_id"],
                    "district_name": taluk_row.get("district_name", ""),
                    "taluk_id": taluk_row["taluk_id"],
                    "taluk_name": taluk_row["taluk_name"],
                    "subdivision": taluk_row["taluk_name"],
                    "address": f"{station_name}, {taluk_row['taluk_name']}",
                    "phone": f"080-{self.rng.integers(20000000, 29999999)}",
                    "latitude": taluk_row["latitude"] + lat_offset,
                    "longitude": taluk_row["longitude"] + lon_offset,
                    "jurisdiction_area_sq_km": round(float(self.rng.uniform(20, 200)), 1),
                    "officer_strength": int(self.rng.integers(15, 80)),
                })

        # Add special police stations in major districts
        major_districts = ["Bengaluru Urban", "Mysuru", "Belagavi", "Mangaluru",
                          "Kalaburagi", "Dharwad", "Ballari"]
        for _, sp_type in special_types.iterrows():
            for dist_name in major_districts:
                dist_rows = districts_df[districts_df["district_name"] == dist_name]
                if dist_rows.empty:
                    # Try partial match for Dakshina Kannada → Mangaluru
                    if dist_name == "Mangaluru":
                        dist_rows = districts_df[districts_df["district_name"] == "Dakshina Kannada"]
                    if dist_rows.empty:
                        continue

                dist_row = dist_rows.iloc[0]
                station_counter += 1
                records.append({
                    "station_id": generate_id("PS-"),
                    "station_name": f"{dist_name} {sp_type['unit_type_name']}",
                    "station_code": f"PS-{station_counter:04d}",
                    "unit_type_id": sp_type["unit_type_id"],
                    "district_id": dist_row["district_id"],
                    "district_name": dist_row["district_name"],
                    "taluk_id": "",
                    "taluk_name": "",
                    "subdivision": dist_row["headquarters"],
                    "address": f"{sp_type['unit_type_name']}, {dist_name}",
                    "phone": f"080-{self.rng.integers(30000000, 39999999)}",
                    "latitude": dist_row["latitude"] + float(self.rng.uniform(-0.02, 0.02)),
                    "longitude": dist_row["longitude"] + float(self.rng.uniform(-0.02, 0.02)),
                    "jurisdiction_area_sq_km": 0.0,
                    "officer_strength": int(self.rng.integers(10, 40)),
                })

        self.logger.info(f"Generated {len(records)} police stations")
        return pd.DataFrame(records)

    # ─── Courts ───────────────────────────────────────────
    def _generate_courts(
        self, districts_df: pd.DataFrame, taluks_df: pd.DataFrame
    ) -> pd.DataFrame:
        records = []
        court_counter = 0

        for _, dist_row in districts_df.iterrows():
            # District-level courts
            for ctype in ["Sessions Court", "CJM", "Fast Track Court", "Family Court"]:
                court_counter += 1
                records.append({
                    "court_id": generate_id("CRT-"),
                    "court_name": f"{ctype}, {dist_row['district_name']}",
                    "court_type": ctype,
                    "district_id": dist_row["district_id"],
                    "district_name": dist_row["district_name"],
                    "taluk_id": "",
                    "address": f"{ctype}, {dist_row['headquarters']}",
                    "latitude": dist_row["latitude"] + float(self.rng.uniform(-0.01, 0.01)),
                    "longitude": dist_row["longitude"] + float(self.rng.uniform(-0.01, 0.01)),
                    "presiding_judge": f"Hon. {self.fake.name()}",
                })

        # Taluk-level JMFC courts
        for _, taluk_row in taluks_df.iterrows():
            court_counter += 1
            records.append({
                "court_id": generate_id("CRT-"),
                "court_name": f"JMFC, {taluk_row['taluk_name']}",
                "court_type": "JMFC",
                "district_id": taluk_row["district_id"],
                "district_name": taluk_row.get("district_name", ""),
                "taluk_id": taluk_row["taluk_id"],
                "address": f"JMFC Court, {taluk_row['taluk_name']}",
                "latitude": taluk_row["latitude"] + float(self.rng.uniform(-0.005, 0.005)),
                "longitude": taluk_row["longitude"] + float(self.rng.uniform(-0.005, 0.005)),
                "presiding_judge": f"Hon. {self.fake.name()}",
            })

        # High Court
        records.append({
            "court_id": generate_id("CRT-"),
            "court_name": "High Court of Karnataka, Bengaluru",
            "court_type": "High Court of Karnataka",
            "district_id": districts_df.loc[
                districts_df["district_name"] == "Bengaluru Urban", "district_id"
            ].values[0] if "Bengaluru Urban" in districts_df["district_name"].values else "",
            "district_name": "Bengaluru Urban",
            "taluk_id": "",
            "address": "High Court of Karnataka, Raj Bhavan Road, Bengaluru",
            "latitude": 12.9763,
            "longitude": 77.5929,
            "presiding_judge": "Hon. Chief Justice",
        })

        # Dharwad & Kalaburagi benches
        for bench_city, bench_dist in [("Dharwad", "Dharwad"), ("Kalaburagi", "Kalaburagi")]:
            dist_rows = districts_df[districts_df["district_name"] == bench_dist]
            if not dist_rows.empty:
                records.append({
                    "court_id": generate_id("CRT-"),
                    "court_name": f"High Court Bench, {bench_city}",
                    "court_type": "High Court of Karnataka",
                    "district_id": dist_rows.iloc[0]["district_id"],
                    "district_name": bench_dist,
                    "taluk_id": "",
                    "address": f"High Court Bench, {bench_city}",
                    "latitude": dist_rows.iloc[0]["latitude"],
                    "longitude": dist_rows.iloc[0]["longitude"],
                    "presiding_judge": "Hon. Justice",
                })

        self.logger.info(f"Generated {len(records)} courts")
        return pd.DataFrame(records)

    # ─── Ranks ────────────────────────────────────────────
    def _generate_ranks(self) -> pd.DataFrame:
        records = []
        for r in RANKS:
            records.append({
                "rank_id": generate_id("RNK-"),
                "rank_name": r["name"],
                "rank_code": r["code"],
                "rank_level": r["level"],
                "pay_grade": r["grade"],
            })
        return pd.DataFrame(records)

    # ─── Designations ─────────────────────────────────────
    def _generate_designations(self, ranks_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for d in DESIGNATIONS:
            rank_rows = ranks_df[ranks_df["rank_name"] == d["rank"]]
            rank_id = rank_rows.iloc[0]["rank_id"] if not rank_rows.empty else ""
            records.append({
                "designation_id": generate_id("DSG-"),
                "designation_name": d["name"],
                "rank_id": rank_id,
                "rank_name": d["rank"],
                "description": d["desc"],
            })
        return pd.DataFrame(records)

    # ─── Occupations ──────────────────────────────────────
    def _generate_occupations(self) -> pd.DataFrame:
        records = []
        for o in OCCUPATIONS:
            records.append({
                "occupation_id": generate_id("OCC-"),
                "occupation_name": o["name"],
                "occupation_category": o["category"],
            })
        return pd.DataFrame(records)

    # ─── Religions ────────────────────────────────────────
    def _generate_religions(self) -> pd.DataFrame:
        records = []
        for r in RELIGIONS:
            records.append({
                "religion_id": generate_id("REL-"),
                "religion_name": r["name"],
            })
        return pd.DataFrame(records)

    # ─── Castes ───────────────────────────────────────────
    def _generate_castes(self) -> pd.DataFrame:
        records = []
        for c in CASTES:
            records.append({
                "caste_id": generate_id("CST-"),
                "caste_name": c["name"],
                "caste_category": c["category"],
            })
        return pd.DataFrame(records)

    # ─── Case Categories ──────────────────────────────────
    def _generate_case_categories(self) -> pd.DataFrame:
        records = []
        for c in CASE_CATEGORIES:
            records.append({
                "category_id": generate_id("CAT-"),
                "category_name": c["name"],
                "description": c["desc"],
            })
        return pd.DataFrame(records)

    # ─── Case Statuses ────────────────────────────────────
    def _generate_case_statuses(self) -> pd.DataFrame:
        records = []
        for s in CASE_STATUSES:
            records.append({
                "status_id": generate_id("STS-"),
                "status_name": s["name"],
                "status_code": s["code"],
                "is_final": s["is_final"],
            })
        return pd.DataFrame(records)

    # ─── Gravity Offences ─────────────────────────────────
    def _generate_gravity_offences(self) -> pd.DataFrame:
        records = []
        for g in GRAVITY_OFFENCES:
            records.append({
                "gravity_id": generate_id("GRV-"),
                "gravity_name": g["name"],
                "gravity_level": g["level"],
                "description": g["desc"],
            })
        return pd.DataFrame(records)

    # ─── Crime Heads ──────────────────────────────────────
    def _generate_crime_heads(self, gravity_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for ch in CRIME_HEADS:
            gravity_rows = gravity_df[gravity_df["gravity_name"] == ch["gravity"]]
            gravity_id = gravity_rows.iloc[0]["gravity_id"] if not gravity_rows.empty else ""
            records.append({
                "crime_head_id": generate_id("CH-"),
                "crime_head_name": ch["name"],
                "crime_head_code": ch["code"],
                "gravity_id": gravity_id,
                "gravity_name": ch["gravity"],
                "description": "",
            })
        return pd.DataFrame(records)

    # ─── Crime Sub Heads ──────────────────────────────────
    def _generate_crime_sub_heads(self, crime_heads_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for ch_name, sub_heads in CRIME_SUB_HEADS.items():
            ch_rows = crime_heads_df[crime_heads_df["crime_head_name"] == ch_name]
            ch_id = ch_rows.iloc[0]["crime_head_id"] if not ch_rows.empty else ""
            for sh in sub_heads:
                records.append({
                    "crime_sub_head_id": generate_id("CSH-"),
                    "crime_sub_head_name": sh["name"],
                    "crime_sub_head_code": sh["code"],
                    "crime_head_id": ch_id,
                    "crime_head_name": ch_name,
                    "description": "",
                })
        return pd.DataFrame(records)

    # ─── Acts ─────────────────────────────────────────────
    def _generate_acts(self) -> pd.DataFrame:
        records = []
        for a in ACTS:
            records.append({
                "act_id": generate_id("ACT-"),
                "act_name": a["name"],
                "act_code": a["code"],
                "act_year": a["year"],
                "is_active": a["active"],
                "replaced_by": a["replaced_by"],
            })
        return pd.DataFrame(records)

    # ─── Sections ─────────────────────────────────────────
    def _generate_sections(self, acts_df: pd.DataFrame, gravity_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for s in SECTIONS:
            act_rows = acts_df[acts_df["act_code"] == s["act"]]
            act_id = act_rows.iloc[0]["act_id"] if not act_rows.empty else ""

            gravity_rows = gravity_df[gravity_df["gravity_name"] == s.get("gravity", "")]
            gravity_id = gravity_rows.iloc[0]["gravity_id"] if not gravity_rows.empty else ""

            records.append({
                "section_id": generate_id("SEC-"),
                "section_number": s["number"],
                "section_title": s["title"],
                "act_id": act_id,
                "act_code": s["act"],
                "description": s["title"],
                "is_bailable": s["bailable"],
                "is_cognizable": s["cognizable"],
                "max_punishment": s["max_punishment"],
                "gravity_id": gravity_id,
                "gravity_name": s.get("gravity", ""),
                "replaced_by_section": s.get("bns"),
            })
        return pd.DataFrame(records)
