#!/usr/bin/env python3
"""
Loader for CHARTHST into skyline_live_production.sqlite and Claude's sqlite.
Extracts 13-month historical account balance buckets for every company.
"""

import os
import sys
import sqlite3
import time

sys.path.append("/Users/louislapat/vibe/skyline")
from extract_skyline import mbf_to_double
from btrieve_reader import BtrieveFile

LIVE_ROOT = "/Volumes/skyline$/Skyline"
IFS_DIR = os.path.join(LIVE_ROOT, "IFS")
if not os.path.exists(IFS_DIR):
    IFS_DIR = os.path.abspath("live_skyline_fast_mirror/IFS")
DB_LOCAL = os.path.abspath("skyline_live_production.sqlite")
DB_CLAUDE = "/Users/louislapat/vibe/skyline/skyline_all_companies_gemini.sqlite"

def load_charthst():
    print(f"Scanning {IFS_DIR} for CHARTHST files...", flush=True)
    all_folders = [f for f in os.listdir(IFS_DIR) if os.path.isdir(os.path.join(IFS_DIR, f)) and not f.startswith(".")]

    charthst_records = []
    t0 = time.time()

    for idx, f in enumerate(all_folders, 1):
        cp = os.path.join(IFS_DIR, f, "CHARTHST")
        if os.path.exists(cp) and os.path.getsize(cp) > 512:
            try:
                bf = BtrieveFile(cp, 8)
                for r in bf.records():
                    if len(r) >= 104:
                        acct = r[:8].decode("latin1", errors="replace").strip()
                        if not acct or acct[0] == "\x00":
                            continue
                        m_bals = []
                        for m in range(12):
                            chunk = r[8 + m*8 : 8 + (m+1)*8]
                            val = mbf_to_double(chunk) if len(chunk) == 8 else 0.0
                            m_bals.append(round(val, 2))
                        
                        charthst_records.append((f, acct, *m_bals))
            except Exception:
                pass

    print(f"Loaded {len(charthst_records):,} CHARTHST account-month records in {time.time() - t0:.2f}s.", flush=True)

    # Insert into local DB and Claude's DB
    for db in [DB_LOCAL, DB_CLAUDE]:
        if os.path.exists(db):
            conn = sqlite3.connect(db)
            conn.executescript("""
                DROP TABLE IF EXISTS chart_history;
                CREATE TABLE chart_history (
                    ifs_id TEXT,
                    account_number TEXT,
                    m01_bal REAL, m02_bal REAL, m03_bal REAL, m04_bal REAL,
                    m05_bal REAL, m06_bal REAL, m07_bal REAL, m08_bal REAL,
                    m09_bal REAL, m10_bal REAL, m11_bal REAL, m12_bal REAL,
                    PRIMARY KEY (ifs_id, account_number)
                );
                CREATE INDEX IF NOT EXISTS idx_charthst_ifs ON chart_history(ifs_id);
            """)
            conn.execute("DELETE FROM chart_history")
            conn.executemany("""
                INSERT OR REPLACE INTO chart_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, charthst_records)
            conn.commit()
            count = conn.execute("SELECT count(*) FROM chart_history").fetchone()[0]
            conn.close()
            print(f"✅ Injected into {os.path.basename(db)}: {count:,} records in chart_history table.", flush=True)

if __name__ == "__main__":
    load_charthst()
