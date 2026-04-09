import originpro as op
import tkinter as tk
from tkinter import ttk
import sys

# --- Helper: Convert 0-based column index to Origin/Excel-style letters ---
def col_index_to_letter(idx):
    letters = ""
    idx += 1  # convert to 1-based
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def gui_select_columns(wks):
    """
    Replacement for the old Tkinter GUI.
    Now returns the list of 0-based column indices
    that the user has selected in the active worksheet.
    """

    selected = []

    # Origin uses 1-based column indices
    for i in range(1, wks.cols + 1):
        is_selected = op.lt_int(f"wks.isColSel({i})")
        if is_selected == 1:
            selected.append(i - 1)  # convert to 0-based

    return selected


# ------------------------------------------------------------
# 1) COLLECT APPLICABLE COLUMNS BASED ON MODE
# ------------------------------------------------------------
def collect_applicable_columns(mode="au"):
    """
    mode = "au"  → return all columns with Units == "AU"
    mode = "gui" → open GUI and let user choose columns
    """
    wks = op.find_sheet()

    if mode.lower() == "gui":
        return gui_select_columns(wks)

    # Default: AU mode
    units = wks.get_labels('U')
    applicable = []

    for col in range(wks.cols):
        unit = units[col].strip().lower() if units[col] else ""
        if unit == "au":
            applicable.append(col)

    return applicable


# ------------------------------------------------------------
# 2) ADD NEW RESCALED COLUMNS FOR EACH INDEX
# ------------------------------------------------------------
def add_columns(col_indices, transform):
    wks = op.find_sheet()

    # Create or get the ScaleFactor user parameter row
    scaleIndex = wks._user_param_row('ScaleFactor', True)
    d_row = scaleIndex + 1

    units = wks.get_labels('U')
    longnames = wks.get_labels('L')
    comments = wks.get_labels('C')

    try:
        sourcefiles = wks.get_labels('SourceFile')
    except:
        sourcefiles = [""] * wks.cols

    # Iterate in reverse so shifting does not break indices
    for col in reversed(col_indices):

        # 1) Add new column at end
        old_ncols = wks.cols
        wks.cols = old_ncols + 1

        new_col_index = old_ncols
        target_index = col + 1

        # 2) Move new column next to original
        n = target_index - new_col_index
        wks.move_cols(n, new_col_index, 1)

        new_col = target_index

        # 3) Long Name transformation
        orig_ln = longnames[col] or ""

        if transform == "scale":
            # Keep original Long Name
            new_ln = orig_ln

        elif transform == "square":
            # Example: Int -> Int\\+(2)
            if orig_ln:
                new_ln = f"{orig_ln}^2"
            else:
                new_ln = "Int^2"

        elif transform == "sqrt":
            # Example: Int -> Int\\+(1/2)
            if orig_ln:
                new_ln = f"sqrt[{orig_ln}]"
            else:
                new_ln = "sqrt[Int]"

        else:
            new_ln = orig_ln  # fallback

        wks.set_label(new_col, new_ln, 'L')


        # 4) Copy Units
        if units[col]:
            wks.set_label(new_col, units[col], 'U')

        # 5) Copy SourceFile
        try:
            sourcefiles = wks.get_labels('SourceFile')
        except:
            sourcefiles = [""] * wks.cols

        if len(sourcefiles) < wks.cols:
            sourcefiles += [""] * (wks.cols - len(sourcefiles))

        sourcefiles[new_col] = sourcefiles[col]
        wks.set_label(new_col, sourcefiles[new_col], 'SourceFile')

        # 6) Copy Comment and append transformation tag
        base_comment = comments[col] or ""

        if transform == "scale":
            suffix = "(Rescaled)"
        elif transform == "square":
            suffix = "(Squared)"
        elif transform == "sqrt":
            suffix = "(Sqrt)"
        else:
            suffix = ""

        # LabTalk-compatible line break is "\n"
        new_comment = f"{base_comment}\n{suffix}" if base_comment else suffix

        wks.set_label(new_col, new_comment, 'C')


        # 7) Process column lettering
        orig_letter = col_index_to_letter(col)
        new_letter  = col_index_to_letter(new_col)
            
        # 8) Apply transformation formula, add scale row if needed
        if transform == "scale":
            # dynamic ScaleFactor row
            lt_set_scale = f"wcol({new_col+1})[D{d_row}] = 0.5;"
            op.lt_exec(lt_set_scale)
            formula_text = f"{new_letter}[D{d_row}] * {orig_letter}"

        elif transform == "square":
            formula_text = f"{orig_letter}^2"

        elif transform == "sqrt":
            formula_text = f"sqrt({orig_letter})"

        else:
            raise ValueError(f"Unknown transform mode: {transform}")

        # Store formula in the Formula label row (dynamic!)
        wks.set_formula(new_col, formula_text)

    op.lt_exec('type -b "Transformed Columns Successfully";')


# ------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    mode = "au"
    transform = "scale"

    if len(sys.argv) > 1:
        mode = sys.argv[1].strip('"')

    if len(sys.argv) > 2:
        transform = sys.argv[2].strip('"')

    cols = collect_applicable_columns(mode)
    add_columns(cols, transform)
