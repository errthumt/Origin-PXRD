import subprocess
from pathlib import Path
import shutil
import zipfile
import re

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

def get_base_version(version: str) -> str:
    return version.split("-")[0]

def to_nsis_version(version: str) -> str:
    """
    Convert a git describe version into a valid NSIS X.X.X.X version.
    Examples:
        "1.2.1"            -> "1.2.1.0"
        "1.2.1-3-g0c354ba" -> "1.2.1.3"
        "0.0.0-a1b2c3"     -> "0.0.0.0"
    """
    base = get_base_version(version)          # "1.2.1"
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
    Update the 'recent installer' and 'recent zip' links in selected Markdown files.

    Replaces the blocks:
      <!--start recent installer link--> ... <!--end recent installer link-->
      <!--start recent zip link--> ... <!--end recent zip link-->
    """

    # Files to update (paths only; nest level computed automatically)
    files = [
        REPO_ROOT / "install_guide" / "index.md",
        REPO_ROOT / "release_notes.md"
    ]

    # ------------------------------------------------------------
    # Helper: compute nest level relative to repo root
    # ------------------------------------------------------------
    def compute_nest_level(md_file: Path, repo_root: Path) -> int:
        """
        Compute how many directory levels `md_file` is below `repo_root`.

        Example:
            repo_root = /home/user/project
            md_file   = /home/user/project/docs/sub/page.md
            → nest_level = 2
        """
        rel = md_file.relative_to(repo_root)
        # rel.parents includes the file itself as the first parent, so subtract 1
        return len(rel.parents) - 1

    # ------------------------------------------------------------
    # URL + line builders (nest-level aware)
    # ------------------------------------------------------------
    def installer_url(nest_level=0):
        return f"{'../'*nest_level if nest_level > 0 else './'}installer/release/OriginPXRD_Installer_v{version}.exe"
    
    def zip_url(nest_level=0):
        return f"{'../'*nest_level if nest_level > 0 else './'}manual_install/OriginPXRD_v{version}.zip"

    def recent_installer_line(nest_level=0):
        return f"[Click Here to Download the most recent installer]({installer_url(nest_level)})"
    
    def recent_zip_line(nest_level=0):
        return f"[Click Here to Download the most recent zip package]({zip_url(nest_level)})"

    def release_notes_lines(nest_level=0):
        inst = installer_url(nest_level)
        zipf = zip_url(nest_level)
        return (
            f"## Release {get_base_version(version)}\n\n"
            f"Installer: [OriginPXRD_Installer_v{version}.exe]({inst})\n"
            f"Zip Package: [OriginPXRD_v{version}.zip]({zipf})\n"
            f"<!--end release link-->"
        )


    # ------------------------------------------------------------
    # Regex patterns (unchanged)
    # ------------------------------------------------------------
    recent_installer_pattern = re.compile(
        r"<!--start recent installer link-->.*?<!--end recent installer link-->",
        flags=re.DOTALL,
    )
    recent_zip_pattern = re.compile(
        r"<!--start recent zip link-->.*?<!--end recent zip link-->",
        flags=re.DOTALL,
    )

    release_notes_new_pattern = re.compile(
        fr"## Release {re.escape(get_base_version(version))}"
    )

    release_notes_existing_pattern = re.compile(
        fr"## Release {re.escape(get_base_version(version))}\n<!--start release link-->.*?<!--end release link-->",
        flags=re.DOTALL,
    )

    # ------------------------------------------------------------
    # Apply replacements to each file
    # ------------------------------------------------------------
    for md_file in files:
        if not md_file.exists():
            print(f"Skipping missing file: {md_file}")
            continue

        # Compute nest level automatically
        nest_level = compute_nest_level(md_file, REPO_ROOT)

        # Build replacement blocks using the computed nest level
        installer_block = (
            f"<!--start recent installer link-->\n"
            f"{recent_installer_line(nest_level)}\n"
            f"<!--end recent installer link-->"
        )

        zip_block = (
            f"<!--start recent zip link-->\n"
            f"{recent_zip_line(nest_level)}\n"
            f"<!--end recent zip link-->"
        )

        # Read using UTF‑8 to avoid CP1252 decode errors
        text = md_file.read_text(encoding="utf-8")

        # Replace installer block if present
        text = recent_installer_pattern.sub(installer_block, text)

        # Replace zip block if present
        text = recent_zip_pattern.sub(zip_block, text)

        # ------------------------------------------------------------
        # Release notes replacement logic (no insertion)
        # ------------------------------------------------------------

        # Build the release notes block using the computed nest level
        release_block = release_notes_lines(nest_level)

        # 1. Try replacing an existing full release block
        if release_notes_existing_pattern.search(text):
            text = release_notes_existing_pattern.sub(release_block, text)

        # 2. Otherwise, try replacing a header-only match
        elif release_notes_new_pattern.search(text):
            text = release_notes_new_pattern.sub(release_block, text)

        # 3. Otherwise: do nothing (no release notes section in this file)


        # Write back using UTF‑8
        md_file.write_text(text, encoding="utf-8")
        print(f"Updated links in: {md_file} (nest level {nest_level})")

def git_cache_installer(file_path: Path):
    """
    Force-add a file to Git once, commit it, and mark it assume-unchanged
    so future local changes or deletions do not affect origin.
    """
    rel = file_path.relative_to(REPO_ROOT)

    # Force-add the file even if ignored
    subprocess.run(["git", "add", "-f", str(rel)], cwd=REPO_ROOT)

    # Commit it (optional but recommended)
    subprocess.run(
        ["git", "commit", "-m", f"Cache installer at {rel}"], 
        cwd=REPO_ROOT
    )

    # Mark assume-unchanged so local edits/deletes don't propagate
    subprocess.run(
        ["git", "update-index", "--assume-unchanged", str(rel)],
        cwd=REPO_ROOT
    )

    print(f"Cached installer: {rel}")

def git_uncache_installer(file_path: Path):
    """
    Remove a one-time cached installer from origin without deleting
    the local file. This reverses git_cache_installer().
    """
    rel = file_path.relative_to(REPO_ROOT)

    # Stop ignoring local changes
    subprocess.run(
        ["git", "update-index", "--no-assume-unchanged", str(rel)],
        cwd=REPO_ROOT
    )

    # Stage the deletion (but do NOT delete locally)
    subprocess.run(
        ["git", "rm", "--cached", str(rel)],
        cwd=REPO_ROOT
    )

    # Commit the removal
    subprocess.run(
        ["git", "commit", "-m", f"Remove or relocate cached installer {rel}"],
        cwd=REPO_ROOT
    )

    print(f"Removed cached unstable installer from origin: {rel}")



def relocate_old_versions(version: str):
    """
    Move older installer/zip files with the same base version into
    release/unstable or manual_install/unstable so only the newest
    hotfix remains in the published folders.
    """
    base = get_base_version(version)

    # Directories
    installer_dir = REPO_ROOT / "installer" / "release"
    manual_dir = REPO_ROOT / "manual_install"

    unstable_installer = installer_dir / "unstable"
    unstable_manual = manual_dir / "unstable"

    unstable_installer.mkdir(exist_ok=True)
    unstable_manual.mkdir(exist_ok=True)

    # Patterns to match
    installer_pattern = re.compile(rf"OriginPXRD_Installer_v{base}(-\d+-g[0-9a-f]+)?\.exe$")
    zip_pattern = re.compile(rf"OriginPXRD_v{base}(-\d+-g[0-9a-f]+)?\.zip$")

    # --- Process installer files ---
    for file in installer_dir.glob("OriginPXRD_Installer_v*.exe"):
        name = file.name
        if installer_pattern.match(name) and version not in name:
            dest = unstable_installer / name
            print(f"Moving old installer: {file} → {dest}")
            git_uncache_installer(file)
            file.replace(dest)
            git_cache_installer(dest)


    # --- Process zip files ---
    for file in manual_dir.glob("OriginPXRD_v*.zip"):
        name = file.name
        if zip_pattern.match(name) and version not in name:
            dest = unstable_manual / name
            print(f"Moving old zip: {file} → {dest}")
            file.replace(dest)
            git_cache_installer(dest)

def update_all_release_links():
    """
    One-time utility:
      1. Scans REPO_ROOT/release_notes.md for all '## Release {base_version}' headers.
      2. For each base version, finds the newest matching hotfix installer in
         REPO_ROOT/installer/release/.
      3. Calls update_recent_links(version) for each discovered hotfix version.
    """

    release_notes_path = REPO_ROOT / "release_notes.md"
    installer_dir = REPO_ROOT / "installer" / "release"

    # --- Step 1: Extract base versions from release_notes.md ---
    base_versions = []
    release_header_pattern = re.compile(r"^## Release (\d+\.\d+\.\d+)", re.MULTILINE)

    text = release_notes_path.read_text(encoding="utf-8")
    for match in release_header_pattern.finditer(text):
        base_versions.append(match.group(1))

    print("Found base versions:", base_versions)

    # --- Step 2: For each base version, find the newest hotfix version ---
    hotfix_versions = []

    for base in base_versions:
        # Matches:
        #   OriginPXRD_Installer_v1.4.2.exe
        #   OriginPXRD_Installer_v1.4.2-16-gabc123.exe
        pattern = re.compile(
            rf"OriginPXRD_Installer_v({re.escape(base)}(?:-\d+-g[0-9a-f]+)?)\.exe$"
        )

        newest = None

        for file in installer_dir.glob("OriginPXRD_Installer_v*.exe"):
            m = pattern.match(file.name)
            if m:
                version = m.group(1)
                # git-describe versions sort lexicographically
                if newest is None or version > newest:
                    newest = version

        if newest:
            hotfix_versions.append(newest)
            print(f"Base {base} → newest hotfix version: {newest}")
        else:
            print(f"WARNING: No installer found for base version {base}")

    # --- Step 3: Update recent links for each hotfix version ---
    for version in hotfix_versions:
        print(f"\nUpdating recent links for version: {version}")
        update_recent_links(version)


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

installer_path = REPO_ROOT / "installer" / "release" / f"OriginPXRD_Installer_v{version}.exe"
git_cache_installer(installer_path)

relocate_old_versions(version)

update_recent_links(version)

# OCCASIONAL UTILITY:
# update_all_release_links()  # Uncomment to scan release_notes.md and update all links to the newest hotfix versions
