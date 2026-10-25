#!/usr/bin/env python3
"""
High-Speed Read-Only Extractor for Live Tax Certificate Redemptions & Purchases.

Source:
  Primary S: Drive: /Volumes/jennings-data$/Collar Counties/CollarCountiesCertificates_be.mdb
  (Strictly read-only plain copy, never opens or writes network path)

Output:
  tax_activity_summary.json (structured metrics for portal & morning email)
"""

import os
import sys
import shutil
import subprocess
import csv
import json
import time
from datetime import datetime

S_DRIVE_MDB = "/Volumes/jennings-data$/Collar Counties/CollarCountiesCertificates_be.mdb"
LOCAL_CACHE_DIR = os.path.abspath("live_skyline_fast_mirror/tax_certs")
LOCAL_MDB = os.path.join(LOCAL_CACHE_DIR, "CollarCountiesCertificates_be.mdb")
OUTPUT_JSON = os.path.abspath("tax_activity_summary.json")

def sync_local_mdb_copy(verbose=True):
    """Safely performs a read-only copy of the S: drive Access database to local NVMe."""
    if not os.path.exists(S_DRIVE_MDB):
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] ⚠️ S: drive tax database not found at {S_DRIVE_MDB}", file=sys.stderr)
        return os.path.exists(LOCAL_MDB)

    os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)
    
    # Delta copy check
    if os.path.exists(LOCAL_MDB):
        s_stat = os.stat(S_DRIVE_MDB)
        l_stat = os.stat(LOCAL_MDB)
        if s_stat.st_size == l_stat.st_size and abs(s_stat.st_mtime - l_stat.st_mtime) < 3:
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}] ⚡ Local tax database copy is already up to date ({s_stat.st_size / 1e6:.1f} MB).")
            return True

    t0 = time.time()
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] 🔄 Copying live tax database from S: drive ({os.path.getsize(S_DRIVE_MDB) / 1e6:.1f} MB)...", flush=True)
    
    shutil.copyfile(S_DRIVE_MDB, LOCAL_MDB)
    shutil.copystat(S_DRIVE_MDB, LOCAL_MDB)
    
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Copied tax database in {time.time() - t0:.2f}s")
    return True

def extract_tax_activity(verbose=True):
    """Parses redemptions and purchases from local MDB copy via mdb-export."""
    if not os.path.exists(LOCAL_MDB):
        print(f"Error: {LOCAL_MDB} does not exist!", file=sys.stderr)
        return None

    t0 = time.time()
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] ⚙️ Parsing live certificate redemptions and purchases via mdbtools...")

    # 1. Parse Redemptions from tblCertificates
    proc = subprocess.Popen(["mdb-export", LOCAL_MDB, "tblCertificates"], stdout=subprocess.PIPE, text=True)
    reader = csv.DictReader(proc.stdout)

    oct_redemptions = []
    ytd_redemptions_2026 = []
    
    county_names = {
        "1": "Cook", "2": "Lake", "3": "DuPage", "4": "Kane", "5": "Champaign",
        "6": "Will", "8": "McHenry", "10": "Tazewell", "12": "Kendall",
        "18": "DeKalb", "23": "Grundy", "25": "Boone", "26": "Winnebago",
        "28": "LaSalle", "51": "Cook Scavenger"
    }

    for r in reader:
        dr = (r.get("DateRedeemed") or "")[:8]
        dp = (r.get("DateOfPayOff") or "")[:8]
        ru = (r.get("RecUpdateed") or "")[:8]

        # Check if 2026 event
        is_2026 = dr.endswith("/26") or dp.endswith("/26") or ru.endswith("/26")
        if not is_2026:
            continue

        c_amt = float(r.get("CertificateAmount") or 0.0)
        p_amt = float(r.get("CountyPayOff") or 0.0)
        if p_amt == 0.0 and c_amt > 0.0:
            p_amt = c_amt # Fallback if payoff not yet entered

        cid = str(r.get("County") or "").strip()
        cname = county_names.get(cid, f"County {cid}")

        item = {
            "county_id": cid,
            "county_name": cname,
            "cert_no": r.get("CertificateNo") or "",
            "pin": r.get("PropertyNo") or "",
            "date_redeemed": dr,
            "date_payoff": dp,
            "date_updated": ru,
            "principal": c_amt,
            "payoff": p_amt,
            "profit": p_amt - c_amt,
            "owner": r.get("CertificateOwner") or "",
            "check_no": r.get("CheckNo") or ""
        }

        ytd_redemptions_2026.append(item)

        # Check if October 2026
        if dr.startswith("10/") or dp.startswith("10/") or ru.startswith("10/"):
            oct_redemptions.append(item)

    proc.stdout.close()
    proc.wait()

    # Sort October redemptions by payoff descending
    oct_redemptions.sort(key=lambda x: x["payoff"], reverse=True)

    oct_total_payoff = sum(x["payoff"] for x in oct_redemptions)
    oct_total_principal = sum(x["principal"] for x in oct_redemptions)
    oct_total_profit = oct_total_payoff - oct_total_principal

    # 2. Parse Subtax Disbursements from tblSubTaxes
    proc_sub = subprocess.Popen(["mdb-export", LOCAL_MDB, "tblSubTaxes"], stdout=subprocess.PIPE, text=True)
    reader_sub = csv.DictReader(proc_sub.stdout)

    recent_subtaxes = []
    for r in reader_sub:
        dp = (r.get("DatePaid") or "")[:8]
        if dp.endswith("/26") and dp.startswith(("09/", "10/")):
            recent_subtaxes.append({
                "date": dp,
                "county": r.get("County"),
                "cert": r.get("CertificateNo"),
                "amount": float(r.get("TaxAmount") or 0.0),
                "status": r.get("SubtaxStatus"),
                "check": r.get("CheckNo")
            })
    proc_sub.stdout.close()
    proc_sub.wait()

    total_subtax_outflow = sum(x["amount"] for x in recent_subtaxes)

    result = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "october_redemptions": {
            "count": len(oct_redemptions),
            "total_collected": oct_total_payoff,
            "principal_recovered": oct_total_principal,
            "net_profit_earned": oct_total_profit,
            "top_redemptions": oct_redemptions[:12]
        },
        "ytd_2026_redemptions": {
            "count": len(ytd_redemptions_2026),
            "total_collected": sum(x["payoff"] for x in ytd_redemptions_2026),
            "principal_recovered": sum(x["principal"] for x in ytd_redemptions_2026),
            "net_profit_earned": sum(x["profit"] for x in ytd_redemptions_2026)
        },
        "recent_subtax_purchases": {
            "count": len(recent_subtaxes),
            "total_deployed": total_subtax_outflow,
            "sample_payments": recent_subtaxes[:8]
        }
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Tax certificate extraction complete in {time.time() - t0:.2f}s")
        print(f"  October Redemptions Collected: ${oct_total_payoff:,.2f} ({len(oct_redemptions)} certificates)")
        print(f"  October Net Profit / Interest: ${oct_total_profit:,.2f}")
        print(f"  Recent Subtax Capital Deployed: ${total_subtax_outflow:,.2f}")
        print(f"  Saved structured metrics -> {OUTPUT_JSON}")

    return result

if __name__ == "__main__":
    sync_local_mdb_copy(verbose=True)
    extract_tax_activity(verbose=True)
