#!/usr/bin/env python3
"""
Automount Engine for Skyline SMB Network Shares.

Mandate from user:
"You have to mount the s drive first for it to mount skyline."

S Drive:       smb://10.221.20.235/jennings-data$  (Mounted at /Volumes/jennings-data$)
Skyline Share: smb://172.17.21.167/skyline$        (Mounted at /Volumes/skyline$)
Target Path:   /Volumes/skyline$/Skyline
"""

import os
import subprocess
import time
import sys

S_SHARE_URL = "smb://10.221.20.235/jennings-data$"
S_MOUNT_POINT = "/Volumes/jennings-data$"

SKYLINE_SHARE_URL = "smb://172.17.21.167/skyline$"
SKYLINE_MOUNT_POINT = "/Volumes/skyline$"
SKYLINE_TARGET_DIR = "/Volumes/skyline$/Skyline"

def is_mounted(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)

def mount_smb_share(share_url: str, mount_point: str, timeout: int = 10) -> bool:
    """Mounts an SMB share using macOS AppleScript (reuses Keychain credentials)."""
    if is_mounted(mount_point):
        return True
    
    cmd = ["osascript", "-e", f'mount volume "{share_url}"']
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if res.returncode != 0 and "already mounted" not in res.stderr.lower():
            # Fallback to 'open' command
            subprocess.run(["open", share_url], capture_output=True, text=True)
    except Exception as e:
        print(f"Mount trigger note for {share_url}: {e}", file=sys.stderr)

    # Wait for mount point to appear in /Volumes
    start_t = time.time()
    while time.time() - start_t < timeout:
        if is_mounted(mount_point):
            return True
        time.sleep(0.5)

    return is_mounted(mount_point)

def ensure_skyline_mounted(verbose: bool = True) -> bool:
    """
    Ensures Skyline share is mounted by mounting S drive first, then Skyline.
    Returns True if /Volumes/skyline$/Skyline is accessible.
    """
    if is_mounted(SKYLINE_TARGET_DIR):
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}] 🔗 🟢 Live Skyline production share already mounted at {SKYLINE_TARGET_DIR}")
        return True

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] 🔄 Skyline share not mounted. Initiating automated dependency mount sequence...")

    # Step 1: Mount S Drive first
    if not is_mounted(S_MOUNT_POINT):
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}]   [1/2] Mounting primary S: drive ({S_SHARE_URL})...")
        s_ok = mount_smb_share(S_SHARE_URL, S_MOUNT_POINT, timeout=8)
        if s_ok:
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}]   ✅ S: drive mounted at {S_MOUNT_POINT}")
            time.sleep(1.5)  # Allow Kerberos / NTLM session token negotiation
        else:
            if verbose:
                print(f"[{time.strftime('%H:%M:%S')}]   ⚠️ S: drive mount did not complete in time, attempting Skyline mount directly...")

    # Step 2: Mount Skyline Share
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}]   [2/2] Mounting Skyline production share ({SKYLINE_SHARE_URL})...")
    skyline_ok = mount_smb_share(SKYLINE_SHARE_URL, SKYLINE_MOUNT_POINT, timeout=10)

    if skyline_ok and is_mounted(SKYLINE_TARGET_DIR):
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}]   ✅ Skyline production share successfully mounted at {SKYLINE_TARGET_DIR}")
        return True
    else:
        if verbose:
            print(f"[{time.strftime('%H:%M:%S')}]   ⚠️ Unable to mount Skyline share. Verify machine is connected to office network / VPN.")
        return False

if __name__ == "__main__":
    success = ensure_skyline_mounted(verbose=True)
    sys.exit(0 if success else 1)
