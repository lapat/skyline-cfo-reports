#!/usr/bin/env python3
"""
Safe General Ledger Entry Staging Tool for Skyline.

Constructs pre-validated journal entries for Skyline's native CSV import engine.
Enforces the mandatory rule: DO NOT WRITE TO SKYLINE WITHOUT EXPLICIT USER APPROVAL.
"""

import sys
import os
from typing import List, Dict, Any
from skyline_db import SkylineIntegration

def validate_and_stage_batch(entries: List[Dict[str, Any]], output_csv_path: str):
    """
    Validates a batch of journal entries and stages them to a CSV file.
    Checks that total debits equal total credits before exporting.
    """
    print("\n==================================================")
    print("Skyline GL Entry Staging Review")
    print("==================================================")
    
    total_debit = 0.0
    total_credit = 0.0

    print(f"{'Company':<10} {'Account':<12} {'Description':<25} {'Amount ($)':>12}")
    print("-" * 65)

    for entry in entries:
        amt = float(entry["amount"])
        if amt > 0:
            total_debit += amt
        else:
            total_credit += abs(amt)
            
        print(f"{entry['company_code']:<10} {entry['gl_account']:<12} {entry['description'][:25]:<25} {amt:>12,.2f}")

    print("-" * 65)
    print(f"Total Debits:  ${total_debit:,.2f}")
    print(f"Total Credits: ${total_credit:,.2f}")
    variance = round(total_debit - total_credit, 2)
    print(f"Net Variance:  ${variance:,.2f}")

    if variance != 0.0:
        print("\n❌ VALIDATION ERROR: Total debits do not equal total credits!")
        print("This entry is unbalanced and will NOT be staged.")
        return False

    print("\n✅ Balance Check Passed (Debits == Credits).")
    print(f"Target Output File: {output_csv_path}")
    print("\n⚠️  MANDATE CHECK: Under GEMINI.md guidelines, no writes to Skyline")
    print("can proceed without explicit user confirmation.")
    
    confirm = input("Confirm staging this batch to CSV? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("Staging cancelled by user. No files written.")
        return False

    integration = SkylineIntegration()
    integration.write_gl_import_csv(entries, output_csv_path)
    print(f"✨ Successfully generated Skyline GL Import CSV at: {output_csv_path}")
    print("You can now import this file natively via the Skyline desktop client.")
    return True

if __name__ == "__main__":
    # Example balanced entry: Accrued revenue or intercompany transfer
    sample_entries = [
        {
            "company_code": "001",
            "post_date": "2026-10-20",
            "gl_account": "1010-00",
            "description": "Sample Cash Transfer Debit",
            "amount": 5000.00
        },
        {
            "company_code": "001",
            "post_date": "2026-10-20",
            "gl_account": "3100-00",
            "description": "Sample Revenue Credit",
            "amount": -5000.00
        }
    ]
    
    validate_and_stage_batch(sample_entries, "sample_gl_import.csv")
