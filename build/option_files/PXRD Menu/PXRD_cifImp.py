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
from pymatgen.core.periodic_table import Element #type: ignore
from pymatgen.analysis.diffraction.xrd import XRDCalculator #type: ignore

import numpy as np
from pymatgen.core import Element #type: ignore

try:
    import xraydb  #type: ignore
except ImportError:
    xraydb = None


NA = 6.02214076e23  # mol^-1
ANG3_TO_CM3 = 1e-24
HC_KEV_ANG = 12.398419843320026  # keV·Å


def _mu_over_rho_element(z, energy_kev):
    """
    Mass attenuation coefficient μ/ρ for a single element (cm^2/g).

    Replace this with your own tabulated lookup if you don't want xraydb.
    """
    if xraydb is None:
        raise RuntimeError("xraydb is required for μ/ρ lookup or replace _mu_over_rho_element.")
    # Elam data, energy in keV
    return xraydb.mu_elam(z, energy_kev)


def _density_from_structure(structure):
    """
    Compute bulk density from the crystallographic structure (g/cm^3).

    Uses the composition per unit cell and the cell volume.
    """
    comp = structure.composition
    # mass per mole of "one unit cell composition"
    molar_mass = comp.weight  # g/mol
    # mass per cell
    mass_cell_g = molar_mass / NA
    # volume in cm^3
    vol_cm3 = structure.lattice.volume * ANG3_TO_CM3
    return mass_cell_g / vol_cm3


def _mu_linear_mixture(structure, wavelength):
    """
    Linear attenuation coefficient μ for the phase (cm^-1) at given wavelength (Å).

    Uses mass-fraction mixing of μ/ρ for each element.
    """
    energy_kev = HC_KEV_ANG / wavelength

    comp = structure.composition
    elements = list(comp.elements)

    # atomic masses and counts per cell
    masses = {el: float(el.atomic_mass) for el in elements}
    counts = {el: comp[el] for el in elements}

    total_mass = sum(counts[el] * masses[el] for el in elements)
    # mass fractions
    mass_fracs = {el: counts[el] * masses[el] / total_mass for el in elements}

    # mixture μ/ρ (cm^2/g)
    mu_over_rho_mix = 0.0
    for el in elements:
        w_i = mass_fracs[el]
        mu_rho_i = _mu_over_rho_element(el.Z, energy_kev)  # cm^2/g
        mu_over_rho_mix += w_i * mu_rho_i

    # density (g/cm^3)
    rho = _density_from_structure(structure)

    # linear attenuation μ (cm^-1)
    return mu_over_rho_mix * rho


def get_mu_phase(structure, wavelength, two_theta, thickness_cm=0.001):
    """
    Return an absorption correction factor A(θ, λ) for the phase.

    Parameters
    ----------
    structure : pymatgen Structure
    wavelength : float
        Wavelength in Å.
    two_theta : float
        2θ in degrees for the reflection.
    thickness_cm : float, optional
        Effective sample thickness in cm (flat plate, reflection geometry).

    Returns
    -------
    A : float
        Dimensionless absorption factor to multiply I0.
    """
    mu = _mu_linear_mixture(structure, wavelength)  # cm^-1

    theta = np.radians(two_theta / 2.0)
    # effective path length factor for symmetric reflection: in + out
    x = 2.0 * mu * thickness_cm / np.sin(theta)

    # Flat-plate absorption factor:
    # A = (1 - exp(-x)) / x
    # well-behaved for small x
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        A = (1.0 - np.exp(-x)) / np.where(x == 0.0, 1.0, x)

    return float(A)



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

def compute_Z(structure):
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
        Z = compute_Z(structure)
        mu = absorption_proxy(structure) # This is very fudgy
        # Modify reflections with scattering factors
        for idx, (t0, I0) in enumerate(zip(pattern.x, pattern.y)):
            # Useful constants
            theta = np.radians(t0 / 2)
            sin_th = np.sin(theta)
            cos_th = np.cos(theta)

            # Get atoms
            atoms = structure.sites
                
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
            I0 *= DW_atoms #* DW_extra
            I0 *= 1.0/Z
            
            #A_abs = get_mu_phase(structure, wl, t0)
            #I0 *= A_abs


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


