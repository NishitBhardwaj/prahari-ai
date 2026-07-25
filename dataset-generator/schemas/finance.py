"""
Financial schemas.
Bank accounts, transactions, UPI records, and suspicious activity flags.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import Field
from .base import AuditModel, generate_id


class BankAccount(AuditModel):
    """A bank account belonging to a person."""
    account_id: str = Field(default_factory=lambda: generate_id("BACC-"))
    person_id: str
    bank_name: str
    branch_name: str = ""
    branch_code: str = ""
    account_number: str
    account_type: str = "Savings"  # Savings, Current, Fixed Deposit
    ifsc_code: str = ""
    opening_date: date
    balance: float = 0.0
    is_active: bool = True
    is_joint: bool = False
    joint_holder_id: str = ""
    is_suspicious: bool = False
    kyc_verified: bool = True


class Transaction(AuditModel):
    """A financial transaction."""
    transaction_id: str = Field(default_factory=lambda: generate_id("TXN-"))
    from_account_id: str
    to_account_id: str = ""
    from_person_id: str
    to_person_id: str = ""
    transaction_datetime: datetime
    amount: float
    transaction_type: str  # Credit, Debit, Transfer, ATM Withdrawal, ATM Deposit
    transaction_mode: str = ""  # NEFT, RTGS, IMPS, UPI, Cash, Cheque, Card
    reference_number: str = ""
    description: str = ""
    status: str = "Completed"  # Completed, Pending, Failed, Reversed
    is_suspicious: bool = False
    suspicion_reason: str = ""
    linked_case_id: str = ""
    merchant_name: str = ""
    merchant_category: str = ""
    location: str = ""


class UPIRecord(AuditModel):
    """A UPI payment record."""
    upi_id: str = Field(default_factory=lambda: generate_id("UPI-"))
    sender_vpa: str  # name@upi format
    receiver_vpa: str
    sender_person_id: str
    receiver_person_id: str = ""
    amount: float
    transaction_datetime: datetime
    reference_number: str = ""
    status: str = "Success"  # Success, Failed, Pending
    remarks: str = ""
    app_name: str = ""  # PhonePe, GPay, Paytm, etc.
    is_suspicious: bool = False
    linked_case_id: str = ""
    merchant_name: str = ""
