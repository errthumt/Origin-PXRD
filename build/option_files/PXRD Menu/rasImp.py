# TEST SUCCEEDED

import originpro as op
import os
import sys

# ------------------------------------------------------------
# 1) Import RAS files from a list of file paths
# ------------------------------------------------------------
def import_ras_files():

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
    wb = op.new_book('w',lname="RAS Imports")
    wks = wb[0]

    op.lt_exec(labtalk_cmd)

    # ------------------------------------------------------------
    # Extract wavelength from each file and write to user parameter
    # ------------------------------------------------------------

    # 1) Get the list of imported file paths from fname$
    file_paths = op.get_lt_str('fname$').split("\r\n")
    file_paths = [p for p in file_paths if p.strip()]  # clean empties

    # 2) Get the user parameter row index
    wl_row = wks._user_param_row("Wavelength (Å)", True)

    # 3) Iterate through files in order
    for i, path in enumerate(file_paths):
        wl_value = None

        # Read header and extract wavelength
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "HW_XG_WAVE_LENGTH_ALPHA1" in line:
                        # Extract the number inside quotes
                        parts = line.split('"')
                        if len(parts) >= 2:
                            wl_value = float(parts[1])
                        break
        except Exception as e:
            print(f"Failed to read wavelength from {path}: {e}")

        # 4) Write wavelength into the correct 2θ column
        if wl_value is not None:
            two_theta_col = 2*i  # 0-based column index for 2θ
            wks.set_label(two_theta_col,wl_value,"Wavelength (Å)")
    
    # Hide Group and Method
    for uParam in ("Group Info","Method"):
        idx = wks._user_param_row(uParam,True) + 1
        op.lt_exec(f"wks.labels(#D{idx});")

    # Clean SourceFile label row to contain only filenames
    try:
        sourcefiles = wks.get_labels('SourceFile')
        cleaned = [os.path.basename(s) if s else "" for s in sourcefiles]
        for i, val in enumerate(cleaned):
            wks.set_label(i, val, 'SourceFile')
    except:
        pass

    op.lt_exec('type -b "RAS import complete.";')


# ------------------------------------------------------------
# 2) Folder selection mode
# ------------------------------------------------------------
def import_ras_from_folder():

    folder_path = op.lt_exec('dlgPath init:=%X title:="Select folder containing RAS files"; findFiles ext:=*.ras;')

    if not folder_path:
        op.lt_exec('type -b "No folder selected.";')
        return

    file_paths = op.get_lt_str('fname$')

    if not file_paths:
        op.lt_exec('type -b "No RAS files found in folder.";')
        return

    import_ras_files()


# ------------------------------------------------------------
# 3) Multi-folder, multi-file selection dialog
# ------------------------------------------------------------
def import_ras_from_file_dialog():
    file_select = op.lt_exec('dlgFile init:=%X multi:=1 title:="Select RAS files for import" group:=*.ras')
    file_paths = op.get_lt_str('fname$')
    if not file_select or not file_paths:
        op.lt_exec('type -b "No files selected"')
        return
    import_ras_files()



# ------------------------------------------------------------
# 4) Dispatch based on sys.argv (LabTalk argument)
# ------------------------------------------------------------
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else ""

    if mode == "folder":
        import_ras_from_folder()
    elif mode == "files":
        import_ras_from_file_dialog()
    else:
        op.lt_exec(f'type -b "Unknown mode: {mode}";')
