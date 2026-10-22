#!/usr/bin/env python3
"""
Full Enterprise Skyline Portfolio Sync.

Discovers and syncs all 347+ company general ledgers from the live 
network share (/Volumes/skyline$/Skyline/IFS/) to local storage (live_skyline_local/IFS/).

Transfers only the essential GL tables:
- NAMEGL    (Company master details)
- CHART     (Chart of accounts & categories)
- CHARTHST  (Chart history)
- JOURHIST  (Historical ledger transactions)
- JOURTRAN  (Current period transactions)
"""

import os
import shutil
import sys
import time

SOURCE_IFS = "/Volumes/skyline$/Skyline/IFS"
DEST_IFS = os.path.abspath("live_skyline_local/IFS")
ESSENTIAL_FILES = ["NAMEGL", "CHART", "CHARTHST", "JOURHIST", "JOURTRAN"]

def sync_all():
    if not os.path.exists(SOURCE_IFS):
        print(f"Error: Source path {SOURCE_IFS} not accessible! Check mapped drive.", file=sys.stderr)
        return False

    os.makedirs(DEST_IFS, exist_ok=True)
    all_folders = [f for f in os.listdir(SOURCE_IFS) if os.path.isdir(os.path.join(SOURCE_IFS, f)) and not f.startswith(".")]
    
    print(f"Found {len(all_folders)} company folders on live share.")
    print("Beginning local synchronization of essential GL data...")

    synced_count = 0
    total_bytes = 0
    t0 = time.time()

    for idx, folder in enumerate(all_folders, 1):
        src_dir = os.path.join(SOURCE_IFS, folder)
        dst_dir = os.path.join(DEST_IFS, folder)

        # Check if folder has at least JOURHIST
        jh_src = os.path.join(src_dir, "JOURHIST")
        if not os.path.exists(jh_src) or os.path.getsize(jh_src) < 512:
            continue

        os.makedirs(dst_dir, exist_ok=True)
        copied_any = False

        for fname in ESSENTIAL_FILES:
            s_file = os.path.join(src_dir, fname)
            d_file = os.path.join(dst_dir, fname)
            if os.path.exists(s_file):
                sz = os.path.getsize(s_file)
                # Only copy if missing or size differs
                if not os.path.exists(d_file) or os.path.getsize(d_file) != sz:
                    shutil.copy2(s_file, d_file)
                total_bytes += sz
                copied_any = True

        if copied_any:
            synced_count += 1
            elapsed = time.time() - t0
            print(f"  [{synced_count}] Synced IFS/{folder:<8} ({total_bytes / (1024*1024):.1f} MB, {elapsed:.1f}s)", flush=True)

    t_total = time.time() - t0
    print("\n" + "=" * 75, flush=True)
    print(f"SYNC COMPLETE: Successfully synced {synced_count} active companies!", flush=True)
    print(f"Total Data Transferred: {total_bytes / (1024*1024):.1f} MB in {t_total:.1f} seconds.", flush=True)
    print("=" * 75, flush=True)
    return True

if __name__ == "__main__":
    sync_all()
