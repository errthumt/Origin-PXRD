import warnings
warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D",
    category=UserWarning,
    module="matplotlib.projections"
)


import tkinter as tk
root = tk.Tk()
root.withdraw()   # Must be created BEFORE importing originpro

import os
import sys
import originpro as op

import numpy as np
from pymatgen.core import Structure
from pymatgen.analysis.diffraction.xrd import XRDCalculator

LABTALK_CLEANUP = r'''
@SWS = 0;

int nCols = wks.ncols;
if (nCols < 2)
    break;

wks.UserParam1 = 1;
wks.UserParam1$ = "SourceFile";

wks.col1.lname$ = "2θ";
wks.col1.unit$ = "deg";

for(int ii = 2; ii <= nCols; ii++)
{
    string lng$ = wks.col$(ii).lname$;
    wcol(ii)[SourceFile]$ = lng$;

    wks.col$(ii).lname$ = "Int";
    rnormalize irng:=$(ii) method:=1 orng:=$(ii);
    wks.col$(ii).unit$ = "AU";
    
    wcolwidth $(ii) -1;
};

wks.labels(-O);
'''


# ----------------------------------------------------------------------
#  ATOMIC SCATTERING FACTORS (f0 + f' + f'')
# ----------------------------------------------------------------------
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

def fprime_fdoubleprime(element):
    data = ANOMALOUS.get(element)
    if data:
        return data["f1"], data["f2"]
    return 0.0, 0.0

# ----------------------------------------------------------------------
#  TCH PSEUDO-VOIGT
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
#  FCJ ASYMMETRY
# ----------------------------------------------------------------------
def fcj_asymmetry(two_theta, t0, H, S=0.015):
    delta = S * np.tan(np.radians(t0/2))
    shift = delta * (two_theta - t0)
    return np.exp(-shift**2 / (2*H**2))

# ----------------------------------------------------------------------
#  CORE DIFFRACTION ENGINE (from calculate_pattern_vesta_exact)
# ----------------------------------------------------------------------
def calculate_pattern_vesta_exact(
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
    structure = Structure.from_file(cif_path)

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

    tmin, tmax = two_theta_range
    two_theta = np.arange(tmin, tmax + step, step)
    intensity = np.zeros_like(two_theta)

    for wl, wt in zip(fe_wavelengths, fe_weights):
        xrd = XRDCalculator(wavelength=wl)
        pattern = xrd.get_pattern(structure, two_theta_range=two_theta_range)

        for idx, (t0, I0) in enumerate(zip(pattern.x, pattern.y)):
            theta = np.radians(t0 / 2)
            sin_th = np.sin(theta)
            cos_th = np.cos(theta)

            hkl = pattern.hkls[idx][0]["hkl"]
            atoms = structure.sites

            fscale = 0.0
            for atom, B in zip(atoms, atom_B):
                f1, f2 = fprime_fdoubleprime(atom.species_string)
                fscale += (f1 + f2)
            # optional: I0 *= (1 + fscale * 0.02)

            s = sin_th / wl
            pi2 = np.pi**2
            B_extra = 0.4

            DW_atoms = np.mean([np.exp(-2 * pi2 * B * s**2) for B in atom_B])
            DW_extra = np.exp(-2 * pi2 * B_extra * s**2)

            I0 *= DW_atoms * DW_extra

            H_G = np.sqrt(U*np.tan(theta)**2 + V*np.tan(theta) + W)
            H_L = X*np.tan(theta) + Y/np.cos(theta)

            pv = tch_pseudo_voigt(two_theta, t0, H_G, H_L)
            asym = fcj_asymmetry(two_theta, t0, H_G, S=axial_S)

            intensity += wt * I0 * pv * asym

    return two_theta, intensity

# ----------------------------------------------------------------------
#  PARAMETER HANDLING
# ----------------------------------------------------------------------
def get_default_parameters():
    return {
        "fe_wavelengths": [1.5406, 1.54439],
        "fe_weights": [1.0, 0.5],
        "two_theta_range": (3.0, 90.0),
        "step": 0.02,
        "U": 0.0,
        "V": 0.0,
        "W": 0.012,
        "X": 0.0,
        "Y": 0.0,
        "axial_S": 0.015,
    }

def get_custom_parameters(start_dir):
    # Default PXRD parameters
    DEFAULT_WAVELENGTHS = [1.5406, 1.54439]
    DEFAULT_WEIGHTS     = [1.0,    0.5]
    DEFAULT_TMIN        = 3.0
    DEFAULT_TMAX        = 90.0
    DEFAULT_STEP        = 0.01
    DEFAULT_U           = 0.0
    DEFAULT_V           = 0.0
    DEFAULT_W           = 0.012
    DEFAULT_X           = 0.0
    DEFAULT_Y           = 0.0
    DEFAULT_S           = 0.015

    win = tk.Toplevel()
    win.title("CIF Import Parameters")

    # -----------------------------
    # WAVELENGTH SECTION
    # -----------------------------
    def update_wavelength_fields(*args):
        for widget in wl_frame.winfo_children():
            widget.destroy()
        wl_entries.clear()
        wt_entries.clear()

        count = fe_count_var.get()

        for i in range(count):
            tk.Label(wl_frame, text=f"fE{i+1} λ (Å):").grid(row=i, column=0, sticky="e")

            default_wl = DEFAULT_WAVELENGTHS[i] if i < len(DEFAULT_WAVELENGTHS) else DEFAULT_WAVELENGTHS[0]
            wv = tk.DoubleVar(value=default_wl)
            tk.Entry(wl_frame, textvariable=wv, width=10).grid(row=i, column=1)
            wl_entries.append(wv)

            tk.Label(wl_frame, text=f"Weight:").grid(row=i, column=2, sticky="e")

            default_wt = DEFAULT_WEIGHTS[i] if i < len(DEFAULT_WEIGHTS) else DEFAULT_WEIGHTS[1]
            wt = tk.DoubleVar(value=default_wt)
            tk.Entry(wl_frame, textvariable=wt, width=6).grid(row=i, column=3)
            wt_entries.append(wt)

    def submit():
        win.destroy()

    tk.Label(win, text="Number of fE wavelengths:").grid(row=0, column=0, sticky="e")
    fe_count_var = tk.IntVar(value=2)
    tk.OptionMenu(win, fe_count_var, *range(1, 6)).grid(row=0, column=1, sticky="w")

    wl_frame = tk.Frame(win)
    wl_frame.grid(row=1, column=0, columnspan=3, pady=5)
    wl_entries = []
    wt_entries = []

    fe_count_var.trace_add("write", update_wavelength_fields)
    update_wavelength_fields()

    # -----------------------------
    # BASIC PARAMETERS
    # -----------------------------
    tk.Label(win, text="2θ Min (deg):").grid(row=2, column=0, sticky="e")
    tmin_var = tk.DoubleVar(value=DEFAULT_TMIN)
    tk.Entry(win, textvariable=tmin_var).grid(row=2, column=1)

    tk.Label(win, text="2θ Max (deg):").grid(row=3, column=0, sticky="e")
    tmax_var = tk.DoubleVar(value=DEFAULT_TMAX)
    tk.Entry(win, textvariable=tmax_var).grid(row=3, column=1)

    tk.Label(win, text="Step Size (deg):").grid(row=4, column=0, sticky="e")
    step_var = tk.DoubleVar(value=DEFAULT_STEP)
    tk.Entry(win, textvariable=step_var).grid(row=4, column=1)

    # -----------------------------
    # ADVANCED PARAMETERS (HIDDEN)
    # -----------------------------
    advanced_frame = tk.Frame(win)
    advanced_visible = False  # toggle state

    def toggle_advanced():
        nonlocal advanced_visible
        if advanced_visible:
            advanced_frame.grid_remove()
            adv_button.config(text="Show Advanced ▼")
        else:
            advanced_frame.grid(row=6, column=0, columnspan=3, pady=5)
            adv_button.config(text="Hide Advanced ▲")
        advanced_visible = not advanced_visible

    adv_button = tk.Button(win, text="Show Advanced ▼", command=toggle_advanced)
    adv_button.grid(row=5, column=0, columnspan=3, pady=5)

    # Advanced fields inside advanced_frame
    tk.Label(advanced_frame, text="U:").grid(row=0, column=0, sticky="e")
    U_var = tk.DoubleVar(value=DEFAULT_U)
    tk.Entry(advanced_frame, textvariable=U_var).grid(row=0, column=1)

    tk.Label(advanced_frame, text="V:").grid(row=1, column=0, sticky="e")
    V_var = tk.DoubleVar(value=DEFAULT_V)
    tk.Entry(advanced_frame, textvariable=V_var).grid(row=1, column=1)

    tk.Label(advanced_frame, text="W:").grid(row=2, column=0, sticky="e")
    W_var = tk.DoubleVar(value=DEFAULT_W)
    tk.Entry(advanced_frame, textvariable=W_var).grid(row=2, column=1)

    tk.Label(advanced_frame, text="X:").grid(row=3, column=0, sticky="e")
    X_var = tk.DoubleVar(value=DEFAULT_X)
    tk.Entry(advanced_frame, textvariable=X_var).grid(row=3, column=1)

    tk.Label(advanced_frame, text="Y:").grid(row=4, column=0, sticky="e")
    Y_var = tk.DoubleVar(value=DEFAULT_Y)
    tk.Entry(advanced_frame, textvariable=Y_var).grid(row=4, column=1)

    tk.Label(advanced_frame, text="Axial S:").grid(row=5, column=0, sticky="e")
    S_var = tk.DoubleVar(value=DEFAULT_S)
    tk.Entry(advanced_frame, textvariable=S_var).grid(row=5, column=1)

    # Start hidden
    advanced_frame.grid_remove()

    # -----------------------------
    # OK BUTTON
    # -----------------------------
    tk.Button(win, text="OK", command=submit).grid(row=7, column=1, pady=10)

    win.grab_set()
    win.wait_window()

    return {
        "fe_wavelengths": [v.get() for v in wl_entries],
        "fe_weights": [v.get() for v in wt_entries],
        "two_theta_range": (tmin_var.get(), tmax_var.get()),
        "step": step_var.get(),
        "U": U_var.get(),
        "V": V_var.get(),
        "W": W_var.get(),
        "X": X_var.get(),
        "Y": Y_var.get(),
        "axial_S": S_var.get(),
    }




def get_parameters(mode):
    proj_path = op.path('p')
    start_dir = os.path.dirname(proj_path) if proj_path and os.path.isfile(proj_path) else os.getcwd()

    if mode.lower() == "cuka":
        return get_default_parameters()
    else:
        return get_custom_parameters(start_dir)




# ----------------------------------------------------------------------
#  HIGH-LEVEL IMPORT: FROM LIST OF FILES
# ----------------------------------------------------------------------
def import_cif_files(file_list, wavelength_mode):
    #print("DEBUG: Entered import_cif_files()")
    #print("DEBUG: file_list =", file_list)
    #print("DEBUG: wavelength_mode =", wavelength_mode)

    params = get_parameters(wavelength_mode)
    #print("DEBUG: Parameters loaded:", params)

    wb = op.new_book('w', lname='CIF Imports')
    #print("DEBUG: Workbook created")

    wks = wb[0]
    #print("DEBUG: Worksheet created")

    first_two_theta = None
    col_index = 0

    for cif_path in sorted(file_list):
        #print("DEBUG: Processing file:", cif_path)

        two_theta, intensity = calculate_pattern_vesta_exact(
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
        #print("DEBUG: Pattern calculated for:", cif_path)

        if first_two_theta is None:
            #print("DEBUG: Writing 2θ column")
            first_two_theta = two_theta
            wks.from_list(col_index, first_two_theta, lname='2Theta')
            col_index += 1

        #print("DEBUG: Writing intensity column for:", cif_path)
        sample_name = os.path.splitext(os.path.basename(cif_path))[0]
        wks.from_list(col_index, intensity, lname=sample_name)
        col_index += 1

    #print("DEBUG: Running LabTalk cleanup")
    wb.activate()
    wks.activate()
    op.lt_exec(LABTALK_CLEANUP)
    
    for uParam in ("Group Info","Method"):
        idx = wks._user_param_row(uParam,True) + 1
        op.lt_exec(f"wks.labels(#D{idx});")
        
    #print("DEBUG: LabTalk cleanup finished")

# ----------------------------------------------------------------------
#  DISPATCHER (LABTALK ARGUMENTS)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Read the LabTalk variable fname$
    raw_list = op.get_lt_str('fname$')

    if raw_list:
        # Normalize Windows newlines and split into lines
        file_list = [
            f.strip()
            for f in raw_list.replace("\r\n", "\n").split("\n")
            if f.strip()
        ]

        # Read wavelength mode from LabTalk argument
        wavelength_mode = sys.argv[1] if len(sys.argv) > 1 else "CuKa"

        import_cif_files(file_list, wavelength_mode)


