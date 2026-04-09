import tkinter as tk
from tkinter import filedialog
import originpro as op
import sys
import os

def pick_cif_files():
    file_select = op.lt_exec('dlgFile init:=%X multi:=1 group:=*.cif title:="Select CIF files to calculate patterns for"')
    file_names = op.get_lt_str('fname$')
    if not file_select or not file_names:
        op.lt_exec('type -b "No files selected"')
        return False
    return True

def pick_folder_files():
    folder_selected = op.lt_exec('dlgPath init:=%X title:="Select folder containing CIF files"; findFiles ext:=*.cif')
    if not folder_selected:
        op.lt_exec('type -b "No folder selected"')
        return False
    
    file_names = op.get_lt_str('fname$')
    if not file_names:
        op.lt_exec('type -b "No CIF files found in the selected folder"')
        return False
    
    return True


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "file"

    if mode == "folder":
        files = pick_folder_files()
    else:
        files = pick_cif_files()


