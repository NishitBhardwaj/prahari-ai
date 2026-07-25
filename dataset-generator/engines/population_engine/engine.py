"""
Population Engine — generates the complete synthetic population of Karnataka.
Every person is a complete entity with household, family, demographics,
education, occupation, income, address, and contact information.

Depends on: master (districts, taluks, religions, castes, occupations)
"""

from typing import Dict, List, Tuple
from datetime import date, timedelta
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine, DataStore
from configs.config_loader import PlatformConfig
from schemas.base import generate_id
from engines.master_engine.reference_data import (
    MALE_FIRST_NAMES, FEMALE_FIRST_NAMES, LAST_NAMES,
    RELIGION_DISTRIBUTION, CASTE_DISTRIBUTION,
    EDUCATION_LEVELS, EDUCATION_DISTRIBUTION,
    INCOME_BRACKETS, INCOME_DISTRIBUTION,
)


class PopulationEngine(BaseEngine):
    """
    Generates the synthetic population with realistic demographics.
    Creates households first, then populates them with family members.
    """

    @property
    def name(self) -> str:
        return "population"

    @property
    def dependencies(self) -> List[str]:
        return ["master"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating synthetic population...")

        # Load master data
        districts = self.store.get("districts")
        taluks = self.store.get("taluks")
        religions = self.store.get("religions")
        castes = self.store.get("castes")
        occupations = self.store.get("occupations")

        target_population = self.config.scale.population
        target_households = self.config.scale.households

        # Step 1: Generate households distributed across districts/taluks
        households = self._generate_households(target_households, districts, taluks)

        # Step 2: Populate each household with family members
        persons, family_rels = self._populate_households(
            households, religions, castes, occupations
        )

        # Trim or pad to target population
        if len(persons) > target_population:
            persons = persons.iloc[:target_population]
        elif len(persons) < target_population:
            extra = self._generate_single_persons(
                target_population - len(persons),
                districts, taluks, religions, castes, occupations,
            )
            persons = pd.concat([persons, extra], ignore_index=True)

        # Update household member counts
        member_counts = persons.groupby("household_id").size().reset_index(name="num_members")
        households = households.merge(member_counts, on="household_id", how="left", suffixes=("_orig", ""))
        if "num_members_orig" in households.columns:
            households["num_members"] = households["num_members"].fillna(households["num_members_orig"]).astype(int)
            households.drop(columns=["num_members_orig"], inplace=True)

        self.logger.info(
            f"Generated {len(persons)} persons in {len(households)} households "
            f"with {len(family_rels)} family relationships"
        )

        return {
            "persons": persons,
            "households": households,
            "family_relationships": family_rels,
        }

    def _generate_households(
        self, n_households: int, districts: pd.DataFrame, taluks: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate households distributed across districts proportionally to population."""
        records = []

        # Distribute households proportionally to district population
        total_pop = districts["population"].sum()
        if total_pop == 0:
            total_pop = 1
        district_weights = (districts["population"] / total_pop).values
        district_assignments = self.rng.choice(
            len(districts), size=n_households, p=district_weights
        )

        household_types = ["Nuclear", "Joint", "Single"]
        household_type_probs = [0.55, 0.25, 0.20]

        income_keys = list(INCOME_BRACKETS.keys())

        for i in range(n_households):
            dist_idx = district_assignments[i]
            dist_row = districts.iloc[dist_idx]

            # Find a taluk in this district
            dist_taluks = taluks[taluks["district_id"] == dist_row["district_id"]]
            if not dist_taluks.empty:
                taluk_row = dist_taluks.iloc[int(self.rng.integers(0, len(dist_taluks)))]
                taluk_name = taluk_row["taluk_name"]
                taluk_id = taluk_row["taluk_id"]
                base_lat = taluk_row["latitude"]
                base_lon = taluk_row["longitude"]
            else:
                taluk_name = dist_row["headquarters"]
                taluk_id = ""
                base_lat = dist_row["latitude"]
                base_lon = dist_row["longitude"]

            hh_type = str(self.random_choice(household_types, p=household_type_probs)[0])
            income_bracket = str(self.random_choice(income_keys, p=INCOME_DISTRIBUTION)[0])

            # Jitter coordinates within ~2km
            lat = base_lat + float(self.rng.uniform(-0.02, 0.02))
            lon = base_lon + float(self.rng.uniform(-0.02, 0.02))

            ward_num = int(self.rng.integers(1, 60))
            pincode = f"{self.rng.integers(560001, 591999)}"

            records.append({
                "household_id": generate_id("HH-"),
                "address_line1": f"House No. {self.rng.integers(1, 999)}, {self.rng.integers(1,20)}th Cross",
                "address_line2": f"Ward {ward_num}",
                "village_or_ward": f"Ward {ward_num}" if dist_row["population"] > 500000 else taluk_name,
                "taluk": taluk_name,
                "district": dist_row["district_name"],
                "district_id": dist_row["district_id"],
                "taluk_id": taluk_id,
                "pincode": pincode,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "household_type": hh_type,
                "income_bracket": income_bracket,
                "num_members": 0,  # Will be updated
                "head_person_id": "",  # Will be updated
            })

        return pd.DataFrame(records)

    def _populate_households(
        self,
        households: pd.DataFrame,
        religions: pd.DataFrame,
        castes: pd.DataFrame,
        occupations: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Populate each household with family members."""
        persons = []
        family_rels = []

        religion_names = religions["religion_name"].tolist()
        caste_names = castes["caste_name"].tolist()
        caste_categories = castes["caste_category"].tolist()
        religion_ids = religions["religion_id"].tolist()
        caste_ids = castes["caste_id"].tolist()
        occupation_names = occupations["occupation_name"].tolist()
        occupation_ids = occupations["occupation_id"].tolist()

        for _, hh in households.iterrows():
            hh_type = hh["household_type"]
            family_group_id = generate_id("FAM-")

            # Determine family structure
            if hh_type == "Single":
                n_adults = 1
                n_children = 0
            elif hh_type == "Nuclear":
                n_adults = 2
                n_children = int(self.rng.integers(0, 4))
            else:  # Joint
                n_adults = int(self.rng.integers(3, 7))
                n_children = int(self.rng.integers(1, 5))

            # Shared demographics for the family
            rel_idx = int(self.rng.choice(len(religion_names), p=RELIGION_DISTRIBUTION))
            family_religion = religion_names[rel_idx]
            family_religion_id = religion_ids[rel_idx]

            caste_probs = np.array(CASTE_DISTRIBUTION)
            caste_probs = caste_probs / caste_probs.sum()
            caste_idx = int(self.rng.choice(len(caste_names), p=caste_probs))
            family_caste = caste_names[caste_idx]
            family_caste_id = caste_ids[caste_idx]
            family_caste_cat = caste_categories[caste_idx]

            family_last_name = str(self.rng.choice(LAST_NAMES))

            # Income for the household
            income_range = INCOME_BRACKETS.get(hh["income_bracket"], (10000, 30000))

            # Generate head of household (adult male or female)
            head_gender = "Male" if self.rng.random() < 0.75 else "Female"
            head_age = int(self.rng.integers(28, 65))
            head_person = self._create_person(
                gender=head_gender,
                age=head_age,
                last_name=family_last_name,
                household=hh,
                family_group_id=family_group_id,
                relationship="Self",
                religion=family_religion,
                religion_id=family_religion_id,
                caste=family_caste,
                caste_id=family_caste_id,
                caste_category=family_caste_cat,
                occupation_names=occupation_names,
                occupation_ids=occupation_ids,
                income_range=income_range,
            )
            persons.append(head_person)
            head_id = head_person["person_id"]

            # Spouse
            if n_adults >= 2:
                spouse_gender = "Female" if head_gender == "Male" else "Male"
                spouse_age = head_age + int(self.rng.integers(-5, 3))
                spouse_age = max(20, spouse_age)
                spouse = self._create_person(
                    gender=spouse_gender,
                    age=spouse_age,
                    last_name=family_last_name,
                    household=hh,
                    family_group_id=family_group_id,
                    relationship="Spouse",
                    religion=family_religion,
                    religion_id=family_religion_id,
                    caste=family_caste,
                    caste_id=family_caste_id,
                    caste_category=family_caste_cat,
                    occupation_names=occupation_names,
                    occupation_ids=occupation_ids,
                    income_range=income_range,
                )
                persons.append(spouse)

                family_rels.append({
                    "relationship_id": generate_id("FREL-"),
                    "person_id": head_id,
                    "related_person_id": spouse["person_id"],
                    "relationship_type": "Spouse",
                    "household_id": hh["household_id"],
                    "family_group_id": family_group_id,
                })
                family_rels.append({
                    "relationship_id": generate_id("FREL-"),
                    "person_id": spouse["person_id"],
                    "related_person_id": head_id,
                    "relationship_type": "Spouse",
                    "household_id": hh["household_id"],
                    "family_group_id": family_group_id,
                })

            # Additional adults (for joint families: parents, siblings)
            for j in range(2, n_adults):
                extra_gender = "Male" if self.rng.random() < 0.5 else "Female"
                if j == 2:
                    # Parent
                    extra_age = head_age + int(self.rng.integers(20, 30))
                    extra_rel = "Father" if extra_gender == "Male" else "Mother"
                elif j == 3:
                    extra_age = head_age + int(self.rng.integers(18, 28))
                    extra_rel = "Mother" if extra_gender == "Female" else "Father"
                else:
                    extra_age = head_age + int(self.rng.integers(-8, 8))
                    extra_age = max(18, extra_age)
                    extra_rel = "Brother" if extra_gender == "Male" else "Sister"

                extra_age = min(95, max(18, extra_age))
                extra = self._create_person(
                    gender=extra_gender,
                    age=extra_age,
                    last_name=family_last_name,
                    household=hh,
                    family_group_id=family_group_id,
                    relationship=extra_rel,
                    religion=family_religion,
                    religion_id=family_religion_id,
                    caste=family_caste,
                    caste_id=family_caste_id,
                    caste_category=family_caste_cat,
                    occupation_names=occupation_names,
                    occupation_ids=occupation_ids,
                    income_range=income_range,
                )
                persons.append(extra)

                family_rels.append({
                    "relationship_id": generate_id("FREL-"),
                    "person_id": head_id,
                    "related_person_id": extra["person_id"],
                    "relationship_type": extra_rel,
                    "household_id": hh["household_id"],
                    "family_group_id": family_group_id,
                })

            # Children
            for k in range(n_children):
                child_gender = "Male" if self.rng.random() < 0.52 else "Female"
                child_age = int(self.rng.integers(1, min(head_age - 18, 25)))
                child_age = max(1, child_age)
                child_rel = "Son" if child_gender == "Male" else "Daughter"

                child = self._create_person(
                    gender=child_gender,
                    age=child_age,
                    last_name=family_last_name,
                    household=hh,
                    family_group_id=family_group_id,
                    relationship=child_rel,
                    religion=family_religion,
                    religion_id=family_religion_id,
                    caste=family_caste,
                    caste_id=family_caste_id,
                    caste_category=family_caste_cat,
                    occupation_names=occupation_names,
                    occupation_ids=occupation_ids,
                    income_range=(0, 0) if child_age < 18 else income_range,
                )
                persons.append(child)

                family_rels.append({
                    "relationship_id": generate_id("FREL-"),
                    "person_id": head_id,
                    "related_person_id": child["person_id"],
                    "relationship_type": "Child",
                    "household_id": hh["household_id"],
                    "family_group_id": family_group_id,
                })

        persons_df = pd.DataFrame(persons)
        family_rels_df = pd.DataFrame(family_rels) if family_rels else pd.DataFrame(
            columns=["relationship_id", "person_id", "related_person_id",
                     "relationship_type", "household_id", "family_group_id"]
        )

        # Update household head_person_id
        heads = persons_df[persons_df["relationship_to_head"] == "Self"][["household_id", "person_id"]]
        heads = heads.rename(columns={"person_id": "head_person_id"})
        households = households.drop(columns=["head_person_id"], errors="ignore")
        households = households.merge(heads, on="household_id", how="left")
        households["head_person_id"] = households["head_person_id"].fillna("")

        return persons_df, family_rels_df

    def _create_person(
        self, gender: str, age: int, last_name: str,
        household, family_group_id: str, relationship: str,
        religion: str, religion_id: str,
        caste: str, caste_id: str, caste_category: str,
        occupation_names: list, occupation_ids: list,
        income_range: tuple,
    ) -> dict:
        """Create a single person record with complete demographics."""
        if gender == "Male":
            first_name = str(self.rng.choice(MALE_FIRST_NAMES))
        else:
            first_name = str(self.rng.choice(FEMALE_FIRST_NAMES))

        full_name = f"{first_name} {last_name}"
        dob_year = 2024 - age
        dob_month = int(self.rng.integers(1, 13))
        dob_day = int(self.rng.integers(1, 29))
        dob = f"{dob_year:04d}-{dob_month:02d}-{dob_day:02d}"

        father_name = f"{str(self.rng.choice(MALE_FIRST_NAMES))} {last_name}"
        mother_name = f"{str(self.rng.choice(FEMALE_FIRST_NAMES))} {last_name}"

        # Aadhaar-like 12-digit
        aadhaar = f"{self.rng.integers(2000, 9999)}{self.rng.integers(1000, 9999)}{self.rng.integers(1000, 9999)}"

        # PAN-like ABCDE1234F
        pan_letters = "".join([chr(int(self.rng.integers(65, 91))) for _ in range(5)])
        pan_digits = f"{self.rng.integers(1000, 9999)}"
        pan_last = chr(int(self.rng.integers(65, 91)))
        pan = f"{pan_letters}{pan_digits}{pan_last}"

        # Education based on age
        if age < 6:
            education = "Illiterate"
        elif age < 15:
            edu_idx = int(self.rng.integers(0, 3))
            education = EDUCATION_LEVELS[edu_idx]
        else:
            edu_probs = np.array(EDUCATION_DISTRIBUTION)
            edu_probs = edu_probs / edu_probs.sum()
            education = str(self.rng.choice(EDUCATION_LEVELS, p=edu_probs))

        # Occupation based on age and education
        if age < 18:
            occupation = "Student" if age >= 5 else "Homemaker"
            occ_idx = next(
                (i for i, n in enumerate(occupation_names) if n == occupation),
                int(self.rng.integers(0, len(occupation_names)))
            )
        elif age > 60:
            occupation = "Retired" if self.rng.random() < 0.5 else str(self.rng.choice(occupation_names))
            occ_idx = next(
                (i for i, n in enumerate(occupation_names) if n == occupation),
                int(self.rng.integers(0, len(occupation_names)))
            )
        else:
            occ_idx = int(self.rng.integers(0, len(occupation_names)))
            occupation = occupation_names[occ_idx]

        occupation_id = occupation_ids[occ_idx] if occ_idx < len(occupation_ids) else ""

        # Income
        if age < 18:
            income = 0.0
        else:
            income = float(self.rng.uniform(income_range[0], max(income_range[0] + 1, income_range[1])))

        # Phone
        phone_primary = f"+91{self.rng.integers(7000000000, 9999999999)}"
        phone_secondary = f"+91{self.rng.integers(7000000000, 9999999999)}" if self.rng.random() < 0.3 else ""

        # Email (only for educated working adults)
        email = ""
        if age >= 18 and education not in ["Illiterate", "Primary (1-5)"]:
            if self.rng.random() < 0.6:
                email = f"{first_name.lower()}.{last_name.lower()}{self.rng.integers(1, 999)}@{'gmail.com' if self.rng.random() < 0.7 else 'yahoo.com'}"

        # Jitter from household coordinates
        lat = household["latitude"] + float(self.rng.uniform(-0.001, 0.001))
        lon = household["longitude"] + float(self.rng.uniform(-0.001, 0.001))

        return {
            "person_id": generate_id("PER-"),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "father_name": father_name,
            "mother_name": mother_name,
            "date_of_birth": dob,
            "age": age,
            "gender": gender,
            "aadhaar_id": aadhaar,
            "pan_id": pan if age >= 18 else "",
            "religion_id": religion_id,
            "religion": religion,
            "caste_id": caste_id,
            "caste": caste,
            "caste_category": caste_category,
            "education": education,
            "occupation_id": occupation_id,
            "occupation": occupation,
            "income_monthly": round(income, 2),
            "household_id": household["household_id"],
            "family_group_id": family_group_id,
            "relationship_to_head": relationship,
            "address": household["address_line1"],
            "village_or_ward": household["village_or_ward"],
            "taluk": household["taluk"],
            "district": household["district"],
            "district_id": household["district_id"],
            "taluk_id": household["taluk_id"],
            "pincode": household["pincode"],
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "phone_primary": phone_primary,
            "phone_secondary": phone_secondary,
            "email": email,
            "is_criminal": False,
            "is_victim": False,
            "is_witness": False,
            "is_police": False,
            "risk_score": 0.0,
        }

    def _generate_single_persons(
        self, n: int,
        districts: pd.DataFrame, taluks: pd.DataFrame,
        religions: pd.DataFrame, castes: pd.DataFrame,
        occupations: pd.DataFrame,
    ) -> pd.DataFrame:
        """Generate additional single persons not in households (transient, migrants, etc.)."""
        records = []
        total_pop = districts["population"].sum()
        if total_pop == 0:
            total_pop = 1
        district_weights = (districts["population"] / total_pop).values

        religion_names = religions["religion_name"].tolist()
        religion_ids = religions["religion_id"].tolist()
        caste_names = castes["caste_name"].tolist()
        caste_ids = castes["caste_id"].tolist()
        caste_categories = castes["caste_category"].tolist()
        occupation_names = occupations["occupation_name"].tolist()
        occupation_ids = occupations["occupation_id"].tolist()

        for _ in range(n):
            dist_idx = int(self.rng.choice(len(districts), p=district_weights))
            dist_row = districts.iloc[dist_idx]

            gender = "Male" if self.rng.random() < 0.55 else "Female"
            age = int(self.rng.integers(18, 60))
            last_name = str(self.rng.choice(LAST_NAMES))

            rel_idx = int(self.rng.choice(len(religion_names), p=RELIGION_DISTRIBUTION))
            caste_probs = np.array(CASTE_DISTRIBUTION)
            caste_probs = caste_probs / caste_probs.sum()
            caste_idx = int(self.rng.choice(len(caste_names), p=caste_probs))

            income_keys = list(INCOME_BRACKETS.keys())
            income_bracket = str(self.rng.choice(income_keys, p=INCOME_DISTRIBUTION))
            income_range = INCOME_BRACKETS[income_bracket]

            # Create a pseudo-household dict for this person
            pseudo_hh = {
                "household_id": generate_id("HH-"),
                "address_line1": f"Room {self.rng.integers(1, 50)}, PG/Hostel",
                "village_or_ward": dist_row["headquarters"],
                "taluk": dist_row["headquarters"],
                "district": dist_row["district_name"],
                "district_id": dist_row["district_id"],
                "taluk_id": "",
                "pincode": f"{self.rng.integers(560001, 591999)}",
                "latitude": dist_row["latitude"] + float(self.rng.uniform(-0.03, 0.03)),
                "longitude": dist_row["longitude"] + float(self.rng.uniform(-0.03, 0.03)),
            }

            person = self._create_person(
                gender=gender, age=age, last_name=last_name,
                household=pseudo_hh, family_group_id=generate_id("FAM-"),
                relationship="Self",
                religion=religion_names[rel_idx],
                religion_id=religion_ids[rel_idx],
                caste=caste_names[caste_idx],
                caste_id=caste_ids[caste_idx],
                caste_category=caste_categories[caste_idx],
                occupation_names=occupation_names,
                occupation_ids=occupation_ids,
                income_range=income_range,
            )
            records.append(person)

        return pd.DataFrame(records)
