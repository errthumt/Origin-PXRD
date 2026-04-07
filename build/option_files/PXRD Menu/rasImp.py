# TEST SUCCEEDED

import originpro as op
import os
import sys

# ------------------------------------------------------------
# 1) Import RAS files from a list of file paths
# ------------------------------------------------------------
def import_ras_files():

    labtalk_cmd = fr'''
    @SWS = 0;

    impASC fname:=fname$
    options.Sparklines:=0
    options.FirstMode:=3
    options.Mode:=1
    options.headers.AutoSubHeaderLines:=0
    options.headers.CountHeaderLines:=1
    options.headers.HeaderLeadingChar:=*
    options.Cols.NumCols:=2
    options.Cols.ColDesignations:=(XY)
    options.names.FNameToSht:=0
    options.names.FNameToBk:=0
    options.names.FNameToUDL:=1
    options.Miscs.NonNum:=5
    options.scripts.ScriptAfterAllImport:=]>;

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
    
    op.lt_exec(labtalk_cmd)
    
    # Declare worksheet
    wks = op.find_sheet()
    
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

    folder_path = op.lt_exec('dlgPath title:="Select folder containing RAS files"; findFiles ext:=*.ras;')

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
    file_select = op.lt_exec('dlgFile multi:=1 title:="Select RAS files for import" group:=*.ras')
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
