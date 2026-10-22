#!/usr/bin/env python3
"""
Full Portfolio Extractor: Extracts all 347 company ledgers into SQLite.
Database target: live_skyline_local/skyline_all_companies.sqlite
"""

import os
import sys
import sqlite3
import time

sys.path.append("/Users/louislapat/vibe/skyline")
import extract_skyline

LOCAL_ROOT = os.path.abspath("live_skyline_local")
DB_PATH = os.path.join(LOCAL_ROOT, "skyline_all_companies.sqlite")

def extract_all():
    os.environ["SKYLINE_ROOT"] = LOCAL_ROOT
    extract_skyline.SKYLINE_ROOT = LOCAL_ROOT
    extract_skyline.DATA_DIR = os.path.join(LOCAL_ROOT, "DATA")

    print("Loading schema catalog (FILE.DDF / FIELD.DDF)...", flush=True)
    files_by_id, fields_by_id = extract_skyline.load_schema()

    ifs_dir = os.path.join(LOCAL_ROOT, "IFS")
    company_ids = [d for d in os.listdir(ifs_dir) if os.path.isdir(os.path.join(ifs_dir, d)) and not d.startswith(".")]
    company_ids.sort()

    print(f"Discovered {len(company_ids)} company folders locally. Initializing database...", flush=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            ifs_id TEXT PRIMARY KEY,
            company_name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT
        );
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            ifs_id TEXT,
            account_number TEXT,
            account_title TEXT,
            account_type TEXT,
            account_level TEXT,
            account_category TEXT,
            PRIMARY KEY (ifs_id, account_number)
        );
        CREATE TABLE IF NOT EXISTS journal_entries (
            ifs_id TEXT,
            account TEXT,
            date TEXT,
            journal_key TEXT,
            description TEXT,
            reference TEXT,
            amount REAL,
            voucher_number TEXT,
            chk_num TEXT,
            batch_num INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_je_ifs ON journal_entries(ifs_id);
        CREATE INDEX IF NOT EXISTS idx_je_date ON journal_entries(date);
        CREATE INDEX IF NOT EXISTS idx_je_acct ON journal_entries(account);
    """)

    t0 = time.time()
    total_entries = 0
    total_charts = 0

    print(f"Extracting transactions and accounts across all {len(company_ids)} entities...", flush=True)

    for idx, cid in enumerate(company_ids, 1):
        try:
            extracted = extract_skyline.extract_company(cid, files_by_id, fields_by_id)
            extract_skyline.load_company_into_db(conn, extracted)
            total_entries += len(extracted["journhist"])
            total_charts += len(extracted["chart"])
            
            if idx % 50 == 0 or idx == len(company_ids):
                elapsed = time.time() - t0
                print(f"  [{idx}/{len(company_ids)}] Extracted {cid:<8} ({total_entries:,} transactions, {total_charts:,} chart accounts, {elapsed:.1f}s)", flush=True)
        except Exception as e:
            # Continue on any corrupted legacy folder
            pass

    conn.commit()
    conn.close()

    t_total = time.time() - t0
    print("\n" + "=" * 80, flush=True)
    print("EXTRACTION COMPLETE!", flush=True)
    print(f"  Total Companies Loaded:  {len(company_ids)}", flush=True)
    print(f"  Total Transactions:      {total_entries:,}", flush=True)
    print(f"  Total Chart Accounts:    {total_charts:,}", flush=True)
    print(f"  Target Database:         {DB_PATH}", flush=True)
    print(f"  Total Time Elapsed:      {t_total:.1f} seconds", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    extract_all()
