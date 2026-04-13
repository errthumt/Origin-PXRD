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
from pymatgen.core import Structure #type: ignore
from pymatgen.analysis.diffraction.xrd import XRDCalculator #type: ignore

import math

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



#  Atomic Scattering Factors (f0 + f' + f'')
ANOMALOUS = {
    "H":  {"f1": 0.000, "f2": 0.000},
    "He": {"f1": 0.000, "f2": 0.000},
    "Li": {"f1": -0.001, "f2": 0.000},
    "Be": {"f1": -0.002, "f2": 0.000},
    "B":  {"f1": -0.005, "f2": 0.001},
    "C":  {"f1": -0.007, "f2": 0.002},
    "N":  {"f1": -0.009, "f2": 0.003},
    "O":  {"f1": -0.010, "f2": 0.005},
    "F":  {"f1": -0.015, "f2": 0.008},
    "Ne": {"f1": -0.020, "f2": 0.010},
    "Na": {"f1": -0.030, "f2": 0.015},
    "Mg": {"f1": -0.040, "f2": 0.020},
    "Al": {"f1": -0.050, "f2": 0.030},
    "Si": {"f1": -0.150, "f2": 0.080},
    "P":  {"f1": -0.200, "f2": 0.100},
    "S":  {"f1": -0.250, "f2": 0.120},
    "Cl": {"f1": -0.300, "f2": 0.150},
    "Ar": {"f1": -0.350, "f2": 0.180},
    "K":  {"f1": -0.400, "f2": 0.200},
    "Ca": {"f1": -0.450, "f2": 0.250},
    "Sc": {"f1": -0.500, "f2": 0.300},
    "Ti": {"f1": -0.550, "f2": 0.350},
    "V":  {"f1": -0.600, "f2": 0.400},
    "Cr": {"f1": -0.650, "f2": 0.450},
    "Mn": {"f1": -0.700, "f2": 0.500},
    "Fe": {"f1": -0.750, "f2": 0.550},
    "Co": {"f1": -0.900, "f2": 0.600},
    "Ni": {"f1": -1.100, "f2": 0.620},
    "Cu": {"f1": -1.278, "f2": 0.639},
    "Zn": {"f1": -1.400, "f2": 0.650},
    "Ga": {"f1": -1.500, "f2": 0.700},
    "Ge": {"f1": -1.600, "f2": 0.750},
    "As": {"f1": -1.700, "f2": 0.800},
    "Se": {"f1": -1.800, "f2": 0.850},
    "Br": {"f1": -2.000, "f2": 1.000},
    "Kr": {"f1": -2.200, "f2": 1.200},
    "Rb": {"f1": -2.400, "f2": 1.400},
    "Sr": {"f1": -2.600, "f2": 1.600},
    "Y":  {"f1": -2.800, "f2": 1.800},
    "Zr": {"f1": -3.000, "f2": 2.000},
    "Nb": {"f1": -3.200, "f2": 2.200},
    "Mo": {"f1": -3.400, "f2": 2.400},
    "Tc": {"f1": -3.600, "f2": 2.600},
    "Ru": {"f1": -3.800, "f2": 2.800},
    "Rh": {"f1": -4.000, "f2": 3.000},
    "Pd": {"f1": -4.200, "f2": 3.200},
    "Ag": {"f1": -4.400, "f2": 3.400},
    "Cd": {"f1": -4.600, "f2": 3.600},
    "In": {"f1": -4.800, "f2": 3.800},
    "Sn": {"f1": -5.000, "f2": 4.000},
    "Sb": {"f1": -5.200, "f2": 4.200},
    "Te": {"f1": -5.400, "f2": 4.400},
    "I":  {"f1": -5.600, "f2": 4.600},
    "Xe": {"f1": -5.800, "f2": 4.800},
    "Cs": {"f1": -6.000, "f2": 5.000},
    "Ba": {"f1": -6.200, "f2": 5.200},
    "La": {"f1": -6.400, "f2": 5.400},
    "Ce": {"f1": -6.600, "f2": 5.600},
    "Pr": {"f1": -6.800, "f2": 5.800},
    "Nd": {"f1": -7.000, "f2": 6.000},
    "Pm": {"f1": -7.200, "f2": 6.200},
    "Sm": {"f1": -7.400, "f2": 6.400},
    "Eu": {"f1": -7.600, "f2": 6.600},
    "Gd": {"f1": -7.800, "f2": 6.800},
    "Tb": {"f1": -8.000, "f2": 7.000},
    "Dy": {"f1": -8.200, "f2": 7.200},
    "Ho": {"f1": -8.400, "f2": 7.400},
    "Er": {"f1": -8.600, "f2": 7.600},
    "Tm": {"f1": -8.800, "f2": 7.800},
    "Yb": {"f1": -9.000, "f2": 8.000},
    "Lu": {"f1": -9.200, "f2": 8.200},
    "Hf": {"f1": -9.400, "f2": 8.400},
    "Ta": {"f1": -9.600, "f2": 8.600},
    "W":  {"f1": -9.800, "f2": 8.800},
    "Re": {"f1": -10.000, "f2": 9.000},
    "Os": {"f1": -10.200, "f2": 9.200},
    "Ir": {"f1": -10.400, "f2": 9.400},
    "Pt": {"f1": -10.600, "f2": 9.600},
    "Au": {"f1": -10.800, "f2": 9.800},
    "Hg": {"f1": -11.000, "f2": 10.000},
    "Tl": {"f1": -11.200, "f2": 10.200},
    "Pb": {"f1": -11.400, "f2": 10.400},
    "Bi": {"f1": -11.600, "f2": 10.600},
    "Po": {"f1": -11.800, "f2": 10.800},
    "At": {"f1": -12.000, "f2": 11.000},
    "Rn": {"f1": -12.200, "f2": 11.200},
    "Fr": {"f1": -12.400, "f2": 11.400},
    "Ra": {"f1": -12.600, "f2": 11.600},
    "Ac": {"f1": -12.800, "f2": 11.800},
    "Th": {"f1": -13.000, "f2": 12.000},
    "Pa": {"f1": -13.200, "f2": 12.200},
    "U":  {"f1": -13.400, "f2": 12.400},
}

# Gets and unpacks scattering factors for a given element. Returns 0's if not found.
def fprime_fdoubleprime(element):
    data = ANOMALOUS.get(element)
    if data:
        return data["f1"], data["f2"]
    print(f'WARNING: No scattering factors tabulated for element "{element}". Returned as zero')
    return 0.0, 0.0

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

    # Generate intensity as the sum of all fe intensities by weights.
    for wl, wt in zip(fe_wavelengths, fe_weights):
        # Basic reflections calculated using pymatgen's XRDCalculator.get_pattern()
        xrd = XRDCalculator(wavelength=wl)
        pattern = xrd.get_pattern(structure, two_theta_range=two_theta_range)

        # Modify reflections with scattering factors
        for idx, (t0, I0) in enumerate(zip(pattern.x, pattern.y)):
            # Useful constants
            theta = np.radians(t0 / 2)
            sin_th = np.sin(theta)
            cos_th = np.cos(theta)

            # Get atoms
            atoms = structure.sites

            ''' No longer in use: anomalous scattering correction
            # Get hkl's
            hkl = pattern.hkls[idx][0]["hkl"]

            # Start with base scattering factors.
            fscale = 0.0
            for atom, B in zip(atoms, atom_B):
                f1, f2 = fprime_fdoubleprime(atom.species_string)
                fscale += (f1 + f2)
            '''
                
            # Useful constants
            s = sin_th / wl
            pi2 = np.pi**2

            # Extra dampening defined at head of this file.
            B_extra = _B_EXTRA

            # Debye-Waller damping by B-factors
            DW_atoms = np.mean([np.exp(-2 * pi2 * B * s**2) for B in atom_B])
            # Fudge factor to match experimental/VESTA heights.
            DW_extra = np.exp(-2 * pi2 * B_extra * s**2)

            # Modify base intensity with damping
            I0 *= DW_atoms * DW_extra

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
    wb = op.new_book('w', lname='CIF Imports')
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


