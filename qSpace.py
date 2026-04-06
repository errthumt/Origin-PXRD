import originpro as op
import numpy as np
import tkinter as tk
from tkinter import simpledialog

# --- TKINTER PROMPT FOR WAVELENGTH ---
root = tk.Tk()
root.withdraw()

lambda_A = simpledialog.askfloat(
    "Wavelength",
    "Enter X-ray wavelength (Å):",
    initialvalue=1.5406,
    parent=root
)

root.destroy()

# If user cancels, stop script entirely
if lambda_A is None:
    op.lt_exec('type -b "Operation cancelled. No Q columns created.";')
else:
    # If user enters non-positive, fall back to default
    if lambda_A <= 0:
        lambda_A = 1.5406

    # --- MAIN ---
    wks = op.find_sheet()
    ncols = wks.cols

    # Get Units label row
    units = wks.get_labels('U')

    # Get SourceFile label row (user-defined label)
    try:
        sourcefiles = wks.get_labels('SourceFile')
    except:
        sourcefiles = [""] * ncols

    # Loop backwards so shifting doesn't break upcoming indices
    for col in range(ncols - 1, -1, -1):

        unit = units[col].strip().lower() if units[col] else ""

        if unit == "deg":

            # 1) Add one new column at the end
            old_ncols = wks.cols
            wks.cols = old_ncols + 1

            new_col_index = old_ncols
            target_index = col + 1

            # 2) Move the new column into position
            n = target_index - new_col_index   # negative = move left
            wks.move_cols(n, new_col_index, 1)

            q_col = target_index

            # 3) Set Long Name
            wks.set_label(q_col, "Q", 'L')

            # 4) Set Q column as X designation
            wks.cols_axis('x', q_col, q_col, False)

            # 5) Compute Q values with numeric filtering
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

            # 6) Set units using Origin rich-text syntax
            wks.set_label(q_col, "A\\+(-1)", 'U')

            # 7) Copy SourceFile label
            try:
                sourcefiles = wks.get_labels('SourceFile')
            except:
                sourcefiles = [""] * wks.cols

            if len(sourcefiles) < wks.cols:
                sourcefiles += [""] * (wks.cols - len(sourcefiles))

            sourcefiles[q_col] = sourcefiles[col]
            wks.set_label(q_col, sourcefiles[q_col], 'SourceFile')

            ncols += 1
    labtalk_cmd = '''
        @SWS = 0;
        int nCols = wks.ncols;
        if (nCols < 2)
            break;
        for(int ii = 2; ii <= nCols; ii++)
        {
            wcolwidth $(ii) -1
        }
        '''
    op.lt_exec(labtalk_cmd)
    op.lt_exec('type -b "Q-space columns created successfully.";')

