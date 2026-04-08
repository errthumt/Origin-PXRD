# Origin-PXRD
A plugin for importing experimental patterns and calculating theoretical patterns for PXRD in OriginLab's OriginPro software.

This plugin is primarily used by Kovnir and Zaikina research groups at Iowa State University, Department of Chemistry

**Have a bug to report or feature to request? Use one of the links below (for Github accounts only) or [use this form](https://forms.office.com/r/9bfw1zLiDh)**
* [Create a bug report](https://github.com/errthumt/Origin-PXRD/issues/new?template=bug_report.yml)
* [Request a feature](https://github.com/errthumt/Origin-PXRD/issues/new?template=feature_request.yml)
* [Other feedback](https://github.com/errthumt/Origin-PXRD/issues/new)

# Installation Instructions

## Automatic Install (Origin 2025 or later):
1. Download and run [the most recent installer](installer/release). It will open the installation project inside Origin.
2. In the pop up menus, select which plugin features you want to install.
3. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.
4. After the python packages have been installed (CMD line should end with "Press any key to continue..."), save the Origin project (It will be deleted shortly, but Origin will not release it for deletion until it's saved.) and close all copies of Origin.
5. If using the automatic installer, a CMD window should appear that will clean up the installation files from their temporary directory. **Do not close this window, it will close itself after cleaning up**
5. Review the instructions for use below for further guidance.

## Manual Install (Origin 2022-2024)
**Disclaimer:** This plugin should work as far back as Origin 2022. However, it has only been tested for 2024 or later. 
1. Locate your Origin User Files Folder.
   * In Origin 2024 or later, your user files folder can be found from inside Origin: Help > Open Folder > User Files Folder
2. Download [the most recent zip release](manual_install) and extract it to an easy-to-find location
3. For each option that you want to install, copy the entire contents of the corresponding option folder into the user files folder.
    * For example: If you want to install the PXRD Menu, open the PXRD Menu folder and copy cifImp.py, cifPicker.py, PXRD.omc, etc... directly into the user file folder
    * Some option folders contain additional folders inside them. The folder itself needs to be put inside the user files folder, then the files inside stay inside that folder. If the folder already exists in the user files folder, make sure the new files are inside that folder after copying.
      - Example: The In-Situ Beamline option has a folder inside called Filters. This matches the Filters folder inside the User Files Folder. The *.oif files in that folder need to end up inside User Files/Filters/.
4. In Origin, open the script window with: Window > Script Window
5. Copy/Paste the ENTIRE command below as one line into the script window:
    ```
    pip -chk numpy bibtexparser matplotlib monty narwhals orjson palettable pandas plotly pymatgen requests scipy spglib sympy tabulate tqdm uncertainties
    ```
7. Ensure that your text cursor is at the end of the pasted line (not on a new line) and press \<Enter\>
8. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.
9. After the python packages have been installed (CMD line should end with "Press any key to continue..."), close restart Origin with a fresh project.
10. Review the instructions for use below for further guidance.

# Instructions for Use
**Please Note:** If you opted to install Graph Templates without the PXRD Menu, refer to the Graph Templates section below. Some options (like In-Situ processing) are available to install independently, but require you to execute commands through the script window instead of the menu.

**After installing the plugin (with PXRD Menu) and restarting Origin, a new dropdown should appear on the top banner titled 'PXRD'**

## If "PXRD" dropdown does not appear:
1. Select Preferences > Custom Menu Organizer
2. Verify that there is an entry titled "PXRD"
3. If the entry is not there, inside the menu organizer, select File > Open... and search for PXRD.omc in the User Files Folder
4. Close the menu organizer and look for the dropdown

### If "PXRD" dropdown STILL does not appear:
You may need to switch GUI mode.

<ins>**Origin 2025b:**</ins> Preferences > GUI Mode > PXRD

<ins>**Origin 2024–2025:**</ins> Preferences > Menu > PXRD

## PXRD MENU OPTIONS:
<ins>**Import RAS Files:**</ins> Rigaku powder patterns can be imported directly from .RAS files without converting using PowDLL. Each import command creates a new workbook in Origin. All patterns normalized to [0,1].

<ins>**Calculate CIF Patterns:**</ins> Calculated patterns can be brought directly into origin from .CIF files. Each import command creates a new workbook in origin. All patterns normalized to [0,1]

* <ins>**Cu-Ka (3-90deg):**</ins> Calculates powder patterns for 3–90° 2θ using default Cu‑Ka doublet splitting. Step size = 0.01°.

* <ins>**Custom Parameters:**</ins> After selecting CIF files, opens a window to specify (similar to VESTA's options, but with further tunability):
  - Number of fE wavelengths
  - Wavelengths and relative intensities
  - 2θ ranges
  - Step Size
  - ADVANCED PARAMETERS: U, V, W, X, Y, and Axial S
  - Other presets: Additional presets can be added easily. Reach out to Travis if there is an import setting that you anticipate using frequently. It will be added to the next installer version.
---
  ### When importing RAS or CIF files:
  - <ins>**Select Files:**</ins> Opens a window to add/remove desired files. After all files have been added to the window, select "Import" or "OK" to proceed

  - <ins>**Select Folder:**</ins> Opens a window to select a folder containing all desired files. Origin will import every file in the selected folder that matches the intended filetype.
---
<ins>**Transform Columns:**</ins> These options only appear when a worksheet is open in Origin
* <ins>**Add Q Columns:**</ins> Detects any column in the current worksheet with "deg" as units. Prompts the user for wavelength, then adds a new column in Q space next to each column.
* <ins>**Rescale Columns:**</ins> Adds a new column next to each applicable column (see selection methods below) with a new row titled "ScaleFactor". Data from the original column is multiplied by the scale factor in the new column. Scale factors can be adjusted and columns will auto-update.
* <ins>**Square Columns:**</ins> Adds a new column next to each applicable column (see selection methods below) that squares the values in the original column.
* <ins>**Sqrt Columns:**</ins> Adds a new column next to each applicable column (see selection methods below) that takes the square root of values in the original column.
---
  ### Selection Methods for Rescale, Square, and Sqrt Transformations:
  - <ins>**All "AU":**</ins> Adds the new column for every column in the current worksheet with "AU" in the Units row.

  - <ins>**Select Columns:**</ins> Opens a new window to select desired columns. Multiple rows can be highlighted using \<Ctrl\>-\<Click\> or \<Shift\>-\<Click\>
---
## Graph Templates
Installed graph templates can be found in Plot > User Templates
* <ins>**Stacked PXRD:**</ins> Each plot is offset by one unit. Good for displaying multiple normalized patterns.
* <ins>**Sample+Refs:**</ins> The first added plots are displayed as full-sized patterns on the top portion. Additional patterns can be added to the "Reference Patterns" layer to be displayed below at 1/2 scale.
