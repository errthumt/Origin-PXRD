import urllib.request

import originpro as op
import os

def get_installed_version():
    """
    Determines the Origin User Files Folder (UFF) and reads:
        <UFF>/PXRD_versionTag.txt

    Returns:
        version string (e.g. "1.4.7") or None if missing/unreadable.
    """

    # Determine UFF using LabTalk
    op.lt_exec('string __uff$ = %Y;')
    uff_path = op.get_lt_str('__uff$')

    version_file = os.path.join(uff_path, "PXRD_versionTag.txt")

    if not os.path.exists(version_file):
        return None

    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_latest_version():
    url = "https://raw.githubusercontent.com/errthumt/Origin-PXRD/1.3-dev/build/option_files/PXRD%20Menu/PXRD_versionTag.txt"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode("utf-8").strip()
    except Exception as e:
        print(e)
        return None

def notify_if_outdated(local_version):
    latest = get_latest_version()
    if latest is None:
        print("Could not check for updates.")
        return

    if latest != local_version:
        print(f"A new version is available: {latest} (you have {local_version})")
    else:
        print(f"You are up to date (version {local_version}).")

# Example usage:
LOCAL_VERSION = get_installed_version()
notify_if_outdated(LOCAL_VERSION)
