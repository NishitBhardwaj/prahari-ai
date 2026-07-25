"""
Gang & Syndicates Engine — creates organized crime networks.
Clusters habitual offenders into gangs based on location and MO.

Depends on: master, behaviour (which provides accused)
"""

from typing import Dict, List
import pandas as pd
import numpy as np

from engines.base_engine import BaseEngine
from schemas.base import generate_id

GANG_NAMES = [
    "D-Company", "Ravi Pujari Gang", "Chhota Rajan Syndicate", 
    "Bannanje Raja Group", "Silent Sunil Associates", "Onte Rohith Gang",
    "Jedarahalli Krishnappa Associates", "Agni Sridhar Syndicate"
]

GANG_TYPES = [
    "Extortion", "Land Grabbing", "Narcotics", "Cyber Syndicate", 
    "Vehicle Theft Ring", "Smuggling", "Contract Killing"
]

class GangEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "gang"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "behaviour"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating Organized Crime Syndicates...")

        accused = self.store.get("accused_records")
        if accused.empty:
            self.logger.warning("No accused records to form gangs.")
            return {}

        districts = self.store.get("districts")
        dist_list = districts["district_id"].tolist()

        gang_records = []
        updated_accused = accused.copy()
        
        # Create a few major gangs and several smaller ones
        num_gangs = int(self.rng.integers(10, 30))
        
        habitual_offenders = updated_accused[updated_accused["is_habitual_offender"] == True]
        if len(habitual_offenders) < num_gangs * 2:
            self.logger.warning("Not enough habitual offenders to form robust gangs. Downscaling.")
            num_gangs = max(1, len(habitual_offenders) // 3)
            
        for i in range(num_gangs):
            gang_id = generate_id("GANG-")
            
            # Select name and type
            if i < len(GANG_NAMES):
                name = GANG_NAMES[i]
            else:
                name = f"Local Syndicate {i+1}"
                
            gtype = str(self.rng.choice(GANG_TYPES))
            base_dist = str(self.rng.choice(dist_list))
            
            # Threat level
            threat = round(float(self.rng.uniform(3.0, 9.9)), 1)
            
            gang_records.append({
                "gang_id": gang_id,
                "gang_name": name,
                "gang_type": gtype,
                "base_district_id": base_dist,
                "threat_level": threat,
                "active_status": bool(self.rng.random() > 0.1),
                "formation_year": int(self.rng.integers(1990, 2024)),
            })
            
            # Assign members
            # Pick a leader from habitual offenders
            potential_members = habitual_offenders[habitual_offenders["gang_id"] == ""]
            if not potential_members.empty:
                num_members = int(self.rng.integers(2, 10))
                members = potential_members.sample(n=min(num_members, len(potential_members)))
                
                for idx in members.index:
                    updated_accused.at[idx, "gang_id"] = gang_id
                    updated_accused.at[idx, "label_is_gang_related"] = True
                    # Update local view so we don't pick them again
                    habitual_offenders.at[idx, "gang_id"] = gang_id
                    
                    # Graph Edge
                    pid = updated_accused.at[idx, "person_id"]
                    self.store.add_edge(pid, "MEMBER_OF", gang_id, {"join_year": int(self.rng.integers(2000, 2024))})
                    
        self.logger.info(f"Generated {len(gang_records)} organized crime gangs.")

        return {
            "gangs": pd.DataFrame(gang_records),
            "accused_records": updated_accused,
        }
