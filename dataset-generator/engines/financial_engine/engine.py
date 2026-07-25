"""
Financial Engine — generates Bank Accounts and Transactions.
Simulates financial trails for cyber fraud, hawala, and extortion.

Depends on: master, population, crime, gang
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from engines.base_engine import BaseEngine
from schemas.base import generate_id

class FinancialEngine(BaseEngine):

    @property
    def name(self) -> str:
        return "financial"

    @property
    def dependencies(self) -> List[str]:
        return ["master", "population", "crime", "gang"]

    def generate(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("Generating Bank Accounts and Financial Transactions...")

        population = self.store.get("persons")
        accused_records = self.store.get("accused_records")
        gangs = self.store.get("gangs")
        cases = self.store.get("cases")
        
        if population.empty or accused_records.empty:
            return {}

        accounts = []
        transactions = []
        
        # 1. Create bank accounts for accused and some victims
        # For performance, only generate for those involved in cases
        accused_ids = accused_records["person_id"].unique().tolist()
        
        # Get victims from cyber/fraud cases (financial crimes)
        financial_cases = cases[cases["crime_head_name"].isin(["Cyber Crime", "Cheating/Fraud", "Extortion"])]
        # We need the victims of these cases, but since victims are just IDs, let's create a pool
        # Actually we don't have victim person_ids easily available here unless we load victims table
        victims_table = self.store.get("victims") if "victims" in self.store.data else pd.DataFrame()
        victim_ids = victims_table["person_id"].tolist() if not victims_table.empty else []
        
        target_persons = list(set(accused_ids + victim_ids))
        
        account_map = {}
        banks = ["SBI", "HDFC", "ICICI", "Axis", "Canara", "Union Bank"]
        
        for pid in target_persons:
            acc_id = generate_id("ACC-")
            bank_name = str(self.rng.choice(banks))
            ifsc = f"{bank_name[:4].upper()}000{self.rng.integers(1000, 9999)}"
            acc_number = f"{self.rng.integers(10000000000, 99999999999)}"
            
            # Risk score higher for accused
            risk = float(self.rng.uniform(0.6, 1.0)) if pid in accused_ids else float(self.rng.uniform(0.0, 0.4))
            
            account_map[pid] = {
                "account_id": acc_id,
                "bank": bank_name,
                "ifsc": ifsc,
                "number": acc_number
            }
            
            accounts.append({
                "account_id": acc_id,
                "person_id": pid,
                "bank_name": bank_name,
                "account_number": acc_number,
                "ifsc_code": ifsc,
                "account_type": "Savings" if self.rng.random() > 0.1 else "Current",
                "risk_score": round(risk, 2),
                "is_frozen": risk > 0.8 and self.rng.random() > 0.5
            })

        # 2. Generate Fraud/Extortion Transactions
        # Link accused with victims in financial crimes
        for _, case_row in financial_cases.iterrows():
            cid = case_row["case_id"]
            incident_date = datetime.fromisoformat(case_row["date_of_incident_start"])
            
            c_accused = accused_records[accused_records["case_id"] == cid]["person_id"].tolist()
            if not victims_table.empty:
                c_victims = victims_table[victims_table["case_id"] == cid]["person_id"].tolist()
            else:
                c_victims = []
                
            if c_accused and c_victims:
                # Victim pays accused (fraud)
                for _ in range(int(self.rng.integers(1, 4))):
                    sender = str(self.rng.choice(c_victims))
                    receiver = str(self.rng.choice(c_accused))
                    
                    if sender in account_map and receiver in account_map:
                        amount = float(self.rng.integers(1000, 500000))
                        tx_date = incident_date - timedelta(hours=int(self.rng.integers(0, 48)))
                        
                        transactions.append({
                            "transaction_id": generate_id("TXN-"),
                            "sender_account_id": account_map[sender]["account_id"],
                            "receiver_account_id": account_map[receiver]["account_id"],
                            "amount": amount,
                            "transaction_date": tx_date.date().isoformat(),
                            "transaction_time": tx_date.time().strftime("%H:%M:%S"),
                            "transaction_type": str(self.rng.choice(["UPI", "IMPS", "NEFT", "RTGS"])),
                            "status": "Success",
                            "is_suspicious": True,
                            "remarks": f"Fraud transfer related to {cid}"
                        })
                        
                        # Graph Edge: TRANSACTS_WITH
                        self.store.add_edge(sender, "TRANSACTS_WITH", receiver, {"amount": amount, "type": "Fraud"})

        # 3. Gang money laundering (Hawala-like intra-gang transfers)
        if not gangs.empty:
            for _, gang in gangs.iterrows():
                gang_id = gang["gang_id"]
                members = accused_records[accused_records["gang_id"] == gang_id]["person_id"].tolist()
                
                if len(members) >= 2:
                    for _ in range(int(self.rng.integers(5, 20))):
                        sender = str(self.rng.choice(members))
                        receiver = str(self.rng.choice(members))
                        if sender != receiver and sender in account_map and receiver in account_map:
                            amount = float(self.rng.integers(50000, 1000000))
                            tx_date = datetime.now() - timedelta(days=int(self.rng.integers(1, 365)))
                            
                            transactions.append({
                                "transaction_id": generate_id("TXN-"),
                                "sender_account_id": account_map[sender]["account_id"],
                                "receiver_account_id": account_map[receiver]["account_id"],
                                "amount": amount,
                                "transaction_date": tx_date.date().isoformat(),
                                "transaction_time": tx_date.time().strftime("%H:%M:%S"),
                                "transaction_type": "IMPS",
                                "status": "Success",
                                "is_suspicious": True,
                                "remarks": "High-value intra-gang transfer"
                            })
                            
                            # Graph Edge: TRANSACTS_WITH
                            self.store.add_edge(sender, "TRANSACTS_WITH", receiver, {"amount": amount, "type": "Hawala"})

        self.logger.info(f"Generated {len(accounts)} bank accounts and {len(transactions)} financial transactions.")

        return {
            "bank_accounts": pd.DataFrame(accounts),
            "financial_transactions": pd.DataFrame(transactions),
        }
