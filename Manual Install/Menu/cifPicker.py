import tkinter as tk
from tkinter import filedialog
import originpro as op
import sys
import os

def pick_cif_files():
    # Create root (hidden)
    root = tk.Tk()
    root.withdraw()

    # Create modal dialog window
    win = tk.Toplevel(root)
    win.title("Select CIF Files")
    win.geometry("600x400")
    win.grab_set()   # Make modal

    file_list = []

    # Listbox
    listbox = tk.Listbox(win, selectmode=tk.MULTIPLE, width=80, height=15)
    listbox.pack(pady=10)

    # Add files
    def add_files():
        paths = filedialog.askopenfilenames(
            title="Select CIF files",
            filetypes=[("CIF files", "*.cif")]
        )
        for p in paths:
            if p not in file_list:
                file_list.append(p)
                listbox.insert(tk.END, p)

    # Remove selected
    def remove_files():
        selected = list(listbox.curselection())
        selected.reverse()
        for idx in selected:
            file_list.pop(idx)
            listbox.delete(idx)

    # OK
    def do_ok():
        win.selected_files = file_list.copy()
        win.destroy()

    # Cancel
    def do_cancel():
        win.selected_files = []
        win.destroy()

    # Buttons
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add File(s)", width=15, command=add_files).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Remove File(s)", width=15, command=remove_files).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="OK", width=15, command=do_ok).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Cancel", width=15, command=do_cancel).grid(row=0, column=3, padx=5)

    # Wait until dialog closes
    win.wait_window()

    # Clean shutdown
    root.destroy()

    return getattr(win, "selected_files", [])


def pick_folder_files():
    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(title="Select Folder Containing CIF Files")
    root.destroy()

    if not folder:
        return []

    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".cif")
    ]


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "file"

    if mode == "folder":
        files = pick_folder_files()
    else:
        files = pick_cif_files()

    joined = ";".join(files).replace("\\", "/")

    # Store file list in a safe LabTalk variable
    op.lt_exec(f'__cif_file_list$ = "{joined}";')

    # Optional: notify user
    op.lt_exec(f'type -b "Selected {len(files)} CIF file(s).";')


