import warnings

# Axes3D is not included with Origin's native matplotlib, but it is not necessary for this package
warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D",
    category=UserWarning,
    module="matplotlib.projections"
)


import tkinter as tk
root = tk.Tk()
root.withdraw() # Origin is picky about when to display tk windows.

import os
import sys
import originpro as op #type: ignore

import numpy as np #type: ignore
from pymatgen.io.cif import CifParser #type: ignore
from pymatgen.core import Structure #type: ignore
from pymatgen.core.periodic_table import Element #type: ignore
from pymatgen.analysis.diffraction.xrd import XRDCalculator #type: ignore


# Extra dampening to match VESTA's peak heights
_B_EXTRA = 0.4

# Fix column headers, normalize columns, remove function row.
# Executed as a labtalk command near the end of this script.
def lt_cleanup(normalize=True):
    LABTALK_CLEANUP = fr'''
    @SWS = 0;

    int nCols = wks.ncols;
    if (nCols < 2)
        break;

    wks.UserParam1 = 1;
    wks.UserParam1$ = "SourceFile";

    wks.col1.lname$ = "2θ";
    wks.col1.unit$ = "deg";

    for(int ii = 2; ii <= nCols; ii++)
    {{
        string lng$ = wks.col$(ii).lname$;
        wcol(ii)[SourceFile]$ = lng$;

        wks.col$(ii).lname$ = "Int";
        {'rnormalize irng:=$(ii) method:=1 orng:=$(ii)' if normalize else ""};
        wks.col$(ii).unit$ = "AU";
        
        wcolwidth $(ii) -1;
    }};

    wks.labels(-O);
    '''
    return LABTALK_CLEANUP



#  TCH pseudo-approximation of Voight peak shape
def tch_pseudo_voigt(two_theta, t0, H_G, H_L):
    H = (H_G**5 + 2.69269*H_G**4*H_L + 2.42843*H_G**3*H_L**2 +
         4.47163*H_G**2*H_L**3 + 0.07842*H_G*H_L**4 + H_L**5)**0.2

    eta = 1.36603*(H_L/H) - 0.47719*(H_L/H)**2 + 0.11116*(H_L/H)**3
    eta = np.clip(eta, 0, 1)

    sigma = H / (2*np.sqrt(2*np.log(2)))
    gamma = H / 2

    G = np.exp(-((two_theta - t0)**2) / (2*sigma**2))
    L = 1 / (1 + ((two_theta - t0)/gamma)**2)

    pv = eta * L + (1 - eta) * G
    pv /= pv.sum() + 1e-12
    return pv

#  Gaussian approximation of Finger-Cox-Jephcoat axial divergence asymmetry (peak tailing)
def fcj_asymmetry(two_theta, t0, H, S=0.015):
    delta = S * np.tan(np.radians(t0/2))
    shift = delta * (two_theta - t0)
    return np.exp(-shift**2 / (2*H**2))

def compute_Z(structure=None, cif_path=None):
    """
    Compute Z (formula units per unit cell) using the most reliable source:
    1. If cif_path is provided and CIF contains _cell_formula_units_Z, use it.
    2. Otherwise fall back to computing Z from the Structure object.
    """

    # --- Case 1: Try reading Z directly from CIF ---
    if cif_path is not None:
        parser = CifParser(cif_path)
        cif_blocks = parser.as_dict()  # dict of CIF blocks

        # Usually only one block, but loop safely
        for block in cif_blocks.values():
            # Try the canonical key
            if "_cell_formula_units_Z" in block:
                try:
                    return float(block["_cell_formula_units_Z"])
                except Exception:
                    pass

            # Try common variants (CIFs are messy)
            for key in block.keys():
                if key.lower().endswith("formula_units_z"):
                    try:
                        return float(block[key])
                    except Exception:
                        pass

        # If we reach here, CIF did not contain Z → fall back

        structure = parser.get_structures()[0]

    # --- Case 2: Compute Z from Structure ---
    if structure is None:
        raise ValueError("Either structure or cif_path must be provided.")

    comp = structure.composition
    full_atoms = comp.num_atoms
    formula_atoms = comp.reduced_composition.num_atoms

    return full_atoms / formula_atoms

def absorption_proxy(structure, n=2.5):
    """
    Compute a universal absorption proxy:
        μ = Σ (w_i * Z_i^n)
    where w_i is the weight fraction of element i.
    """
    comp = structure.composition
    total_mass = comp.weight

    mu = 0.0
    for species, amount in comp.items():
        symbol = species.symbol          # strip oxidation state
        Z = Element(symbol).Z            # atomic number
        mass = Element(symbol).atomic_mass
        w_i = (amount * mass) / total_mass  # weight fraction
        mu += w_i * (Z ** n)

    return mu



# Core diffraction engine
def calculate_pattern(
    cif_path,
    fe_wavelengths,
    fe_weights,
    two_theta_range,
    step,
    U=0.0,
    V=0.0,
    W=0.012,
    X=0.0,
    Y=0.0,
    axial_S=0.015
):
    # Read CIF file using pymatgen's Structure module
    structure = Structure.from_file(cif_path)
    Z = compute_Z(structure,cif_path)

    # Build list of B values for each atom site
    atom_B = []
    pi2 = np.pi**2
    for site in structure.sites:
        props = site.properties
        if "B_iso" in props:
            B = props["B_iso"]
        elif "Uiso" in props:
            B = 8 * pi2 * props["Uiso"]
        elif "Ueq" in props:
            B = 8 * pi2 * props["Ueq"]
        else:
            B = 0.0
        atom_B.append(B)

    # Generate 2theta column and empty intensity column of same length.
    tmin, tmax = two_theta_range
    two_theta = np.arange(tmin, tmax + step, step)
    intensity = np.zeros_like(two_theta)
    fe_weights = np.array(fe_weights)/np.sum(fe_weights)
    
    # Generate intensity as the sum of all fe intensities by weights.
    for wl, wt in zip(fe_wavelengths, fe_weights):
        # Basic reflections calculated using pymatgen's XRDCalculator.get_pattern()
        xrd = XRDCalculator(wavelength=wl)
        pattern = xrd.get_pattern(structure, two_theta_range=two_theta_range, scaled=False)
        cell_volume = structure.lattice.volume
        mu = absorption_proxy(structure) # This is very fudgy
        # Modify reflections with scattering factors
        for idx, (t0, I0) in enumerate(zip(pattern.x, pattern.y)):
            # Useful constants
            theta = np.radians(t0 / 2)
            sin_th = np.sin(theta)
            cos_th = np.cos(theta)
                
            # Useful constants
            s = sin_th / wl
            pi2 = np.pi**2

            # Extra dampening defined at head of this file.
            B_extra = _B_EXTRA

            # Debye-Waller damping by B-factors
            DW_atoms = np.mean([np.exp(-2 * pi2 * B * s**2) for B in atom_B])
            # Fudge factor to match experimental/VESTA heights. (not currently in use)
            DW_extra = np.exp(-2 * pi2 * B_extra * s**2)

            # Modify base intensity with damping
            I0 *= DW_atoms #* DW_extra
            I0 /= Z
            I0 /= cell_volume

            # Caglioti broadening: Gaussian (H_G) and Lorentzian (HL) hybrid
            H_G = np.sqrt(U*np.tan(theta)**2 + V*np.tan(theta) + W)
            H_L = X*np.tan(theta) + Y/np.cos(theta)

            # Each peak is calculated indepedently as a function of all 2theta values.
            pv = tch_pseudo_voigt(two_theta, t0, H_G, H_L)
            asym = fcj_asymmetry(two_theta, t0, H_G, S=axial_S)

            # Peak is a normalized Voight-shape, with tailing added, multiplied by intensity and wavelength weight.
            # Each individual peak is constructed as a function of all 2theta values. They are all overlaid onto the intensity series.
            intensity += wt * I0 * pv * asym

    # Returns series, not indiviual values
    return two_theta, intensity

default_parameters = {
    "book_name":"CIF Imports",
    "file_mode":"files",
    "doublet": True,
    "wavelength1": 1.5406,
    "weight1":1.0,
    "wavelength2":1.54439,
    "weight2":0.5,
    "start_2th":3.0,
    "end_2th":90.0,
    "step_2th":0.2,
    "U":0.0,
    "V":0.0,
    "W":0.012,
    "X":0.0,
    "Y":0.0,
    "axial_S":0.015,
    "normalize_mode":True
}

def clean_parameters(params):
    new_params = {}
    for key in default_parameters:
        def_val = default_parameters[key]
        def_type = type(def_val)

        new_val = params.get(key)
        if not new_val:
            new_params[key] = def_val
        elif def_type == bool:
            new_params[key] = new_val.lower() == 'true'
        elif def_type != type(new_val):
            try:
                new_params[key] = def_type(new_val)
            except:
                print(f"Incompatible type passed for '{key}'. Defaulting to '{def_val}'")
                new_params[key] = def_val
        else:
            new_params[key] = params[key]

    return new_params

def get_cif_parameters(cleaned_params):
    cif_params = cleaned_params.copy()
    doublet = cif_params.pop("doublet")
    wavelength1 = cif_params.pop("wavelength1")
    weight1 = cif_params.pop("weight1")
    wavelength2 = cif_params.pop("wavelength2")
    weight2 = cif_params.pop("weight2")
    start_2th = cif_params.pop("start_2th")
    end_2th = cif_params.pop("end_2th")
    step = cif_params.pop("step_2th")

    if doublet:
        cif_params["fe_wavelengths"]=[wavelength1,wavelength2]
        cif_params["fe_weights"]=[weight1,weight2]
    else:
        cif_params["fe_wavelengths"]=[wavelength1]
        cif_params["fe_weights"]=[1.0]

    cif_params["two_theta_range"] = (start_2th,end_2th)
    cif_params["step"]=step

    return cif_params

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

#  Major import function
def import_cif_files(cleaned_params):
    file_mode = cleaned_params["file_mode"]
    normalize = cleaned_params["normalize_mode"]

    if file_mode=='folder':
        picked = pick_folder_files()
    else:
        picked = pick_cif_files()

    if not picked:
        return

    # Read the LabTalk variable fname$
    raw_list = op.get_lt_str('fname$')

    if raw_list:
        # Normalize Windows newlines and split into lines
        file_list = [
            f.strip()
            for f in raw_list.replace("\r\n", "\n").split("\n")
            if f.strip()
        ]
    else:
        return

    # Get parameters, unpack wavelength
    params = get_cif_parameters(cleaned_params)
    wavelength = params["fe_wavelengths"][0]

    # Create new book
    wb = op.new_book('w', lname=cleaned_params["book_name"])
    wks = wb[0]

    # Start with no existing 2theta column, starting with first column.
    first_two_theta = None
    col_index = 0

    for cif_path in sorted(file_list):
        two_theta, intensity = calculate_pattern(
            cif_path,
            fe_wavelengths=params["fe_wavelengths"],
            fe_weights=params["fe_weights"],
            two_theta_range=params["two_theta_range"],
            step=params["step"],
            U=params["U"],
            V=params["V"],
            W=params["W"],
            X=params["X"],
            Y=params["Y"],
            axial_S=params["axial_S"],
        )

        # Only write 2theta column once.
        if first_two_theta is None:
            first_two_theta = two_theta
            wks.from_list(col_index, first_two_theta, lname='2Theta')
            col_index += 1

        # Write intensity for each CIF
        sample_name = os.path.splitext(os.path.basename(cif_path))[0]
        wks.from_list(col_index, intensity, lname=sample_name)
        col_index += 1

    # Labtalk cleanup
    wb.activate()
    wks.activate()
    op.lt_exec(lt_cleanup(normalize))
    
    # Create wavelength row expected by Q-space menu
    wks._user_param_row("Wavelength (Å)",True)
    wks.set_label(0,wavelength, "Wavelength (Å)")

    # Hide unwanted parameters.
    for uParam in ("Group Info","Method"):
        idx = wks._user_param_row(uParam,True) + 1
        op.lt_exec(f"wks.labels(#D{idx});")

def parse_params(s):
    items = s.split(',')
    out = {}
    for item in items:
        try:
            key, val = item.split(':')
            out[key.strip()] = val.strip()
        except:
            print(f"Error parsing option '{item}'. Excluding from parsed parameters")
    return out       

# Dispatch with labtalk string arg for parameters dict
if __name__ == "__main__":
    paramString = sys.argv[1] if len(sys.argv) > 1 else ""
    params = parse_params(paramString)
    cleaned_params = clean_parameters(params)



    import_cif_files(cleaned_params)


