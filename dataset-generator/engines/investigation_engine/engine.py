"""
Investigation Engine — simulates the complete lifecycle of a police investigation.
Generates an extensive timeline covering Complaint -> FIR -> IO Assigned -> 
Crime Scene Visit -> Evidence Collection -> Witness Interview -> 
Phone/Financial Analysis -> Arrest -> Chargesheet -> Court.

Depends on: master, crime, police
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from engines.base_engine import BaseEngine
from schemas.base import generate_id

class InvestigationEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "investigation"

    @property
    def dependencies(self) -> List[str]:
        # Replacing 'timeline'
        return ["master", "crime", "police"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating 13-step Investigation Lifecycles...")

        cases = self.store.get("cases")
        crime_events = self.store.get("crime_events")
        employees = self.store.get("employees")
        courts = self.store.get("courts")
        
        if cases.empty:
            return {}

        updated_cases = cases.copy()
        new_events = []
        chargesheets = []
        proceedings = []
        investigation_diaries = []

        court_list = courts["court_id"].tolist() if not courts.empty else []
        io_pool = employees[employees["rank_name"].isin(["Sub-Inspector", "Inspector"])]
        io_list = io_pool["employee_id"].tolist() if not io_pool.empty else ["EMP-00000"]

        for idx, row in updated_cases.iterrows():
            case_id = row["case_id"]
            lat, lon = row["latitude"], row["longitude"]
            incident_date = datetime.fromisoformat(row["date_of_incident_start"])
            
            # Step 1 & 2: Complaint and FIR (Already somewhat implied by Case registration, we just map it)
            assigned_io = str(self.rng.choice(io_list))
            updated_cases.at[idx, "investigating_officer_id"] = assigned_io
            
            current_time = incident_date + timedelta(hours=int(self.rng.integers(1, 12)))
            
            def add_event(e_type, desc, hours_delay, log_to_diary=True):
                nonlocal current_time
                current_time += timedelta(hours=hours_delay)
                new_events.append({
                    "event_id": generate_id("EVT-"),
                    "case_id": case_id,
                    "event_date": current_time.date().isoformat(),
                    "event_time": current_time.time().strftime("%H:%M"),
                    "event_type": e_type,
                    "latitude": lat,
                    "longitude": lon,
                    "description": desc
                })
                
                # Graph Edge for event
                self.store.add_edge(case_id, "HAS_EVENT", new_events[-1]["event_id"], {"type": e_type})
                
                if log_to_diary:
                    investigation_diaries.append({
                        "diary_id": generate_id("CD-"),
                        "case_id": case_id,
                        "officer_id": assigned_io,
                        "entry_date": current_time.date().isoformat(),
                        "entry_time": current_time.time().strftime("%H:%M"),
                        "activity_type": e_type,
                        "notes": f"IO conducted {e_type}. {desc}"
                    })

            # 3. Officer Assigned
            add_event("IO Assigned", f"Officer {assigned_io} took charge of the investigation.", 1)
            
            # 4. Crime Scene Visit
            add_event("Crime Scene Visit", "Visited the place of occurrence, prepared spot panchnama.", int(self.rng.integers(1, 5)))
            
            # 5. Evidence Collection
            if self.rng.random() > 0.3:
                add_event("Evidence Collection", "Seized material evidence from the scene.", int(self.rng.integers(1, 4)))
            
            # 6. Witness Interview
            if self.rng.random() > 0.2:
                add_event("Witness Interview", "Recorded statements of witnesses under Sec 161 CrPC (or Sec 180 BNSS).", int(self.rng.integers(5, 48)))

            # 7 & 8. CCTV and Tech Analysis
            if self.rng.random() > 0.5:
                add_event("CCTV Recovery", "Procured CCTV footage from surrounding areas.", int(self.rng.integers(12, 72)))
            if self.rng.random() > 0.4:
                add_event("Phone Analysis", "Requested CDRs and tower dumps.", int(self.rng.integers(24, 96)))
                
            # 9. Financial Analysis (if fraud)
            if row["crime_head_name"] in ["Cyber Crime", "Cheating/Fraud"]:
                add_event("Financial Analysis", "Requested bank statements and froze suspicious accounts.", int(self.rng.integers(24, 120)))

            # 10 & 11. Suspect Id and Arrest
            status = row["status_name"]
            is_solved = status in ["Chargesheeted", "PT (Pending Trial)", "Convicted", "Acquitted"]
            
            if is_solved:
                add_event("Suspect Identification", "Identified primary suspects based on technical and human intelligence.", int(self.rng.integers(48, 300)))
                add_event("Arrest", "Suspects apprehended and brought to station.", int(self.rng.integers(12, 120)))
                
                # 12. Chargesheet
                cs_delay_days = int(self.rng.integers(10, 60))
                cs_date = current_time + timedelta(days=cs_delay_days)
                
                if cs_date.year <= self.config.years.end:
                    cs_id = generate_id("CS-")
                    cs_num = f"CS-{idx+1:04d}/{cs_date.year}"
                    
                    chargesheets.append({
                        "chargesheet_id": cs_id,
                        "case_id": case_id,
                        "chargesheet_number": cs_num,
                        "filing_date": cs_date.date().isoformat(),
                        "investigating_officer_id": assigned_io,
                        "court_id": str(self.rng.choice(court_list)) if court_list else "",
                        "status": "Accepted",
                    })
                    
                    add_event("Chargesheet Filed", f"Chargesheet {cs_num} submitted to court.", cs_delay_days * 24)
                    
                    # 13. Court Proceedings
                    if status in ["PT (Pending Trial)", "Convicted", "Acquitted"]:
                        num_hearings = int(self.rng.integers(2, 6))
                        current_hearing_date = cs_date + timedelta(days=int(self.rng.integers(30, 90)))
                        
                        for h in range(num_hearings):
                            if current_hearing_date.year > self.config.years.end:
                                break
                                
                            proc_id = generate_id("CRT-")
                            is_final = (h == num_hearings - 1) and status in ["Convicted", "Acquitted"]
                            
                            ptype = "Final Argument" if is_final else str(self.rng.choice(["Framing of Charges", "Evidence", "Cross Examination"]))
                            pstatus = "Judgement" if is_final else "Adjourned"
                            
                            proceedings.append({
                                "proceeding_id": proc_id,
                                "case_id": case_id,
                                "court_id": str(self.rng.choice(court_list)) if court_list else "",
                                "hearing_date": current_hearing_date.date().isoformat(),
                                "proceeding_type": ptype,
                                "next_hearing_date": (current_hearing_date + timedelta(days=int(self.rng.integers(14, 60)))).date().isoformat() if not is_final else "",
                                "judge_name": f"Hon. Judge {self.rng.integers(1,50)}",
                                "prosecutor_name": f"PP {self.rng.integers(1,20)}",
                                "defense_counsel_name": f"Def {self.rng.integers(1,100)}",
                                "status": pstatus,
                                "remarks": "Case concluded." if is_final else "Witness absent."
                            })
                            
                            current_hearing_date += timedelta(days=int(self.rng.integers(14, 60)))

        all_events = pd.concat([crime_events, pd.DataFrame(new_events)], ignore_index=True)

        self.logger.info(f"Generated {len(investigation_diaries)} investigation diaries, {len(chargesheets)} chargesheets and {len(proceedings)} court proceedings.")

        return {
            "cases": updated_cases,
            "crime_events": all_events,
            "investigation_diaries": pd.DataFrame(investigation_diaries),
            "chargesheet_details": pd.DataFrame(chargesheets),
            "court_proceedings": pd.DataFrame(proceedings),
        }
