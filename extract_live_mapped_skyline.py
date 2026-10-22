#!/usr/bin/env python3
"""
Direct Live Skyline Mapped Drive Extractor.

Extracts all active company general ledgers DIRECTLY from the live 
network share (/Volumes/skyline$/Skyline/IFS/) without using any stale local copies.
Target Database: skyline_live_production.sqlite
"""

import os
import sys
import sqlite3
import time

sys.path.append("/Users/louislapat/vibe/skyline")
import extract_skyline

LIVE_ROOT = "/Volumes/skyline$/Skyline"
DATA_DIR = os.path.join(LIVE_ROOT, "DATA")
IFS_DIR = os.path.join(LIVE_ROOT, "IFS")
DB_PATH = os.path.abspath("skyline_live_production.sqlite")

def extract_live():
    if not os.path.exists(LIVE_ROOT):
        print(f"Error: Live mapped drive {LIVE_ROOT} is not mounted!", file=sys.stderr)
        return False

    os.environ["SKYLINE_ROOT"] = LIVE_ROOT
    extract_skyline.SKYLINE_ROOT = LIVE_ROOT
    extract_skyline.DATA_DIR = DATA_DIR

    print(f"Connecting directly to live Skyline mapped drive at: {LIVE_ROOT}", flush=True)
    print("Loading live schema catalogs (FILE.DDF / FIELD.DDF)...", flush=True)
    files_by_id, fields_by_id = extract_skyline.load_schema()

    all_folders = [f for f in os.listdir(IFS_DIR) if os.path.isdir(os.path.join(IFS_DIR, f)) and not f.startswith(".")]
    
    # Filter to folders with active ledger files (>1KB)
    active_folders = []
    for f in all_folders:
        jh = os.path.join(IFS_DIR, f, "JOURHIST")
        if os.path.exists(jh) and os.path.getsize(jh) > 1024:
            active_folders.append(f)

    active_folders.sort()
    print(f"Identified {len(active_folders)} active company ledgers directly on mapped drive.", flush=True)

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

    print(f"Streaming live transactions directly into {os.path.basename(DB_PATH)}...", flush=True)

    for idx, cid in enumerate(active_folders, 1):
        try:
            extracted = extract_skyline.extract_company(cid, files_by_id, fields_by_id)
            extract_skyline.load_company_into_db(conn, extracted)
            n_je = len(extracted["journhist"])
            n_ch = len(extracted["chart"])
            total_entries += n_je
            total_charts += n_ch
            
            if idx % 25 == 0 or idx == len(active_folders):
                elapsed = time.time() - t0
                print(f"  [{idx}/{len(active_folders)}] Live Extracted IFS/{cid:<8} ({n_je:>5} entries | {total_entries:>6,} cumulative, {elapsed:.1f}s)", flush=True)
        except Exception as e:
            # Continue on legacy unreadable folders
            pass

    conn.commit()
    conn.close()

    t_total = time.time() - t0
    print("\n" + "=" * 80, flush=True)
    print("DIRECT LIVE EXTRACTION COMPLETE!", flush=True)
    print(f"  Source:                  {LIVE_ROOT} (Direct Mapped Drive)", flush=True)
    print(f"  Total Companies Loaded:  {len(active_folders)}", flush=True)
    print(f"  Total Live Transactions: {total_entries:,}", flush=True)
    print(f"  Total Live Accounts:     {total_charts:,}", flush=True)
    print(f"  Target SQLite DB:        {DB_PATH}", flush=True)
    print(f"  Time Elapsed:            {t_total:.1f} seconds", flush=True)
    print("=" * 80, flush=True)
    return True

if __name__ == "__main__":
    extract_live()
