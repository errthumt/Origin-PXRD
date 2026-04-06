# Origin-PXRD
A plugin for importing experimental patterns and calculating theoretical patterns for PXRD in OriginLab's OriginPro software.

This plugin is primarily used by Kovnir and Zaikina research groups at Iowa State University, Department of Chemistry

# Installation Instructions

## Automatic Install (Origin 2025 or later):
1. Download and run the most recent installer. It will open the installation project inside Origin.
2. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.
3. After the python packages have been installed (CMD line should end with "Press any key to continue..."), restart Origin with a fresh project.
4. Review the instructions for use below for further guidance.

## Manual Install (Origin 2022-2024)
Disclaimer: Thie plugin should work as far back as Origin 2022. However, it has only been tested for 2024 or later.
1. Locate your Origin User Files Folder.
   * In Origin 2024 or later, your user files folder can be found from inside Origin: Help > Open Folder > User Files Folder
2. Download all files found on the Manual Install Page
3. Copy the desired files from each folder into their specified location:
  PLACEHOLDER TEXT
4. In Origin, open the script window with: Window > Script Window
5. Copy/Paste the ENTIRE command below as one line into the script window:
    ```
    pip -chk numpy bibtexparser matplotlib monty narwhals orjson palettable pandas plotly pymatgen requests scipy spglib sympy tabulate tqdm uncertainties
    ```
7. Ensure that your text cursor is at the end of the pasted line (not on a new line) and press \<Enter\>
8. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.
9. After the python packages have been installed (CMD line should end with "Press any key to continue..."), restart Origin with a fresh project.
10. Review the instructions for use below for further guidance.

# Instructions for Use
## After installing the plugin and restarting Origin, a new dropdown should appear on the top banner titled 'PXRD'
## If "PXRD" dropdown does not appear:
1. Select Preferences > Custom Menu Organizer
2. Verify that there is an entry titled "PXRD"
3. If the entry is not there, inside the menu organizer, select File > Open... and search for PXRD.omc in the User Files Folder
4. Close the menu organizer and look for the dropdown

### If "PXRD" dropwdown STILL does not appear:
You may need to switch GUI mode.

**Origin 2025b:** Preferences > GUI Mode > PXRD

**Origin 2024–2025:** Preferences > Menu > PXRD

## PXRD MENU OPTIONS:
**Import RAS Files:** Rigaku powder patterns can be imported directly from .RAS files without converting using PowDLL. Each import command creates a new workbook in Origin. All patterns normalized to [0,1].

**Calculate CIF Patterns:** Calculated patterns can be brought directly into origin from .CIF files. Each import command creates a new workbook in origin. All patterns normalized to [0,1]

* Cu-Ka (3-90deg): Calculates powder patterns for 3–90° 2θ using default Cu‑Ka doublet splitting. Step size = 0.01°.

* Custom Parameters: After selecting CIF files, opens a window to specify (similar to VESTA's options, but with further tunability):
  - Number of fE wavelengths
  - Wavelengths and relative intensities
  - 2θ ranges
  - Step Size
  - ADVANCED PARAMETERS: U, V, W, X, Y, and Axial S
  - Other presets: Additional presets can be added easily. Reach out to Travis if there is an import setting that you anticipate using frequently. It will be added to the next installer version.

When importing RAS or CIF files:

**Select Files:** Opens a window to add/remove desired files. After all files have been added to the window, select "Import" or "OK" to proceed

**Select Folder:** Opens a window to select a folder containing all desired files. Origin will import every file in the selected folder that matches the intended filetype.

**Transform Columns:** These options only appear when a worksheet is open in Origin
* **Add Q Columns:** Detects any column in the current worksheet with "deg" as units. Prompts the user for wavelength, then adds a new column in Q space next to each column.
* **Rescale Columns:** Adds a new column next to each applicable column (see selection methods below) with a new row titled "ScaleFactor". Data from the original column is multiplied by the scale factor in the new column. Scale factors can be adjusted and columns will auto-update.
* **Square Columns:** Adds a new column next to each applicable column (see selection methods below) that squares the values in the original column.
* **Sqrt Columns:** Adds a new column next to each applicable column (see selection methods below) that takes the square root of values in the original column.

Selection Methods for Rescale, Square, and Sqrt Transformations:
All "AU": Adds the new column for every column in the current worksheet with "AU" in the Units row.
Select Columns: Opens a new window to select desired columns. Multiple rows can be highlighted using <Ctrl>-<Click> or <Shift>-<Click>

## Graph Templates
Installed graph templates can be found in Plot > User Templates
* **Stacked PXRD:** Each plot is offset by one unit. Good for displaying multiple normalized patterns.
* **Sample+Refs:** The first added plots are displayed as full-sized patterns on the top portion. Additional patterns can be added to the "Reference Patterns" layer to be displayed below at 1/2 scale.
