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
S_DRIVE_MARY_SHEET = "/Volumes/jennings-data$/ACCTNG/PERSONAL/MCA/2026 DAILY $.xlsx"

LOCAL_CACHE_DIR = os.path.abspath("live_skyline_fast_mirror/tax_certs")
LOCAL_MDB = os.path.join(LOCAL_CACHE_DIR, "CollarCountiesCertificates_be.mdb")
LOCAL_MARY_ENC = os.path.join(LOCAL_CACHE_DIR, "Mary_2026_DAILY_enc.xlsx")
LOCAL_MARY_DEC = os.path.join(LOCAL_CACHE_DIR, "Mary_2026_DAILY_decrypted.xlsx")

OUTPUT_JSON = os.path.abspath("tax_activity_summary.json")

def sync_local_mdb_copy(verbose=True):
    """Safely performs a read-only copy of the S: drive Access database and Mary's sheet."""
    os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)
    
    # 1. Sync Jim DiGiacomo's Access database
    if os.path.exists(S_DRIVE_MDB):
        if not os.path.exists(LOCAL_MDB) or abs(os.stat(S_DRIVE_MDB).st_mtime - os.stat(LOCAL_MDB).st_mtime) > 3:
            t0 = time.time()
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}] 🔄 Copying live tax database from S: drive...", flush=True)
            shutil.copyfile(S_DRIVE_MDB, LOCAL_MDB)
            shutil.copystat(S_DRIVE_MDB, LOCAL_MDB)
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}] ✅ Copied tax database in {time.time() - t0:.2f}s")
        elif verbose:
            print(f"[{time.strftime('%H:%M:%S')}] ⚡ Local tax database is already fresh.")

    # 2. Sync & Decrypt Mary's Daily Cash Sheet
    if os.path.exists(S_DRIVE_MARY_SHEET):
        if not os.path.exists(LOCAL_MARY_ENC) or abs(os.stat(S_DRIVE_MARY_SHEET).st_mtime - os.stat(LOCAL_MARY_ENC).st_mtime) > 3:
            t0 = time.time()
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}] 🔄 Copying Mary's Daily Cash Sheet from S: drive...", flush=True)
            shutil.copyfile(S_DRIVE_MARY_SHEET, LOCAL_MARY_ENC)
            shutil.copystat(S_DRIVE_MARY_SHEET, LOCAL_MARY_ENC)
            
            # Decrypt with password Beach147
            import msoffcrypto
            with open(LOCAL_MARY_ENC, "rb") as f_enc:
                office_file = msoffcrypto.OfficeFile(f_enc)
                office_file.load_key(password="Beach147")
                with open(LOCAL_MARY_DEC, "wb") as f_dec:
                    office_file.decrypt(f_dec)
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}] ✅ Decrypted Mary's sheet in {time.time() - t0:.2f}s")
        elif verbose:
            print(f"[{time.strftime('%H:%M:%S')}] ⚡ Local Mary's sheet is already fresh.")

    return os.path.exists(LOCAL_MDB) and os.path.exists(LOCAL_MARY_DEC)

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

    # 3. Parse Mary's Reconciled Daily Cash Inflows / Outflows
    mary_weekly = {
        "this_week_inflows": 0.0,
        "this_week_outflows": 0.0,
        "monday_inflows": 0.0,
        "daily_breakdown": []
    }
    
    if os.path.exists(LOCAL_MARY_DEC):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(LOCAL_MARY_DEC, data_only=True)
            if "OCT 2026" in wb.sheetnames:
                ws = wb["OCT 2026"]
                daily_reconciled = []
                # Rows 541 to 585 contains the daily reconciled additions/disbursements
                for r in range(541, 587, 2):
                    d_val = ws.cell(r, 10).value
                    if d_val is None:
                        continue
                    d_str = str(d_val)[:10]

                    # Inflows
                    if_in = float(ws.cell(r, 11).value or 0.0)
                    cb_in = float(ws.cell(r, 12).value or 0.0)
                    dq_in = float(ws.cell(r, 13).value or 0.0)
                    ut_in = float(ws.cell(r, 14).value or 0.0)
                    tot_in = if_in + cb_in + dq_in + ut_in

                    # Outflows
                    if_out = float(ws.cell(r+1, 11).value or 0.0)
                    cb_out = float(ws.cell(r+1, 12).value or 0.0)
                    dq_out = float(ws.cell(r+1, 13).value or 0.0)
                    ut_out = float(ws.cell(r+1, 14).value or 0.0)
                    tot_out = if_out + cb_out + dq_out + ut_out

                    if tot_in != 0 or tot_out != 0:
                        entry = {
                            "date": d_str,
                            "inflows": tot_in,
                            "outflows": tot_out,
                            "cb_in": cb_in,
                            "if_in": if_in,
                            "dq_in": dq_in,
                            "ut_in": ut_in,
                            "net": tot_in + tot_out
                        }
                        daily_reconciled.append(entry)
                        if d_str == "2026-10-19":
                            mary_weekly["monday_inflows"] = tot_in

                mary_weekly["daily_breakdown"] = daily_reconciled
                tw_days = ["2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23"]
                tw_entries = [d for d in daily_reconciled if d["date"] in tw_days]
                mary_weekly["this_week_inflows"] = sum(d["inflows"] for d in tw_entries)
                mary_weekly["this_week_outflows"] = sum(d["outflows"] for d in tw_entries)
                mary_weekly["this_week_net"] = mary_weekly["this_week_inflows"] + mary_weekly["this_week_outflows"]
                mary_weekly["month_total_inflows"] = sum(d["inflows"] for d in daily_reconciled)
                mary_weekly["month_total_outflows"] = sum(d["outflows"] for d in daily_reconciled)
        except Exception as e:
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Note parsing Mary's sheet: {e}")

    result = {
        "as_of_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mary_daily_cash": mary_weekly,
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
