import originpro as op
import tkinter as tk
from tkinter import filedialog
import glob
import os
import sys

# ------------------------------------------------------------
# 1) Import RAS files from a list of file paths
# ------------------------------------------------------------
def import_ras_files(file_list):
    if not file_list:
        op.lt_exec('type -b "No RAS files to import.";')
        return

    fname_str = "\n".join(file_list)

    labtalk_cmd = fr'''
    @SWS = 0;

    impASC fname:="{fname_str}"
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
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(
        title="Select folder containing RAS files"
    )
    root.destroy()

    if not folder_path:
        op.lt_exec('type -b "No folder selected.";')
        return

    file_paths = glob.glob(os.path.join(folder_path, "*.ras"))

    if not file_paths:
        op.lt_exec('type -b "No RAS files found in folder.";')
        return

    import_ras_files(file_paths)


# ------------------------------------------------------------
# 3) Multi-folder, multi-file selection dialog
# ------------------------------------------------------------
def import_ras_from_file_dialog():
    root = tk.Tk()
    root.title("Select RAS Files")
    root.geometry("600x400")

    file_list = []

    # Listbox to show selected files
    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=15)
    listbox.pack(pady=10)

    # Add files button
    def add_files():
        paths = filedialog.askopenfilenames(
            title="Select RAS files",
            filetypes=[("RAS files", "*.ras")]
        )
        for p in paths:
            if p not in file_list:
                file_list.append(p)
                listbox.insert(tk.END, p)

    # Remove selected files
    def remove_files():
        selected = list(listbox.curselection())
        selected.reverse()  # remove bottom-up
        for idx in selected:
            file_list.pop(idx)
            listbox.delete(idx)

    # Import button
    def do_import():
        root.destroy()
        if not file_list:
            op.lt_exec('type -b "No RAS files selected.";')
            return
        import_ras_files(file_list)

    # Cancel button
    def do_cancel():
        root.destroy()
        op.lt_exec('type -b "Operation cancelled.";')

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add Files", width=15, command=add_files).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Remove Selected", width=15, command=remove_files).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Import", width=15, command=do_import).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Cancel", width=15, command=do_cancel).grid(row=0, column=3, padx=5)

    root.mainloop()


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
