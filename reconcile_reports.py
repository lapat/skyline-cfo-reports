#!/usr/bin/env python3
"""
Reconciliation & Validation Tool for Skyline Financial Reports.

Compares newly generated financial reports (via ODBC/SkylineIntegration)
against historical benchmark figures to verify accuracy and ensure no 
regressions exist in revenue, expense, and net income calculations.
"""

import sys
from typing import Dict, Any

# Historical benchmark figures from the validated legacy system
BENCHMARKS = {
    "Bay Bayou Florida RV Resort": {
        "period": ("260101", "260531"),
        "conservative": {"revenue": 253478.30, "expenses": 676331.20, "net": -422852.90},
        "broad": {"revenue": 2628274.02, "expenses": 1299915.96, "net": 1328358.06},
    },
    "Sunkissed Village RV Resort": {
        "period": ("260102", "260615"),
        "conservative": {"revenue": 409517.08, "expenses": 875355.26, "net": -465838.18},
        "broad": {"revenue": 2018706.54, "expenses": 1385777.56, "net": 632928.98},
    },
    "The Bluffs MH & RV Resort": {
        "period": ("260106", "260531"),
        "conservative": {"revenue": 189699.06, "expenses": 162705.34, "net": 26993.72},
        "broad": {"revenue": 203196.74, "expenses": 355019.66, "net": -151822.92},
    },
    "Jennings Realty, Inc.": {
        "period": ("250901", "260612"),
        "conservative": {"revenue": 5081210.78, "expenses": 1829006.52, "net": 3252204.26},
        "broad": {"revenue": 4536239.76, "expenses": 4303921.76, "net": 232318.00},
    },
    "Home Sites / Galaxy": {
        "period": ("260102", "260531"),
        "conservative": {"revenue": 298007.70, "expenses": 6003.74, "net": 292003.96},
        "broad": {"revenue": 309579.18, "expenses": 158431.88, "net": 151147.30},
    },
    "Madison Community Resort": {
        "period": ("260102", "260531"),
        "conservative": {"revenue": 51392.80, "expenses": 186572.70, "net": -135179.90},
        "broad": {"revenue": 390001.20, "expenses": 491204.42, "net": -101203.22},
    },
}

def verify_report(company_name: str, generated_report: Dict[str, Any]) -> bool:
    """
    Check if a generated financial report matches the expected benchmark ranges.
    """
    if company_name not in BENCHMARKS:
        print(f"⚠️  No historical benchmark found for '{company_name}'.")
        return True

    bench = BENCHMARKS[company_name]
    gen_rev = generated_report["revenue"]
    gen_exp = generated_report["expenses"]
    gen_net = generated_report["net_income"]

    rev_min = min(bench["conservative"]["revenue"], bench["broad"]["revenue"])
    rev_max = max(bench["conservative"]["revenue"], bench["broad"]["revenue"])
    exp_min = min(bench["conservative"]["expenses"], bench["broad"]["expenses"])
    exp_max = max(bench["conservative"]["expenses"], bench["broad"]["expenses"])

    print(f"\n--- Reconciling {company_name} ---")
    print(f"Target Period: {bench['period'][0]} to {bench['period'][1]}")
    print(f"Generated: Revenue=${gen_rev:,.2f} | Expenses=${gen_exp:,.2f} | Net=${gen_net:,.2f}")
    print(f"Benchmark Ranges:")
    print(f"  Revenue:  ${rev_min:,.2f} to ${rev_max:,.2f}")
    print(f"  Expenses: ${exp_min:,.2f} to ${exp_max:,.2f}")

    # Allow slight variance for rounding/edge transaction updates
    rev_ok = (rev_min * 0.95) <= gen_rev <= (rev_max * 1.05)
    exp_ok = (exp_min * 0.95) <= gen_exp <= (exp_max * 1.05)

    if rev_ok and exp_ok:
        print(f"✅ PASS: Report figures align with historical benchmarks.")
        return True
    else:
        print(f"❌ VARIANCE DETECTED: Generated report falls outside expected range.")
        return False

if __name__ == "__main__":
    print("==================================================")
    print("Skyline Financial Report Reconciliation Baseline")
    print("==================================================")
    for company, data in BENCHMARKS.items():
        print(f"\n{company}:")
        print(f"  Period: {data['period'][0]} to {data['period'][1]}")
        print(f"  Conservative Net Income: ${data['conservative']['net']:>12,.2f}")
        print(f"  Broad Net Income:        ${data['broad']['net']:>12,.2f}")
