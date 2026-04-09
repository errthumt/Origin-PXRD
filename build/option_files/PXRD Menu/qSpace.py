import originpro as op
import numpy as np
import tkinter as tk
from tkinter import simpledialog
import sys


# ------------------------------------------------------------
# 1) Prompt user for wavelength
# ------------------------------------------------------------
def get_wavelength():
    root = tk.Tk()
    root.withdraw()

    lambda_A = simpledialog.askfloat(
        "Wavelength",
        "Enter X-ray wavelength (Å):",
        initialvalue=1.5406,
        parent=root
    )

    root.destroy()

    if lambda_A is None:
        op.lt_exec('type -b "Operation cancelled. No Q columns created.";')
        return None

    if lambda_A <= 0:
        lambda_A = 1.5406

    return lambda_A


# ------------------------------------------------------------
# 2) Convert a single 2θ column to Q-space
# ------------------------------------------------------------
def convert_column_to_q(wks, col, lambda_A):
    """
    Convert the given 0-based column index (col) from 2θ → Q.
    Creates a new column immediately to the right.
    """

    # 1) Add new column at end
    old_ncols = wks.cols
    wks.cols = old_ncols + 1

    new_col_index = old_ncols
    target_index = col + 1

    # 2) Move new column next to original
    n = target_index - new_col_index
    wks.move_cols(n, new_col_index, 1)

    q_col = target_index

    # 3) Set Long Name
    wks.set_label(q_col, "Q", 'L')

    # 4) Set Q column as X designation
    wks.cols_axis('x', q_col, q_col, False)

    # 5) Compute Q values
    raw_vals = wks.to_list(col)
    Q_out = [""] * len(raw_vals)

    for i, v in enumerate(raw_vals):
        try:
            twotheta = float(v)
            theta = np.radians(twotheta / 2.0)
            Q_out[i] = (4 * np.pi / lambda_A) * np.sin(theta)
        except:
            Q_out[i] = ""

    wks.from_list(q_col, Q_out)

    # 6) Units
    wks.set_label(q_col, "A\\+(-1)", 'U')

    # 7) Copy SourceFile
    try:
        sourcefiles = wks.get_labels('SourceFile')
    except:
        sourcefiles = [""] * wks.cols

    if len(sourcefiles) < wks.cols:
        sourcefiles += [""] * (wks.cols - len(sourcefiles))

    sourcefiles[q_col] = sourcefiles[col]
    wks.set_label(q_col, sourcefiles[q_col], 'SourceFile')


# ------------------------------------------------------------
# 3) Dispatch logic: all_deg OR selected columns
# ------------------------------------------------------------
def dispatch_qspace(mode="all_deg"):
    """
    mode = "all_deg"   → convert all columns with units 'deg'
    mode = "selected"  → convert only user-selected columns
    """

    lambda_A = get_wavelength()
    if lambda_A is None:
        return

    wks = op.find_sheet()
    units = wks.get_labels('U')

    # Determine which columns to convert
    if mode == "all_deg":
        col_indices = [
            col for col in range(wks.cols)
            if (units[col] or "").strip().lower() == "deg"
        ]

    elif mode == "selected":
        col_indices = []
        for i in range(1, wks.cols + 1):  # Origin is 1-based
            if op.lt_int(f"wks.isColSel({i})") == 1:
                col_indices.append(i - 1)

    else:
        op.lt_exec(f'type -b "Unknown mode: {mode}";')
        return

    # Convert in reverse order to avoid index shifting
    for col in reversed(col_indices):
        convert_column_to_q(wks, col, lambda_A)

    # Auto-fit column widths
    op.lt_exec('''
        @SWS = 0;
        int nCols = wks.ncols;
        if (nCols < 2)
            break;
        for(int ii = 2; ii <= nCols; ii++)
        {
            wcolwidth $(ii) -1
        }
    ''')

    op.lt_exec('type -b "Q-space columns created successfully.";')


# ------------------------------------------------------------
# 4) MAIN — dispatch mode from sys.argv
# ------------------------------------------------------------
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "all_deg"
    dispatch_qspace(mode)