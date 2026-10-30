#!/usr/bin/env python3
"""
High-Speed Multi-Threaded Sync for Live Skyline SMB Share.

Techniques applied:
1. Concurrency: 16 parallel SMB worker threads to eliminate the 70ms network latency penalty.
2. Targeted Filtering: Transfers only essential GL tables (NAMEGL, CHART, CHARTHST, JOURHIST, JOURTRAN).
3. Incremental Delta Sync: Skips unmodified files by checking mtime and size.
4. Large Chunk Buffered I/O: 1MB read/write buffers.
"""

import os
import shutil
import time
import concurrent.futures
from typing import List, Tuple, Set

SOURCE_IFS = "/Volumes/skyline$/Skyline/IFS"
SOURCE_DATA = "/Volumes/skyline$/Skyline/DATA"
DEST_LOCAL = os.path.abspath("live_skyline_fast_mirror")
ESSENTIAL_TABLES = {"NAMEGL", "CHART", "CHARTHST", "JOURHIST", "JOURTRAN"}

def copy_file_task(task: Tuple[str, str]) -> Tuple[str, int]:
    src, dst = task
    try:
        # Check if already up to date
        if os.path.exists(dst):
            s_stat = os.stat(src)
            d_stat = os.stat(dst)
            if s_stat.st_size == d_stat.st_size and abs(s_stat.st_mtime - d_stat.st_mtime) < 2:
                return (dst, 0) # Already fresh
        
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        # Use large buffer copy for SMB
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst, length=1024 * 1024)
        shutil.copystat(src, dst)
        return (dst, os.path.getsize(dst))
    except Exception as e:
        return (dst, 0)

def run_fast_sync(max_workers: int = 16) -> Set[str]:
    print("=" * 75)
    print(f"HIGH-SPEED PARALLEL SYNC: LIVE SKYLINE SHARE -> MAC LOCAL")
    print(f"Workers: {max_workers} parallel threads | Buffer: 1MB chunk streaming")
    print("=" * 75)

    if not os.path.exists(SOURCE_IFS):
        print(f"Error: {SOURCE_IFS} not mounted!", file=sys.stderr)
        return set()

    t0 = time.time()
    tasks: List[Tuple[str, str]] = []

    # 1. Add DATA catalog files
    os.makedirs(os.path.join(DEST_LOCAL, "DATA"), exist_ok=True)
    for ddf in ["FILE.DDF", "FIELD.DDF", "INDEX.DDF"]:
        s = os.path.join(SOURCE_DATA, ddf)
        d = os.path.join(DEST_LOCAL, "DATA", ddf)
        if os.path.exists(s):
            tasks.append((s, d))

    # 2. Add all company essential files in parallel
    print(f"Scanning company directories on mapped drive in parallel...", flush=True)
    company_folders = [f for f in os.listdir(SOURCE_IFS) if os.path.isdir(os.path.join(SOURCE_IFS, f)) and not f.startswith(".")]

    def scan_company(comp: str) -> List[Tuple[str, str]]:
        sub_tasks = []
        src_comp = os.path.join(SOURCE_IFS, comp)
        dst_comp = os.path.join(DEST_LOCAL, "IFS", comp)
        try:
            available = set(os.listdir(src_comp))
            for tbl in ESSENTIAL_TABLES:
                if tbl in available:
                    sub_tasks.append((os.path.join(src_comp, tbl), os.path.join(dst_comp, tbl)))
        except Exception:
            pass
        return sub_tasks

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as scan_executor:
        scan_results = scan_executor.map(scan_company, company_folders)
        for r in scan_results:
            tasks.extend(r)

    print(f"Total essential files identified across all companies: {len(tasks):,} files.")
    print(f"Starting multi-threaded transfer across {max_workers} threads...", flush=True)

    copied_bytes = 0
    copied_files = 0
    updated_cids: Set[str] = set()
    t_start_copy = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(copy_file_task, task): task for task in tasks}
        for f in concurrent.futures.as_completed(futures):
            dst, sz = f.result()
            if sz > 0:
                copied_bytes += sz
                copied_files += 1
                parts = dst.split(os.sep)
                if "IFS" in parts:
                    idx = parts.index("IFS")
                    if idx + 1 < len(parts):
                        updated_cids.add(parts[idx + 1])
            
            done = copied_files
            if done > 0 and (done % 100 == 0 or done == len(tasks)):
                elapsed = time.time() - t_start_copy
                mb = copied_bytes / (1024 * 1024)
                speed = mb / elapsed if elapsed > 0 else 0
                print(f"  Transferred {done:,} files | {mb:.1f} MB ({speed:.2f} MB/s) | {elapsed:.1f}s elapsed...", flush=True)

    t_total = time.time() - t0
    total_mb = copied_bytes / (1024 * 1024)
    avg_speed = total_mb / (time.time() - t_start_copy) if (time.time() - t_start_copy) > 0 else 0

    print("\n" + "=" * 75)
    print("FAST SYNC COMPLETE!")
    print(f"  Total Files Copied: {copied_files:,} / {len(tasks):,}")
    print(f"  Companies Modified: {len(updated_cids):,}")
    print(f"  Total Data Copied:  {total_mb:.1f} MB")
    print(f"  Average Throughput: {avg_speed:.2f} MB/s")
    print(f"  Total Time:         {t_total:.2f} seconds")
    print("=" * 75)
    return updated_cids

if __name__ == "__main__":
    run_fast_sync(16)
