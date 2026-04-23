'''
MAKE SURE YOU ARE EDITING THIS FILE EMBEDDED IN THE ORIGIN PROJECT
EDITS IN THE REPO WILL NOT UPDATE
'''
import originpro as op
import os
import shutil
import sys

# ------------------------------------------------------------
# 1. Installation options (declared once)
# ------------------------------------------------------------
installOps = {
    "PXRD Menu": False,
    "Graph Templates": False,
    "In-Situ Beamline Processing": False,
    "Annealing Profiles": False
}

# ------------------------------------------------------------
# CLI parsing helpers
# ------------------------------------------------------------
def parse_params(s):
    items = s.split(',')
    out = {}
    for item in items:
        try:
            key, val = item.split(':')
            out[key.strip()] = val.strip()
        except:
            print(f"Error parsing option '{item}'. Excluding from parsed parameters")
    return out

def clean_parameters(params):
    new_params = {}
    default_parameters = installOps
    for key in default_parameters:
        def_val = default_parameters[key]
        def_type = type(def_val)

        new_val = params.get(key)
        if not new_val:
            print(f"WARNING: Option folder missing from x-function: '{key}'")
            new_params[key] = def_val
        elif def_type == bool:
            new_params[key] = new_val.lower() == 'true'
        elif def_type != type(new_val):
            try:
                new_params[key] = def_type(new_val)
            except:
                print(f"Incompatible type passed for '{key}'. Defaulting to '{def_val}'")
                new_params[key] = def_val
        else:
            new_params[key] = params[key]

    return new_params

# ------------------------------------------------------------
# Prompt helper (same pattern as repo updater)
# ------------------------------------------------------------
def ask_user(prompt):
    op.lt_exec(f't=4; type -y "{prompt}"')
    return op.lt_int('t')  # 1=yes, 0=no, 4=cancel

def select_options(options_dict):
    selected = {}
    for opt in options_dict:
        t = ask_user(f"Install {opt}? (Click cancel to skip ALL installs)")
        if t == 4:
            print("User cancelled. Skipping all installs.")
            return {k: 0 for k in options_dict}
        selected[opt] = t
    return selected

# ------------------------------------------------------------
# 2. Determine selected options (CLI or interactive)
# ------------------------------------------------------------
if len(sys.argv) > 1:
    print("Parsing command-line parameters...")
    raw_params = parse_params(sys.argv[1])
    selected_options = clean_parameters(raw_params)
else:
    selected_options = select_options(installOps)

# ------------------------------------------------------------
# 3. Resolve project folder (%X) and Option Root
# ------------------------------------------------------------
op.lt_exec('string __proj$ = %X;')
projFolder = op.get_lt_str('__proj$').rstrip("\\/")

optRoot = os.path.join(projFolder, "option_files")

print("Project Folder:", projFolder)
print("Option Root:", optRoot)

# ------------------------------------------------------------
# 4. Validate folders based on selected_options
# ------------------------------------------------------------
actual_folders = {
    name for name in os.listdir(optRoot)
    if os.path.isdir(os.path.join(optRoot, name))
}

# Warn if any selected option folder is missing
for opt in selected_options:
    if opt not in actual_folders:
        print(f"WARNING: Expected option folder missing → {opt}")

# Warn if any extra folders exist
for folder in actual_folders:
    if folder not in selected_options:
        print(f"WARNING: Unrecognized folder in option_files → {folder}")

# ------------------------------------------------------------
# 5. Build dictionary of file paths for each install option
# ------------------------------------------------------------
filepaths = {}

for option in selected_options.keys():
    optionFolder = os.path.join(optRoot, option)

    if not os.path.isdir(optionFolder):
        print(f"Warning: Folder not found for option '{option}': {optionFolder}")
        filepaths[option] = []
        continue

    files = []
    for root, dirs, filenames in os.walk(optionFolder):
        for fname in filenames:
            full = os.path.join(root, fname)
            files.append(full)

    filepaths[option] = files

# ------------------------------------------------------------
# 6. Retrieve User Files Folder (%Y)
# ------------------------------------------------------------
op.lt_exec('string __uff$ = %Y;')
UFF = op.get_lt_str('__uff$')
print("User Files Folder:", UFF)

# ------------------------------------------------------------
# 7. Copy selected files into User Files Folder
# ------------------------------------------------------------
for option, selected in selected_options.items():
    if not selected:
        print(f"--- Skipped {option} installation.")
        continue

    print(f"Installing: {option}")

    optionFolder = os.path.join(optRoot, option)

    for src in filepaths[option]:
        rel_path = os.path.relpath(src, optionFolder)
        dst = os.path.join(UFF, rel_path)

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

        print(f"  Copied: {rel_path}")

    print(f"--- {option} successfully installed!")

# ------------------------------------------------------------
# 8. Always copy PXRD_versionTag.txt
# ------------------------------------------------------------
version_tag_src = os.path.join(projFolder, "PXRD_versionTag.txt")
version_tag_dst = os.path.join(UFF, "PXRD_versionTag.txt")

if os.path.isfile(version_tag_src):
    try:
        shutil.copy2(version_tag_src, version_tag_dst)
        print(f"Copied version tag: {version_tag_src} -> {version_tag_dst}")
    except Exception as e:
        print(f"ERROR copying version tag: {e}")
else:
    print(f"WARNING: PXRD_versionTag.txt not found at {version_tag_src}")
