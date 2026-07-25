"""
Narrative Engine — creates consistent text narratives across the case lifecycle.
Generates Complaints, FIR narratives, and Witness Statements derived from a single core incident fact structure.

Depends on: crime, investigation
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime

from engines.base_engine import BaseEngine
from schemas.base import generate_id

class NarrativeEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "narrative"

    @property
    def dependencies(self) -> List[str]:
        return ["crime", "investigation"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating Consistent Narratives (Complaints, FIR Texts, Statements)...")

        cases = self.store.get("cases")
        complainants = self.store.get("complainants")
        
        if cases.empty or complainants.empty:
            return {}

        documents = []

        # Convert to dict for fast lookup
        comp_dict = complainants.groupby("case_id").first().to_dict("index")

        for _, row in cases.iterrows():
            case_id = row["case_id"]
            head = row["crime_head_name"]
            
            # Master Facts
            facts = {
                "time": row["time_of_incident_start"],
                "place": row["place_of_occurrence"],
                "crime": head.lower(),
                "complainant": "the complainant",
            }

            # If we can get complainant name
            if case_id in comp_dict:
                cid = comp_dict[case_id]["person_id"]
                # We could look up the person name from population, but for speed we'll mock it here
                facts["complainant"] = f"person {cid}"
                
            # Generate Complaint
            complaint_text = self._generate_complaint(head, facts)
            
            documents.append({
                "doc_id": generate_id("DOC-"),
                "case_id": case_id,
                "doc_type": "Complaint",
                "content": complaint_text,
                "author_id": comp_dict.get(case_id, {}).get("person_id", "Unknown"),
                "created_at": row["date_of_report"]
            })
            
            # Generate FIR text (formalized version of complaint)
            fir_text = self._generate_fir(head, facts)
            
            documents.append({
                "doc_id": generate_id("DOC-"),
                "case_id": case_id,
                "doc_type": "FIR Narrative",
                "content": fir_text,
                "author_id": row["station_id"],
                "created_at": row["date_of_report"]
            })
            
            # Generate Witness Statement
            if self.rng.random() > 0.5:
                witness_text = self._generate_witness_statement(head, facts)
                documents.append({
                    "doc_id": generate_id("DOC-"),
                    "case_id": case_id,
                    "doc_type": "Witness Statement",
                    "content": witness_text,
                    "author_id": generate_id("WIT-"),
                    "created_at": row["date_of_report"]
                })

        self.logger.info(f"Generated {len(documents)} narrative documents.")

        return {
            "narrative_documents": pd.DataFrame(documents)
        }

    def _generate_complaint(self, crime: str, facts: dict) -> str:
        templates = {
            "theft": [
                "I was at {place} around {time} when I noticed my belongings were missing.",
                "Someone stole my items near {place} at {time}.",
                "To the inspector, I wish to report a theft that occurred at {time} near {place}."
            ],
            "assault": [
                "I was attacked near {place} at {time}. They hit me suddenly.",
                "At {time} near {place}, I was assaulted by unknown persons.",
                "Please register a complaint. I was beaten up around {time} at {place}."
            ],
            "default": [
                "I am reporting an incident of {crime} that took place at {place} around {time}.",
                "An incident of {crime} occurred near {place} at {time}."
            ]
        }
        
        category = crime.lower() if crime.lower() in templates else "default"
        template = str(self.rng.choice(templates[category]))
        return template.format(**facts)

    def _generate_fir(self, crime: str, facts: dict) -> str:
        # Formal tone
        return f"Based on the complaint received, it is recorded that an offense of {facts['crime']} took place at {facts['place']}. The incident reportedly occurred at {facts['time']}. Investigation taken up."

    def _generate_witness_statement(self, crime: str, facts: dict) -> str:
        # Third party tone
        return f"I was passing by {facts['place']} at {facts['time']}. I saw the incident of {facts['crime']} happen in front of me."
