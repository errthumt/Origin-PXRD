# Origin-PXRD
A plugin for importing experimental patterns and calculating theoretical patterns for PXRD in OriginLab's OriginPro software.

This plugin is primarily used by Kovnir and Zaikina research groups at Iowa State University, Department of Chemistry

## Jump to:
* [Automatic Install (Origin 2025 or later)](#automatic-install-origin-2025-or-later)
* [Manual Install (Origin 2022-2024)](#manual-install-origin-2022-2024)
* [Instructions for Use](#instructions-for-use)
* [Release Notes](#release-notes)

## Bug reports or Feature Requests
* <ins>**No GitHub Account?**</ins> [use this form](https://forms.office.com/r/9bfw1zLiDh)
* <ins>**If you have a GitHub account:**</ins>
  * [Create a bug report](https://github.com/errthumt/Origin-PXRD/issues/new?template=bug_report.md)
  * [Request a feature](https://github.com/errthumt/Origin-PXRD/issues/new?template=feature_request.md)
  * [Other feedback](https://github.com/errthumt/Origin-PXRD/issues/new)

---

# Installation Instructions
A full installation guide with screenshots can be found [here](/install_guide/install_guide.md). A PDF version can be found [here](/install_guide/install_guide.pdf)

## Automatic Install (Origin 2025 or later):
1. Download and run [the most recent installer](installer/release). It will open the installation project inside Origin.
2. In the pop up menus, select which plugin features you want to install.
3. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.
4. After the python packages have been installed (CMD line should end with "Press any key to continue..."), save the Origin project (It will be deleted shortly, but Origin will not release it for deletion until it's saved.) and close all copies of Origin.
5. If using the automatic installer, a CMD window should appear that will clean up the installation files from their temporary directory. **Do not close this window, it will close itself after cleaning up**
5. Review the [instructions for use](#instructions-for-use) for further guidance.

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
9. After the python packages have been installed (CMD line should end with "Press any key to continue..."), close and restart Origin with a fresh project.
10. Review the [instructions for use](#instructions-for-use) for further guidance.

---

# Instructions for Use
**Please Note:** If you opted to install Graph Templates without the PXRD Menu, they will work independently (See [Graph Templates](#graph-templates)). Some other options (like In-Situ processing) are available to install independently, but require you to execute commands through the script window if you did not install the menu.

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

---

## PXRD MENU OPTIONS:

<ins>**Import Patterns:**</ins> Import experimental patterns or calculate theoretical patterns from CIF files. 

* <ins>**Full Dialog...:**</ins> Opens the [custom dialog](#import-pattern-dialog-options) to edit parameters, or to save/load your own preset themes
* <ins>**\<Last Used\>**</ins> Without opening the dialog, executes the last used set of import settings. Re-prompts for file selection.
* <ins>**CIF Patterns (CuKa Defaults)**</ins> Without opening the dialog, imports with preset settings for Cu-Ka splitting (2θ 3-90°, step size 0.02°). Re-prompts for file selection.
* <ins>**CIF Patterns (11-ID-C March 2026)**</ins> Without opening the dialog, imports with preset settings to match 11-ID-C. 2θ range and step size are similar to in-situ values, and peak shape parameters were estimated by Rietveld analysis. Re-prompts for file selection.
* <ins>**Experimental Patterns (*.ras)**</ins> Without opening the dialog, imports with preset settings for experimental patterns from the Rigaku Miniflex. Re-prompts for file selection.

<ins>**Transform Columns:**</ins> These options only appear when a worksheet is open in Origin

  | | Selection Methods for Transformations |
  | ---: | :--- |
  | <ins>**All "AU" or All "deg":**</ins> | Adds the new column for every column in the current worksheet with matching units. |
  | <ins>**Select Columns:**</ins> | Adds the new column for each column selected in Origin. |

* <ins>**Add Q Columns:**</ins> Adds a new column in Q-Space next to each applicable column (see selection methods below). Q-Space is dynamically calculated using the value in the "Wavelength" row of the source column.
* <ins>**Rescale Columns:**</ins> Adds a new column next to each applicable column (see selection methods below) with a new row titled "ScaleFactor". Data from the original column is multiplied by the scale factor in the new column. Scale factors can be adjusted and columns will auto-update.
* <ins>**Square Columns:**</ins> Adds a new column next to each applicable column (see selection methods below) that squares the values in the original column.
* <ins>**Sqrt Columns:**</ins> Adds a new column next to each applicable column (see selection methods below) that takes the square root of values in the original column.

<ins>**In-Situ Processing:**</ins> Macros for processing metadata and importing patterns from in-situ beamtimes.

* <ins>**11-ID-C (March 2026):**</ins> Normalizes all patterns (normalized by data set, not by individual pattern) and extracts temperature from all metadata files. Adds temperature as a "Temp" row at the top.

---
## Import Pattern Dialog Options

<p align="center">
  <img src="/install_guide/images/import_dialog.png" width="40%">
</p>

If you have your own set of custom parameters that you like to use for your own analysis, you can save them as a theme using the menu on the top right of the dialog.

|Option | | Description |
| :--- | :--- | :--- |
| New Workbook Name | | Name your imported workbook. All import commands create a new workbook to simplify import and normalization.
| Import File Type | | Select whether you are importing experimental patterns (\*.ras) or calculating theoretical patterns (\*.cif) |
| Selection Type | | Select how you will be selecting your import files after clicking "OK"<br>**Select Files:** Select one or more individual files by selecting and adding them to the dialog.<br>**Select Folder:** Select a folder and import all matching files at once. |
| <ins>**CIF Calculation Parameters**</ins> | Only used for CIF Imports. |
| | Doublet Splitting? | Specify if you would like to simulate peak splitting as a result of 2 different incident wavelengths |
| | Primary Wavelength (Å)<br>Secondary Wavelength (Å) | X-Ray wavelengths. Secondary wavelength only used when Doublet Splitting is enabled. |
| | Weight | Relative weights of Primary and Secondary Wavelengths. Only used when Doublet Splitting is enabled. |
| | X-Axis | Specifies which X-Axis you would like to use.<br>**2θ**: Calculates intensity for the range of 2θ values specified.<br>**Q**: Calculates intensity for the Q range specified. 2θ column will still be generated for reference. |
| | 2θ Start (°) | Beginning of 2θ range. Auto-calculated in Q mode.
| | 2θ End (°) | End of 2θ range. Auto-calculated in Q mode.
| | 2θ Step Size (°) | Patterns will be calculated by incrementing 2θ _regardless of Q mode_. Q Mode can specify range in Q values, but the increment will still be in 2θ. |
| | Q Start (Å⁻¹) | Beginning of Q range. Not available in 2θ mode. |
| | Q End (Å⁻¹) | End of Q range. Not available in 2θ mode. |
| | Advanced Parameters | Used to adjust peak broadening and dampening. |
| Normalization Mode | | Specify whether to normalize imported or calculated patterns.<br>During CIF import, an extra option is available to add scaling for each imported CIF by the relative phase fractions in your analysis. See the Phase Fraction section below. |

### \[BETA] Phase Fraction Analysis
If you select this option under **Normalization Mode** during CIF import, the files will be imported as usual (without normalization), but additional columns will be added to scale phases by their relative fractions present in your analysis. Column types are specified by 'Norm Type' row:
- **Non-normal**: Original, non-normalized calculated patterns
- **Phase-scaled**: Scales original patterns by the value in the 'Phase Fraction' row. <ins>Edits to phase fractions will affect all columns except original</ins>
  - Convention dictates that phase fractions should add to 1, but this is not required.
- **Max=1**: Preserving relative phase fractions, normalizes all patterns so that the max intensity across all phases is 1.0.
- **Sum=1**: Preserving relative phase fractions, normalizes all patterns so that the max intensity is 1.0 when all phases are summed.
- **Normalized, All Phases**: Final column calculated as the sum of all phases, preserving relative phase fractions. This should match a normalized experimental pattern.

---

## Graph Templates
Installed graph templates can be found in Plot > User Templates
* <ins>**Stacked PXRD:**</ins> Each plot is offset by one unit. Good for displaying multiple normalized patterns.
* <ins>**Sample+Refs:**</ins> The first added plots are displayed as full-sized patterns on the top portion. Additional patterns can be added to the "Reference Patterns" layer to be displayed below at 1/2 scale.
* <ins>**In-Situ Contour:**</ins> Typical in-situ contour plot. Intended for data sets normalized to [0,1]. Can be constructed to use a parameter row (such as the "Temp" row generated during In-Situ import) as the y-axis.
* <ins>**In-Situ Browser**</ins> Puts all selected columns into a "browser" graph that allows you to scroll through many patterns. Select multiple rows on the left panel to overlay patterns.

---

# Release Notes
## Release 1.3.1
UI tweaks



## Release 1.3.0
Feature Requests, bugfixes, UI overhaul (I finally learned to code in C)

This release contains features that are difficult to test without a fresh install of Origin. If you are able to use the full import dialog after installing, give Travis the good news!

* **All import commands have been moved into an official X-Function dialog.** *This also allows users to create and save their own import settings using Origin's native themes functionality!*
* New [in-depth installation guide](/install_guide/install_guide.md) with screenshots.
* Updated file selection dialogs to start in folder containing current saved project.
* Updated CIF workflow to prevent errors when cancelling out of menus.
* (Feature Request: David) Changed default CuKa step size to 0.02
* Column selections for transformations are now done using Origin's native column selection instead of a UI.
* Q-Space columns now allow for column selection.
* Added CIF import preset for 11-ID-C March 2026
* (Feature Request: Kirill) \[BETA] Added phase fraction analysis option for CIF imports.
* <ins>**Hotfix 1:**</ins> Improved phase fractions for more "realistic" relative intensities.
## Release 1.2.5
The first public GitHub release.
* Improved file selection workflow to use Origin's native selection tools instead of custom tkinter window
* Added install option for processing In-Situ Beamtime data. Currently only compatible with temperature metadata (no flow options yet). Go to PXRD > In-Situ Processing
  * 11-ID-C (March 2026): Normalizes all patterns (normalized by data set, not by individual pattern) and extracts temperature from all metadata files. Adds temperature as a "Temp" row at the top.
* Added In-Situ Contour graph template. Configured to expect [0,1] normalization and temperatures in "Temp" row. Reach out to Travis for help using this template.
* Added In-Situ Browser graph template. Useful for scrolling through many powder patterns at once.
