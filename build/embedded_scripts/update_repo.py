'''
MAKE SURE YOU ARE EDITING THIS FILE EMBEDDED IN THE ORIGIN PROJECT
EDITS IN THE REPO WILL NOT UPDATE
'''
import os
import shutil
import originpro as op
import sys

# ------------------------------------------------------------
# 1. Resolve project root using your installer logic
# ------------------------------------------------------------
op.lt_exec('string __proj$ = %X;')
projFolder = op.get_lt_str('__proj$').rstrip("\\/")

optRoot = os.path.join(projFolder, "option_files")

# ------------------------------------------------------------
# 2. Resolve User Files Folder
# ------------------------------------------------------------
op.lt_exec('string __uff$ = %Y;')
userFiles = op.get_lt_str('__uff$').rstrip("\\/")

print(f"Project Root: {projFolder}")
print(f"Option Files Root: {optRoot}")
print(f"User Files Folder: {userFiles}")

# ------------------------------------------------------------
# 3. Canonical options dict (friendly name → selected flag)
# ------------------------------------------------------------
options = {
    "PXRD Menu": False,
    "In-Situ Beamline Processing": False,
    "Annealing Profiles": False,
    "Graph Templates": False
}


# ------------------------------------------------------------
# ask_user now returns t directly
# ------------------------------------------------------------
def ask_user(prompt):
    """
    Uses Origin's built-in yes/no/cancel dialog.
    Returns:
        1 = Yes
        0 = No
        4 = Cancel
    """
    op.lt_exec(f't=4; type -y "{prompt}"')
    return op.lt_int('t')

# ------------------------------------------------------------
# Helper: prompt user for all options and return a dict
# ------------------------------------------------------------
def select_options(options_dict):
    """
    Loop through options and ask user which to update.
    Returns a dict mapping option_name -> True/False.
    If user cancels at any point, returns the original options_dict unchanged.
    """
    selected = {}

    for opt in options_dict:


        t = ask_user(f"Update '{opt}' from User Files?")

        if t == 4:  # Cancel
            print("User cancelled. Aborting selection.")
            return options_dict  # unchanged

        selected[opt] = (t == 1)

    return selected
    
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
    default_parameters = options
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
# 5. Get selected options (CLI or interactive)
# ------------------------------------------------------------
if len(sys.argv) > 1:
    print("Parsing command-line parameters...")
    raw_params = parse_params(sys.argv[1])
    selected_options = clean_parameters(raw_params)
else:
    selected_options = select_options(options)

    
# ------------------------------------------------------------
# Validate folders based on selected_options
# ------------------------------------------------------------
actual_folders = {
    name for name in os.listdir(optRoot)
    if os.path.isdir(os.path.join(optRoot, name))
}

# Warn if any selected option folder is missing
for opt in selected_options:
    if opt not in actual_folders:
        print(f"WARNING: Expected option folder missing → {opt}")

# Warn if any extra folders exist in optRoot
for folder in actual_folders:
    if folder not in selected_options:
        print(f"WARNING: Unrecognized folder in option_files → {folder}")


# ------------------------------------------------------------
# 6. Process selected options
# ------------------------------------------------------------
for opt, do_update in selected_options.items():
    print("\n----------------------------------------")
    print(f"Option folder: {opt}")
    print("----------------------------------------")
    if not do_update:
        print(f"\nSkipping '{opt}'.")
        continue

    print(f"\nUpdating '{opt}'...")

    optPath = os.path.join(optRoot, opt)

    # Build list of relative filepaths
    rel_paths = []
    for root, dirs, files in os.walk(optPath):
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, optPath)
            rel_paths.append(rel)

    print(f"Found {len(rel_paths)} files to update.")

    # Copy from User Files Folder into option folder
    for rel in rel_paths:
        src = os.path.join(userFiles, rel)
        dst = os.path.join(optPath, rel)

        if not os.path.isfile(src):
            print(f"WARNING: Missing in User Files → {rel}")
            continue

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Updated: {rel}")

print("\nAll selected updates complete.")
