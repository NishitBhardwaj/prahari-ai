"""
Behaviour Engine — generates Modus Operandi (M.O.) and psychological profiles.
Links behavioral signatures, risk scores, and M.O. methods to the accused records.
Crucial for downstream AI/ML clustering and profiling.

Depends on: master, crime
"""

from typing import Dict, List
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine
from schemas.base import generate_id

MO_METHODS = {
    "Theft": [
        "Pickpocketing in crowded transit",
        "Cutting bags in markets",
        "Distracting victims",
        "Snatched from running vehicle",
        "Theft of unattended luggage"
    ],
    "Burglary": [
        "Breaking lock with crowbar",
        "Entering through roof/tiles",
        "Using duplicate keys",
        "Window grill removal",
        "Targeting locked houses during day"
    ],
    "Robbery": [
        "Threatening with knife/machete",
        "Throwing chili powder",
        "Intercepting on lonely stretch",
        "Impersonating police officers",
        "Following from bank/ATM"
    ],
    "Cyber Crime": [
        "Phishing via fake SMS/links",
        "OLX/Marketplace advance fraud",
        "Fake customer care numbers",
        "Sextortion via video calls",
        "Job offer scams"
    ],
    "Assault": [
        "Sudden provocation",
        "Pre-planned ambush",
        "Use of blunt objects",
        "Intoxicated aggression",
        "Gang rivalry clash"
    ],
    "Vehicle Theft": [
        "Master key usage",
        "Hot-wiring ignition",
        "Targeting parked vehicles at night",
        "Lifting two-wheelers in vans",
        "Replacing ECU/Locks"
    ],
    "Narcotics": [
        "Selling near colleges",
        "Using peddlers on bikes",
        "Dark web procurement",
        "Concealing in regular shipments",
        "Small packets in matchboxes"
    ]
}

PSYCHOLOGICAL_TRAITS = [
    "Impulsive", "Calculated", "Aggressive", "Manipulative",
    "Opportunistic", "Organized", "Disorganized", "Thrill-seeking",
    "Desperate", "Pathological Liar", "Substance Dependent"
]

class BehaviourEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "behaviour"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "crime"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating Modus Operandi and Psychological Profiles...")

        cases = self.store.get("cases")
        accused = self.store.get("accused_records")

        if cases.empty or accused.empty:
            self.logger.warning("No cases or accused generated yet.")
            return {}

        mo_records = []
        updated_accused = accused.copy()

        # Generate MO records
        case_dict = cases.set_index("case_id").to_dict("index")
        
        for idx, row in updated_accused.iterrows():
            case_id = row["case_id"]
            if case_id not in case_dict:
                continue
                
            c = case_dict[case_id]
            crime_head = c.get("crime_head_name", "Other")
            
            # Decide if we generate MO for this accused
            # Habitual offenders almost always have an MO. Others have a chance.
            prob = 0.9 if row.get("is_habitual_offender") else 0.4
            
            if self.rng.random() < prob:
                mo_id = generate_id("MO-")
                
                methods = MO_METHODS.get(crime_head, ["Opportunistic crime", "Unplanned execution", "Standard method"])
                method = str(self.rng.choice(methods))
                
                # Assign traits
                num_traits = int(self.rng.integers(1, 4))
                traits = self.rng.choice(PSYCHOLOGICAL_TRAITS, size=num_traits, replace=False).tolist()
                
                # Calculate violence risk
                violence_base = 0.8 if crime_head in ["Assault", "Murder", "Robbery", "Dacoity"] else 0.2
                violence_risk = min(1.0, max(0.0, float(self.rng.normal(violence_base, 0.15))))
                
                # Calculate flight risk
                flight_risk = float(self.rng.uniform(0.1, 0.9))
                
                mo_records.append({
                    "mo_id": mo_id,
                    "accused_id": row["accused_id"],
                    "person_id": row["person_id"],
                    "crime_head_name": crime_head,
                    "primary_method": method,
                    "psychological_traits": ",".join(traits),
                    "violence_risk_score": round(violence_risk, 3),
                    "flight_risk_score": round(flight_risk, 3),
                    "signature_action": f"{method} with {traits[0].lower()} behavior",
                    "tools_used": "Common tools" if self.rng.random() > 0.5 else "Specialized equipment",
                })
                
                # Graph Edge
                self.store.add_edge(row["person_id"], "HAS_MO", mo_id, {"method": method})
                
                # Link MO to accused
                updated_accused.at[idx, "modus_operandi_id"] = mo_id

        self.logger.info(f"Generated {len(mo_records)} M.O. profiles.")
        
        # Replace the accused_records in the store with the updated ones
        return {
            "modus_operandi": pd.DataFrame(mo_records),
            "accused_records": updated_accused
        }
