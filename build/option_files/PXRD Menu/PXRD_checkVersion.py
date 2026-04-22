import urllib.request

def get_latest_version():
    url = "https://raw.githubusercontent.com/errthumt/Origin-PXRD/main/build/option_files/PXRD%20Menu/PXRD_versionTag.txt"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode("utf-8").strip()
    except Exception:
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
LOCAL_VERSION = "1.3.0"
notify_if_outdated(LOCAL_VERSION)
