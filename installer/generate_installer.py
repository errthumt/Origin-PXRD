import subprocess
from pathlib import Path
import shutil
import zipfile

# Directories
INSTALLER_ROOT = Path(__file__).parent
REPO_ROOT = INSTALLER_ROOT.parent

# NSIS paths
nsi_template = INSTALLER_ROOT / "OriginPXRDInstaller.nsi"
nsi_output = INSTALLER_ROOT / "OriginPXRDInstaller_generated.nsi"

def create_manual_install_zip(version: str):
    """
    Create manual_install/OriginPXRD_<version>.zip containing the contents of
    build/option_files/, preserving relative paths.
    """
    option_root = REPO_ROOT / "build" / "option_files"
    output_dir = REPO_ROOT / "manual_install"
    output_dir.mkdir(exist_ok=True)

    zip_path = output_dir / f"OriginPXRD_v{version}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in option_root.rglob("*"):
            if file.is_file():
                z.write(file, file.relative_to(option_root))

    print(f"Manual install ZIP created: {zip_path}")

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

def update_recent_links(version: str):
    """
    Update the 'recent installer' and 'recent zip' links in:
      - root/README.md
      - root/installer/release/readme.md
      - root/manual_install/readme.md

    Replaces the blocks:
      <!--start recent installer link--> ... <!--end recent installer link-->
      <!--start recent zip link--> ... <!--end recent zip link-->
    """

    # Files to update
    files = [
        REPO_ROOT / "README.md",
        INSTALLER_ROOT / "release" / "readme.md",
        REPO_ROOT / "manual_install" / "readme.md",
    ]

    # New URLs
    new_installer_url = (
        f"https://github.com/errthumt/Origin-PXRD/raw/refs/heads/main/"
        f"installer/release/OriginPXRD_Installer_v{version}.exe"
    )
    new_zip_url = (
        f"https://github.com/errthumt/Origin-PXRD/raw/refs/heads/main/"
        f"manual_install/OriginPXRD_v{version}.zip"
    )

    # Markdown lines
    installer_line = (
        f"[Click Here to Download the most recent installer]({new_installer_url})"
    )
    zip_line = (
        f"[Click Here to Download the most recent zip package]({new_zip_url})"
    )

    import re

    # Regex patterns
    installer_pattern = re.compile(
        r"<!--start recent installer link-->.*?<!--end recent installer link-->",
        flags=re.DOTALL,
    )
    zip_pattern = re.compile(
        r"<!--start recent zip link-->.*?<!--end recent zip link-->",
        flags=re.DOTALL,
    )

    # Replacement blocks
    installer_block = (
        f"<!--start recent installer link-->\n{installer_line}\n<!--end recent installer link-->"
    )
    zip_block = (
        f"<!--start recent zip link-->\n{zip_line}\n<!--end recent zip link-->"
    )

    # Apply replacements to each file
    for md_file in files:
        if not md_file.exists():
            print(f"Skipping missing file: {md_file}")
            continue

        # Read using UTF‑8 to avoid CP1252 decode errors
        text = md_file.read_text(encoding="utf-8")

        # Replace installer block if present
        text = installer_pattern.sub(installer_block, text)

        # Replace zip block if present
        text = zip_pattern.sub(zip_block, text)

        # Write back using UTF‑8
        md_file.write_text(text, encoding="utf-8")
        print(f"Updated links in: {md_file}")




# 1. Get version from Git
version = get_git_version()
print(f"Using version: {version}")
nsis_version = to_nsis_version(version)

# --- Write version tag file before packaging ---
version_tag_path = REPO_ROOT / "build" / "PXRD_versionTag.txt"
version_tag_path.parent.mkdir(exist_ok=True)  # ensure build/ exists
version_tag_path.write_text(version + "\n\nDO NOT EDIT THIS FILE, it is used to check for further updates.")
print(f"Wrote version tag to: {version_tag_path}")

template = nsi_template.read_text()
template = template.replace("${VERSION}", version)
template = template.replace("${NSIS_VERSION}", nsis_version)
nsi_output.write_text(template)
create_manual_install_zip(version)

# 3. Run NSIS compiler
subprocess.check_call([str(MAKENSIS), str(nsi_output)])

print(f"Installer generated: OriginPXRD_Installer_v{version}.exe")

update_recent_links(version)
