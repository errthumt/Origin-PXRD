# Full Installation Guide (with screenshots)

## Before Installing:
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

* Other Windows to Recognize

| Labtalk Script Window | CMD Window |
| :---------------------------: | :-----------------------------: |
| This window is used to run Origin Labtalk commands.<br>It is also used during manual installation to manually request python packages. | This window will be opened by Origin to install any requested python packages |
| ![labtalk window](/install_guide/images/labtalk.png) | ![cmd window](/install_guide/images/cmd.png) |
