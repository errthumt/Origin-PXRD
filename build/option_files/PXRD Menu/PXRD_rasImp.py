# TEST SUCCEEDED

import originpro as op
import os
import sys
import json

# Import ras_files contained in labtalk fname$ variable
def import_ras_files():
    # Imports using User Files\Filters\rasImp.oif
    # Cleans up names and units
    labtalk_cmd = fr'''
    impFile filtername:="rasImp.oif" location:=user;
    page.longname$ = "RAS Imports";
    wks.name$ = "RAS Imports";

    for(int ic=2; ic<=wks.ncols; ic+=2)
    {{
       rnormalize irng:=$(ic) method:=1 orng:=$(ic);
       wks.col$(ic).lname$ = "Int";
       wks.col$(ic).unit$ = "AU";
       wks.col$(ic-1).lname$ = "2θ";
       wks.col$(ic-1).unit$ = "deg";
       
       wcolwidth $(ic) -1;
       wcolwidth $(ic-1) -1;
    }}
    
    // Hide Formula Row
    wks.labels(-O);
    '''

    # Create new book, target worksheet
    wb = op.new_book('w',lname="RAS Imports")
    wks = wb[0]

    # Import
    op.lt_exec(labtalk_cmd)

    # Get the list of imported file paths from fname$
    file_paths = op.get_lt_str('fname$').split("\r\n")
    file_paths = [p for p in file_paths if p.strip()]  # clean empties

    # Init wavelength row if it doesn't exist
    wks._user_param_row("Wavelength (Å)", True)

    # Iterate through files in same order as fname$
    for i, path in enumerate(file_paths):
        wl_value = None

        # Read Rigaku data header and extract wavelength
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "HW_XG_WAVE_LENGTH_ALPHA1" in line:
                        # Wavelength is on line: *HW_XG_WAVE_LENGTH_ALPHA1 "1.2345"
                        # Extract the number inside quotes
                        parts = line.split('"')
                        if len(parts) >= 2:
                            wl_value = float(parts[1])
                        break
        # Skip not-found wavelengths, but warn user in script window.
        except Exception as e:
            print(f"WARNING: Failed to read wavelength from {path}: {e}")

        # Write wavelength into the correct 2θ column
        if wl_value is not None:
            # 2θ columns are every odd column in order of fname$
            two_theta_col = 2*i  # 0-based column index for 2θ
            wks.set_label(two_theta_col,wl_value,"Wavelength (Å)")
    
    # Hide unwanted parameter rows
    for uParam in ("Group Info","Method"):
        idx = wks._user_param_row(uParam,True) + 1
        op.lt_exec(f"wks.labels(#D{idx});")

    # Clean SourceFile label row to contain only filenames (instead of full path)
    try:
        sourcefiles = wks.get_labels('SourceFile')
        cleaned = [os.path.basename(s) if s else "" for s in sourcefiles]
        for i, val in enumerate(cleaned):
            wks.set_label(i, val, 'SourceFile')
    except:
        pass

    op.lt_exec('type -b "RAS import complete.";')



# Select folder containing all desired files. Uses Origin's native dlfPath dialog.
def import_ras_from_folder():
    # dlgPath stores folder path under path$. findFiles finds all matching files in path$ and stores in fname$
    folder_path = op.lt_exec('dlgPath init:=%X title:="Select folder containing RAS files"; findFiles ext:=*.ras;')
    if not folder_path:
        op.lt_exec('type -b "No folder selected.";')
        return

    file_paths = op.get_lt_str('fname$')

    if not file_paths:
        op.lt_exec('type -b "No RAS files found in folder.";')
        return

    import_ras_files()


# Select individual files. Uses Origin's native dlfFile dialo
def import_ras_from_file_dialog():
    file_select = op.lt_exec('dlgFile init:=%X multi:=1 title:="Select RAS files for import" group:=*.ras')
    # dlgFile automatically stores filenames under global variable fname$
    file_paths = op.get_lt_str('fname$')
    if not file_select or not file_paths:
        op.lt_exec('type -b "No files selected"')
        return
    import_ras_files()

def parse_params(s):
    items = s.split(',')
    out = {}
    for item in items:
        key, val = item.split(':')
        out[key.strip()] = val.strip()
    return out


# Dispatch based on labtalk arguments.
if __name__ == "__main__":
    paramString = sys.argv[1].lower() if len(sys.argv) > 1 else ""

    params = parse_params(paramString)

    try:
        mode=params["file_mode"]
    except:
        mode="files"

    if mode == "folder":
        import_ras_from_folder()
    elif mode == "files":
        import_ras_from_file_dialog()
    else:
        op.lt_exec(f'type -b "Unknown mode: {mode}";')
