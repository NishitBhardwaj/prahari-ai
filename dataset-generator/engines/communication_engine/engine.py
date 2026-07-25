"""
Communication Engine — generates Call Detail Records (CDRs) and device graphs.
Builds the communication networks between gang members, accused, and victims.

Depends on: master, population, crime, gang
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from engines.base_engine import BaseEngine
from schemas.base import generate_id

class CommunicationEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "communication"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "population", "crime", "gang"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating Communication Networks (CDRs)...")

        population = self.store.get("persons")
        accused_records = self.store.get("accused_records")
        gangs = self.store.get("gangs")
        cases = self.store.get("cases")
        
        if population.empty or accused_records.empty:
            return {}

        devices = []
        cdrs = []

        # Generate Devices for Accused (and some victims)
        # To keep dataset manageable, we focus heavily on the accused network
        accused_person_ids = accused_records["person_id"].unique()
        
        # We need their phones from the population table
        accused_pop = population[population["person_id"].isin(accused_person_ids)]
        
        # Create devices
        device_map = {}
        for _, row in accused_pop.iterrows():
            pid = row["person_id"]
            phone = row.get("phone_primary", "")
            if not phone:
                phone = f"+91-{self.rng.integers(7000000000, 9999999999)}"
                
            imei = f"35{self.rng.integers(1000000000000, 9999999999999)}"
            imsi = f"404{self.rng.integers(100000000000, 999999999999)}"
            
            p_id = row["person_id"]
            device_id = generate_id("DEV-")
            
            device_map[p_id] = {
                "device_id": device_id,
                "phone": row.get("phone_primary", "")
            }
            
            device = {
                "device_id": device_id,
                "person_id": p_id,
                "phone_number": generate_id("+91-9"),
                "imei": generate_id("IMEI-"),
                "imsi": generate_id("IMSI-"),
                "provider": str(self.rng.choice(["Jio", "Airtel", "Vi", "BSNL"])),
                "device_type": str(self.rng.choice(["Smartphone", "Feature Phone"])),
            }
            devices.append(device)
            person_devices[p_id] = device
            
            # Graph Edge: OWNS device
            self.store.add_edge(p_id, "OWNS", device_id, {"type": "Device"})

        # Generate CDRs (Link Analysis)
        # 1. Intra-gang communication
        for gang_id in accused_records["gang_id"].unique():
            if not gang_id:
                continue
                
            gang_members = accused_records[accused_records["gang_id"] == gang_id]["person_id"].tolist()
            if len(gang_members) < 2:
                continue
                
            # Create a dense communication graph for the gang
            num_calls = int(self.rng.integers(20, 100))
            for _ in range(num_calls):
                caller = str(self.rng.choice(gang_members))
                receiver = str(self.rng.choice(gang_members))
                if caller == receiver:
                    continue
                    
                self._add_call(caller, receiver, device_map, cdrs)

        # 2. Case-based communication (Accused talking to co-accused around crime time)
        case_dict = cases.set_index("case_id").to_dict("index")
        
        for case_id, group in accused_records.groupby("case_id"):
            members = group["person_id"].tolist()
            if len(members) < 2:
                continue
                
            c_info = case_dict.get(case_id)
            if not c_info:
                continue
                
            try:
                incident_time = datetime.fromisoformat(f"{c_info['date_of_incident_start']}T{c_info['time_of_incident_start']}")
            except:
                incident_time = datetime.now() - timedelta(days=100)
                
            # Pre-crime coordination calls
            for _ in range(int(self.rng.integers(5, 15))):
                caller = str(self.rng.choice(members))
                receiver = str(self.rng.choice(members))
                if caller == receiver:
                    continue
                    
                call_time = incident_time - timedelta(hours=int(self.rng.integers(1, 48)))
                self._add_call(caller, receiver, device_map, cdrs, specific_time=call_time)

        self.logger.info(f"Generated {len(devices)} devices and {len(cdrs)} CDR records for link analysis.")

        return {
            "devices": pd.DataFrame(devices),
            "call_detail_records": pd.DataFrame(cdrs),
        }

    def _add_call(self, caller: str, receiver: str, device_map: dict, cdrs: list, specific_time=None):
        if caller not in device_map or receiver not in device_map:
            return
            
        c_dev = device_map[caller]
        r_dev = device_map[receiver]
        
        if specific_time:
            call_time = specific_time
        else:
            # Random time in the past year
            days_ago = int(self.rng.integers(1, 365))
            hours_ago = int(self.rng.integers(0, 24))
            call_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
        duration = int(self.rng.exponential(scale=120)) # Avg 2 min
        
        # Tower locations (randomized for now, normally would pull from a tower db based on person's location)
        caller_lat = round(12.5 + float(self.rng.uniform(-0.1, 0.1)), 4)
        caller_lon = round(77.5 + float(self.rng.uniform(-0.1, 0.1)), 4)
        
        cdrs.append({
            "cdr_id": generate_id("CDR-"),
            "caller_phone": c_dev["phone"],
            "receiver_phone": r_dev["phone"],
            "call_timestamp": call_time.isoformat(),
            "duration_seconds": duration,
            "call_type": str(self.rng.choice(["Voice", "SMS", "Data Call"])),
            "caller_tower_id": f"TWR-{self.rng.integers(1000, 9999)}",
            "receiver_tower_id": f"TWR-{self.rng.integers(1000, 9999)}",
            "caller_latitude": caller_lat,
            "caller_longitude": caller_lon,
        })
        
        # Graph Edge: CALLS
        self.store.add_edge(caller_id, "CALLS", receiver_id, {"timestamp": call_time.isoformat()})
