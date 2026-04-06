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
    <p style="font-family: 'Courier New', monospace;">pip -chk numpy bibtexparser matplotlib monty narwhals orjson palettable pandas plotly pymatgen requests scipy spglib sympy tabulate tqdm uncertainties</p>
6. Ensure that your text cursor is at the end of the pasted line (not on a new line) and press <Enter>
7. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.
8. After the python packages have been installed (CMD line should end with "Press any key to continue..."), restart Origin with a fresh project.
9. Review the instructions for use below for further guidance.
