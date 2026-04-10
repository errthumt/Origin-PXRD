# Full Installation Guide (with screenshots)

# Before Installing:
* Identify your version of Origin.
    * Automatic install is confirmed for 2025 and 2026 releases.
    * Manual Install is required for 2022-2024 releases
    * This plugin is not compatible with Origin 2021 or earlier
* Make sure embedded python is installed.
    * Double check in Origin by navigating to Connectivity > Python Console...

        | Opening the python console | View from the python console |
        | :---------------------------: | :-----------------------------: |
        | ![opening the python console](/install_guide/images/open_python_console.png) | ![view from the python console](/install_guide/images/python_console.png) |

    * If necessary, add the embedded python to your installation by right-clicking in the start menu > Open File Location, and running the install repair tool to modify the installation

        | Find the install repair tool | Modify the installation |
        | :---------------------------: | :-----------------------------: |
        | ![Start Menu > Open File Location](/install_guide/images/open_file_location.png) | ![Modify Installation](/install_guide/images/modify_installation.png) |
        | ![Open repair tool](/install_guide/images/repair_tool.png) | ![Select Embedded Python](/install_guide/images/embedded_python.png) |

* Other Windows to Recognize:

    | Labtalk Script Window | CMD Window |
    | :---------------------------: | :-----------------------------: |
    | This window is used to run Origin Labtalk commands.<br>It is also used during manual installation to manually request python packages. | This window will be opened by Origin to install any requested python packages |
    | ![labtalk window](/install_guide/images/labtalk.png) | ![cmd window](/install_guide/images/cmd.png) |

# Installation Instructions

## Automatic Install (Origin 2025 or later):
1. Download and run [the most recent installer](/installer/release). It will open the installation project inside Origin.

    ![Recent Releases Page](/install_guide/images/release_page.png)

    ![Download installer](/install_guide/images/download_installer.png)
---
2. In the pop up menus, select which plugin features you want to install.

    ![option popup 1](/install_guide/images/popup1.png) ![option popup 2](/install_guide/images/popup2.png)
---
3. If prompted, install any requested python packages. Origin will open an embedded command prompt window to install necessary python packages. This may take longer than 10 minutes, depending on processing speed and internet connection.

    ![package install prompt](/install_guide/images/package_prompt.png)

    ![package installation window](/install_guide/images/package_install.png)

    * While waiting on package install, check on the Labtalk window for confirmation or error messages

        ![labtalk installation messages](/install_guide/images/labtalk_file_install.png)
---
4. After the python packages have been installed (CMD line should end with "Press any key to continue..."), save the Origin project (It will be deleted shortly, but Origin will not release it for deletion until it's saved.) and close all copies of Origin.
---
5. If using the automatic installer, a CMD window should appear that will clean up the installation files from their temporary directory. **Do not close this window, it will close itself after cleaning up**
    * The cleanup window may ask you to close all copies of Origin from task manager. This is because Origin keeps recent files open in the background and prevents their deletion, including some installation files.
        ![cleanup cmd window](/install_guide/images/cleanup_cmd.png)
---
5. Review the [instructions for use](/README.md#instructions-for-use) for further guidance.

## Manual Install (Origin 2022-2024)
**Disclaimer:** This plugin should work as far back as Origin 2022. However, it has only been tested for 2024 or later. 
1. Locate your Origin User Files Folder.
   * In Origin 2024 or later, your user files folder can be found from inside Origin: Help > Open Folder > User Files Folder
2. Download [the most recent zip release](/manual_install) and extract it to an easy-to-find location
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
10. Review the [instructions for use](/README.md#instructions-for-use) for further guidance.
