# Older versions required CIF files to be picked in a separate module call than import because of conflicting tkinter instances
# This can eventually be refactored into cifImp.py. Menu commands would need to be changed.
import originpro as op
import sys

# Select individual files. Uses Origin's native dlfFile dialog
def pick_cif_files():
    file_select = op.lt_exec('dlgFile init:=%X multi:=1 group:=*.cif title:="Select CIF files to calculate patterns for"')
    # dlgFile automatically stores filenames under global variable fname$
    file_names = op.get_lt_str('fname$')
    if not file_select or not file_names:
        op.lt_exec('type -b "No files selected"')
        return False
    return True

# Select folder containing all desired files. Uses Origin's native dlfPath dialog.
def pick_folder_files():
    # dlgPath stores folder path under path$. findFiles finds all matching files in path$ and stores in fname$
    folder_selected = op.lt_exec('dlgPath init:=%X title:="Select folder containing CIF files"; findFiles ext:=*.cif')
    if not folder_selected:
        op.lt_exec('type -b "No folder selected"')
        return False
    
    file_names = op.get_lt_str('fname$')
    if not file_names:
        op.lt_exec('type -b "No CIF files found in the selected folder"')
        return False
    
    return True

# Dispatch using arguments passed in labtalk call.
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "file"

    if mode == "folder":
        files = pick_folder_files()
    else:
        files = pick_cif_files()


