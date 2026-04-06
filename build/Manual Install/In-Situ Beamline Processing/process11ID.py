# TEST SUCCESSFUL

import os
import re
import originpro as op
from pathlib import Path

op.lt_exec('dlgPath title:="Select sample ID folder (contains xye folder and all metadata files)";')
root = Path(op.get_lt_str("path$"))

# --- USER CONFIGURATION ---
xye_folder = root / "xye"
metadata_folder = root
output_folder = root / "xye_withTemp"

output_folder.mkdir(parents=True, exist_ok=True)

# Regex to capture: userComment4=123.45
temp_pattern = re.compile(r"^userComment4\s*=\s*(.+)$")

def extract_temperature(metadata_path):
    """Return the temperature string from a .tif.metadata file."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        for line in f:
            m = temp_pattern.match(line.strip())
            if m:
                return m.group(1).strip()
    return None


for xye_file in xye_folder.glob("*.xye"):
    base = xye_file.stem  # filename without extension
    metadata_file = metadata_folder / f"{base}.tif.metadata"

    if not metadata_file.exists():
        print(f"WARNING: No metadata for {base}")
        continue

    temperature = extract_temperature(metadata_file)
    if temperature is None:
        print(f"WARNING: No userComment4 entry in {metadata_file}")
        continue

    # Read original .xye
    with open(xye_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        print(f"WARNING: Empty file: {xye_file}")
        continue

    # Modify first line
    first_line = lines[0].rstrip("\n")
    new_first_line = f"{first_line}  {temperature}\n"

    # Write new file
    out_path = output_folder / xye_file.name
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new_first_line)
        f.writelines(lines[1:])

    print(f"Processed: {xye_file.name}  →  Temp={temperature}")
print("All temperatures added to xye files.")


wb = op.new_book('w',lname="In-Situ Import")
wks = wb[0]

import_lt = f'''
cd path$;
findFiles ext:=*.xye;
impFile filtername:="11-ID-2_mar2026.oif" location:=user;
wks.labels(-O)
'''

op.set_lt_str("path$",f"{output_folder}\\")
op.lt_exec(import_lt)

ncols = wks.cols
maxInt = 0
for col in range(ncols-1,0,-1):
    if col%2==0:
        wks.del_col(col)
    else:
        wks.set_label(col,'Int','L')
        wks.set_label(col,'AU','U')
        
        col_data = wks.to_list(col)
        local_max = max(col_data)
        if local_max > maxInt:
            maxInt = local_max

wks.set_label(0,'2θ','L')
wks.set_label(0,'deg','U')

ncols = wks.cols        
for col in range(1,ncols,1):
    data = wks.to_list(col)
    norm = [v/maxInt for v in data]
    wks.from_list(col,norm)
    
    op.lt_exec(f'wcolwidth {col+1} -1')
    
