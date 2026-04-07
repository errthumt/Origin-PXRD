import subprocess
from pathlib import Path
import shutil

# Directories
INSTALLER_ROOT = Path(__file__).parent
REPO_ROOT = INSTALLER_ROOT.parent

# NSIS paths
nsi_template = INSTALLER_ROOT / "OriginPXRDInstaller.nsi"
nsi_output = INSTALLER_ROOT / "OriginPXRDInstaller_generated.nsi"


def find_makensis():
    """
    Returns the full path to makensis.exe if found.
    Searches PATH, Program Files, Program Files (x86),
    and an optional portable NSIS folder inside the repo.
    """
    # 1. Check PATH
    makensis = shutil.which("makensis")
    if makensis:
        return Path(makensis)

    # 2. Standard install locations
    possible_paths = [
        Path(r"C:\Program Files (x86)\NSIS\makensis.exe"),
        Path(r"C:\Program Files\NSIS\makensis.exe"),
    ]

    # 3. Optional portable NSIS inside the repo
    portable = REPO_ROOT / "nsis" / "makensis.exe"
    possible_paths.append(portable)

    for path in possible_paths:
        if path.exists():
            return path

    raise FileNotFoundError(
        "makensis.exe not found. Install NSIS or add it to PATH."
    )


MAKENSIS = find_makensis()


def get_git_version():
    """
    Returns a version string based on `git describe`.
    Examples:
        v1.2.1
        v1.2.1-3-g9f8c2d1
    If no tags exist, falls back to commit hash.
    """
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags"],
            cwd=REPO_ROOT,
            text=True
        ).strip()
    except subprocess.CalledProcessError:
        # No tags exist — fall back to commit hash
        version = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True
        ).strip()
        version = f"0.0.0-{version}"

    # Remove leading "v" if present
    return version.lstrip("v")

def to_nsis_version(version: str) -> str:
    """
    Convert a git describe version into a valid NSIS X.X.X.X version.
    Examples:
        "1.2.1"            -> "1.2.1.0"
        "1.2.1-3-g0c354ba" -> "1.2.1.3"
        "0.0.0-a1b2c3"     -> "0.0.0.0"
    """
    base = version.split("-")[0]          # "1.2.1"
    parts = base.split(".")               # ["1","2","1"]

    # Pad to 3 components
    while len(parts) < 3:
        parts.append("0")

    # Fourth component = number of commits since tag (if present)
    if "-" in version:
        try:
            count = version.split("-")[1]  # "3"
            count = int(count)
        except:
            count = 0
    else:
        count = 0

    return f"{parts[0]}.{parts[1]}.{parts[2]}.{count}"

# 1. Get version from Git
version = get_git_version()
print(f"Using version: {version}")
nsis_version = to_nsis_version(version)

template = nsi_template.read_text()
template = template.replace("${VERSION}", version)
template = template.replace("${NSIS_VERSION}", nsis_version)
nsi_output.write_text(template)


# 3. Run NSIS compiler
subprocess.check_call([str(MAKENSIS), str(nsi_output)])

print(f"Installer generated: OriginPXRDInstaller_v{version}.exe")