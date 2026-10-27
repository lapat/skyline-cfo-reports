#!/usr/bin/env python3
"""
hunt_subtax_opportunities.py -- Automated Cross-County Subtax Priority Hunter

Scans all unredeemed certificates owned by Jennings (Central Buyer, Interstate,
Diamond Quest, etc.) in CollarCountiesCertificates_be.mdb, and cross-references
against upcoming county tax sale lists to detect properties where Jennings has
exclusive priority to pay subsequent taxes (subtaxes) directly to the County
Collector, locking in the statutory 12% per year interest rate and bypassing
competitive auction bidding.
"""

import os
import sys
import csv
import json
import time
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT_DIR / "live_skyline_fast_mirror" / "tax_certs" / "CollarCountiesCertificates_be.mdb"
OUTPUT_JSON = ROOT_DIR / "subtax_opportunities_summary.json"
OUTPUT_CSV = ROOT_DIR / "data" / "subtax_payment_request_for_mary.csv"

# County Mapping from tbl_Counties
COUNTY_MAP = {
    "1": "Whiteside",
    "2": "Lake",
    "3": "DuPage",
    "4": "Kane",
    "5": "Kankakee",
    "6": "Will",
    "7": "DeKalb",
    "8": "McHenry",
    "10": "Winnebago",
    "21": "Boone",
    "25": "Kendall"
}

def clean_pin(pin):
    if not pin:
        return ""
    return str(pin).strip().replace("-", "").replace(" ", "").replace(".", "")

def format_pin_display(pin, county):
    # Add standard dashes back if needed
    p = str(pin).strip()
    if county == "Lake" and len(p) == 10 and "-" not in p:
        return f"{p[:2]}-{p[2:4]}-{p[4:7]}-{p[7:]}"
    return p

def get_active_certificates():
    if not DB_PATH.exists():
        print(f"❌ Error: {DB_PATH} not found.")
        return {}

    # Query tblCertificates using mdb-export
    proc = subprocess.Popen(['mdb-export', str(DB_PATH), 'tblCertificates'], stdout=subprocess.PIPE, text=True)
    reader = csv.DictReader(proc.stdout)
    
    active_certs = {}
    for r in reader:
        date_redeemed = (r.get('DateRedeemed') or '').strip()
        if not date_redeemed:
            pin = (r.get('PropertyNo') or '').strip()
            county_id = (r.get('County') or '').strip()
            if pin:
                clean = clean_pin(pin)
                # Store by clean PIN and county
                key = f"{county_id}_{clean}"
                active_certs[key] = r
                # Also index by clean PIN alone for fallback
                active_certs[clean] = r
                
    proc.stdout.close()
    proc.wait()
    return active_certs

def scan_lake_county(active_certs):
    lake_csv = ROOT_DIR / "data" / "lake_2026_sale" / "2026 Lake List 2025 Taxes.csv"
    if not lake_csv.exists():
        return []

    matches = []
    with open(lake_csv, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pin_raw = (row.get("Parcel Number") or "").strip()
            clean = clean_pin(pin_raw)
            
            # Check key with County '2' (Lake) or direct clean PIN
            cert = active_certs.get(f"2_{clean}") or active_certs.get(clean)
            if cert and cert.get("County") == "2":
                amt_str = (row.get("Judgment Amount") or "0").replace("$", "").replace(",", "").strip()
                try:
                    due = float(amt_str)
                except ValueError:
                    due = 0.0

                orig_amt = float(cert.get("CertificateAmount") or 0.0)
                subtax_yield = due * 0.12
                
                matches.append({
                    "county": "Lake",
                    "county_id": "2",
                    "pin": pin_raw,
                    "taxpayer_name": (row.get("Taxpayer Name") or "").strip(),
                    "property_address": (row.get("Property Address 1") or "").strip(),
                    "city": (row.get("Property City") or "").strip(),
                    "township": (row.get("Township") or "").strip(),
                    "tax_due": round(due, 2),
                    "annual_12pct_interest": round(subtax_yield, 2),
                    "certificate_owner": (cert.get("CertificateOwner") or "UNKNOWN").strip(),
                    "certificate_no": (cert.get("CertificateNo") or "").strip(),
                    "cert_tax_year": (cert.get("TaxYear") or "").strip(),
                    "original_cert_amount": round(orig_amt, 2),
                    "status": "URGENT - Post Prior to Nov 13 Sale"
                })
    return matches

def run_subtax_hunter(verbose=True):
    t0 = time.time()
    if verbose:
        print("=" * 80)
        print("🔍 HUNTING MULTI-COUNTY SUBTAX OPPORTUNITIES (Collar Counties)")
        print("=" * 80)

    active_certs = get_active_certificates()
    if verbose:
        print(f"Loaded {len(active_certs)} unredeemed portfolio certificates from Access DB.")

    all_matches = []
    
    # 1. Lake County
    lake_matches = scan_lake_county(active_certs)
    all_matches.extend(lake_matches)

    # Sort matches by Tax Due descending
    all_matches.sort(key=lambda x: x["tax_due"], reverse=True)

    # Summaries
    total_due = sum(m["tax_due"] for m in all_matches)
    total_yield = sum(m["annual_12pct_interest"] for m in all_matches)
    
    owner_breakdown = {}
    for m in all_matches:
        o = m["certificate_owner"]
        owner_breakdown[o] = owner_breakdown.get(o, 0.0) + m["tax_due"]

    summary = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_subtax_parcels": len(all_matches),
        "total_subtax_capital_required": round(total_due, 2),
        "total_projected_12pct_annual_interest": round(total_yield, 2),
        "owner_breakdown": {k: round(v, 2) for k, v in owner_breakdown.items()},
        "opportunities": all_matches
    }

    # Save JSON for Dashboard
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save Check Request CSV for Mary
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "County", "PIN", "Taxpayer / Property", "Certificate Owner",
            "Cert #", "Prior Tax Year", "Original Cert Amount", "Subtax Amount Due (Pay to County)",
            "12% Annual Interest Earned", "Action / Instructions"
        ])
        for m in all_matches:
            writer.writerow([
                m["county"],
                m["pin"],
                f"{m['taxpayer_name']} ({m['city']})",
                m["certificate_owner"],
                m["certificate_no"],
                m["cert_tax_year"],
                f"${m['original_cert_amount']:,.2f}",
                f"${m['tax_due']:,.2f}",
                f"${m['annual_12pct_interest']:,.2f}",
                "SUBTAX PAYMENT REQUEST - Submit check to County Collector before tax sale"
            ])

    if verbose:
        print(f"✅ Found {len(all_matches)} Priority Subtax Parcels across active lists.")
        print(f"💰 Total Subtax Capital: ${total_due:,.2f}")
        print(f"📈 Guaranteed 12% Annual Yield: +${total_yield:,.2f}/yr")
        print(f"📁 JSON Generated: {OUTPUT_JSON}")
        print(f"📄 Check Request Generated: {OUTPUT_CSV}")
        print("=" * 80)

    return summary

if __name__ == "__main__":
    run_subtax_hunter(verbose=True)
