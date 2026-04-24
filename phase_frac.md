# Phase Fraction Analysis: Scaling calculated patterns by molar ratio to match experimental intensities

The end goal of this part of the plugin is to give presenters an easy way to generate theoretical data that can be visually compared to experimental data. When comparing experimental peaks to theoretical peaks for identified phases, it is useful to be able to compare relative intensities with identified phase fractions to verify that the experimental peaks are fully accounted for by the identified phases.

Unfortunately, the previously established method (in our research group) for generating theoretical patterns through VESTA results in an arbitrarily normalized pattern with intensities that cannot be compared with other calculated patterns.

There is, however, an already-established algorithm for scaling intensities by phase fractions which is used by Reitveld refinement technique to simulate multi-phase patterns. Since the calculation method for importing CIFs using the plugin already approximates the Rietveld method, then it is simply a matter of "pre-baking" any other phase-dependent factors into the calculated patterns, such that all there is left to do is multiply by phase fraction.

## Source Code
For reference, the main calculation module is in the `calculate pattern()` module in [PXRD_cifImp.py](/build/option_files/PXRD%20Menu/PXRD_cifImp.py):
<details>
  <summary>Click to expand code</summary>

```python
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
```
</details>

## Approximation of peak shapes and intensities with the Rietveld model

The classical Rietveld method of calculating diffraction intensity for a given sample is:

$$
I_{calc}(\theta) = S_F \sum_{k}^{phases}\left[\frac{\phi_k}{V_k^2}\sum_{j}^{peaks}\left(L_k\left|F_{k,j}\right|^2S_j\left(2\theta-2\theta_{k,j}\right)P_{k,j}A_{j}\right)\right] + bkg
$$

### Reflection Intensities

First, we focus on the peak-scaled intensities outlined in the expression:

$$
\sum_{j}^{peaks}\left(L_k\left|F_{k,j}\right|^2 S_j\left(2\theta-2\theta_{k,j}\right)P_{k,j}A_{j}\right)
$$

Where:
* $L_k$ is the Lorentz-Polarization factor
* $\left|F_{k,j}\right|^2$ is the structure factor
* $S_j\left(2\theta-2\theta_{k,j}\right)$ is the shape function for a peak centered at $2\theta_{k,j}$.
* $P_{k,j}$ is the March-Dollase factor for preferred orientation
* $A_{j}$ is an absorption factor.

In the python code, the base peak intensities are generated by making use of pymatgen's `XRDCalculator.get_pattern()` method:
```python
xrd = XRDCalculator(wavelength=wl)
pattern = xrd.get_pattern(structure, two_theta_range=two_theta_range, scaled=False)
```
This generates a set of sharp peak intensities (`pattern = ` $I_{peak}$) that account for Lorentz-Polarization and structure factor *only*:

$$
I_{peak} = L_k\left|F_{k,j}\right|^2
$$

Since these patterns are generated for visualization, not refinement, we also choose to neglect preferred orientation and absorption effects:

$$
\sum_{j}^{peaks}\left(L_k\left|F_{k,j}\right|^2 S_j\left(2\theta-2\theta_{k,j}\right)P_{k,j}A_{j}\right) \approx \sum_{j}^{peaks}\left(L_k\left|F_{k,j}\right|^2 S_j\left(2\theta-2\theta_{k,j}\right)\right) = \sum_{j}^{peaks}\left(I_{peak}S_j\left(2\theta-2\theta_{k,j}\right)\right)
$$

### Peak Shapes and Broadening

Now we must apply the shape function, $S_j\left(2\theta-2\theta_{k,j}\right)$, which converts theoretical peak intensities into realistically-broadened peak shapes. In this plugin, I opted for construct the peak function as a combination of:
* Debye-Waller Peak Dampening
* Caglioti/Pseudo-Voight Peak Broadening (Hybrid of Gaussian and Lorentzian peak shape)
* Finger-Cox-Jephcoat axial divergence asymmetry for peak tailing

In the python code, the output data starts as an empty data set:
```python
two_theta = np.arange(tmin, tmax + step, step)
intensity = np.zeros_like(two_theta)
```

Then, it loops through every peak intensity in `pattern`:
```python
for idx, (t0, I0) in enumerate(zip(pattern.x, pattern.y)):
```

For each peak intensity, it first multiplies intensity by a Debye-Waller dampening factor averaged from all atoms in the structure:
```python
sin_th = np.sin(theta)
s = sin_th / wl # wl = wavelength
pi2 = np.pi**2
DW_atoms = np.mean([np.exp(-2 * pi2 * B * s**2) for B in atom_B])
I0 *= DW_atoms
```

Next, it generates ($2\theta$, Intensity) peak shape data sets for each individual peak:
```python
H_G = np.sqrt(U*np.tan(theta)**2 + V*np.tan(theta) + W)
H_L = X*np.tan(theta) + Y/np.cos(theta)

pv = tch_pseudo_voigt(two_theta, t0, H_G, H_L)
asym = fcj_asymmetry(two_theta, t0, H_G, S=axial_S)
```

Before finally multiplying the peak shapes by the dampened intensity and adding each peak to the intially empty data set:
```python
intensity += wt * I0 * pv * asym
#wt refers to the relative weight of the current wavelength (for doublet splitting)
```

This generates a full diffraction pattern that approximates a single phase *per unit cell* without relative scaling (`two_theta, intensity = `&nbsp;$I_{k}\left(\theta\right)$).

$$
I_{k}\left(\theta\right) = \sum_{j}^{peaks}\left(I_{peak}S_j\left(2\theta-2\theta_{k,j}\right)\right)
$$

### Scaling by Molar Phase Fraction

Now, we only have to figure out what factor to multiply each phase pattern by in order for it to be imported on a molar basis. Substituting our calculations and approximations so far back into our Rietveld model, we get:

$$
I_{calc}(\theta) = S_F \sum_{k}^{phases}\left[\frac{\phi_k}{V_k^2}I_{k}\left(\theta\right)\right] + bkg
$$

For theoretical patterns, we can neglect background. Also, since we will be normalizing our phases after relative scaling, we can also set $S_F = 1$:

$$
I_{calc}(\theta) =\sum_{k}^{phases}\left[\frac{\phi_k}{V_k^2}I_{k}\left(\theta\right)\right]
$$

Now, the scale factor $\frac{\phi_k}{V_k^2}$ is what we must account for, where:
* $\phi_k$ is the phase *volume* fraction.
* $V_k$ is the phase unit cell volume.

If we express volume fraction as a function of a molar phase fraction by formula unit, $x_k$:

$$
\phi_k \propto x_k \frac{V_k}{Z_k}
$$

Substituting back in, we get:

$$
I_{calc}(\theta)\propto\sum_{k}^{phases}\left[\frac{x_k}{Z_k V_k}I_{k}\left(\theta\right)\right]
$$

Since we will be normalizing, maintaining proportionality is sufficient. We will also be multiplying by $x_k$ *after* import to allow for dynamically changing phase fractions, so we should isolate that from our imported pattern:

$$I_{calc}(\theta)\propto\sum_{k}^{phases}\left[x_k I_{k,imported}(\theta)\right]$$
$$I_{k,imported}(\theta) = \frac{I_{k}\left(\theta\right)}{Z_k V_k}$$

To modify our calculated $I_k$ patterns into $I_{k,imported}$, we only need to divide our peak intensities by $Z_k$ and $V_k$ before adding them to our data set.
```python
I0 /= Z
I0 /= cell_volume

'''
Peak shape functions pv and asym defined here
'''

intensity += wt * I0 * pv * asym
```
