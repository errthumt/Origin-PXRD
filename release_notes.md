---
title: Release Notes
nav_order: 3
---

# Release Notes
## Release 1.3.4

Installer: [OriginPXRD_Installer_v1.3.4-69-g1cd7b7b.exe](./installer/release/OriginPXRD_Installer_v1.3.4-69-g1cd7b7b.exe)
Zip Package: [OriginPXRD_v1.3.4-69-g1cd7b7b.zip](./manual_install/OriginPXRD_v1.3.4-69-g1cd7b7b.zip)
<!--end release link-->


Minor Bugfixes, improvements to phase fraction analysis

* Phase Fraction analysis now allows you to [choose your fraction type.](./phase_frac.md#choosing-your-phase-fraction)
* Fixed the 11-ID-C theme to use a much smaller step size for 2$\theta$
* Fixed RAS imports so that the workbook name is not all lowercase.
* Rearranged some label rows for a more legible worksheet after imports.

## Release 1.3.3

Installer: [OriginPXRD_Installer_v1.3.3-6-ge33aeb8.exe](./installer/release/OriginPXRD_Installer_v1.3.3-6-ge33aeb8.exe)
Zip Package: [OriginPXRD_v1.3.3-6-ge33aeb8.zip](./manual_install/OriginPXRD_v1.3.3-6-ge33aeb8.zip)
<!--end release link-->
Furnace Calibrations, Copy/Pasting Annealing Diagrams

* Added calibration calculations to the annealing template. Input a saved furnace ID, and the template will automatically calculate furnace set temperatures to match your annealing profile
* Added a workflow to edit or add new furnace calibrations. User-saved calibrations will always take precedent over calibrations installed with the plugin.
* Within the furnace editing workflow, a 2nd sheet has also been added which generates a printable report of the trendline, calibration data, and calibration date.
* Annealing Diagrams are now inserted into a new cell in the template workbook so that they can be copy/pasted. They can also be saved as a PNG in the dialog. If no save location is selected, they are saved to a temporary location in the user files folder.

## Release 1.3.2

Installer: [OriginPXRD_Installer_v1.3.2.exe](./installer/release/OriginPXRD_Installer_v1.3.2.exe)
Zip Package: [OriginPXRD_v1.3.2.zip](./manual_install/OriginPXRD_v1.3.2.zip)
<!--end release link-->
Improved workflow for installation

* Installation now uses a single menu with checkboxes for options, instead of individual popups.
* Steamlined backend development.

## Release 1.3.1

Installer: [OriginPXRD_Installer_v1.3.1-2-g8df0677.exe](./installer/release/OriginPXRD_Installer_v1.3.1-2-g8df0677.exe)
Zip Package: [OriginPXRD_v1.3.1-2-g8df0677.zip](./manual_install/OriginPXRD_v1.3.1-2-g8df0677.zip)
<!--end release link-->
UI tweaks, annealing profiles

* Added version checking so that users are notified when a new version is available.
* Added tooltips back to PXRD menu
* Added new [Annealing Profiles Dropdown](./instructions.md#new-annealing-profiles-dropdown).

## Release 1.3.0

Installer: [OriginPXRD_Installer_v1.3.0-1-hotfix.exe](./installer/release/OriginPXRD_Installer_v1.3.0-1-hotfix.exe)
Zip Package: [OriginPXRD_v1.3.0-1-hotfix.zip](./manual_install/OriginPXRD_v1.3.0-1-hotfix.zip)
<!--end release link-->
Feature Requests, bugfixes, UI overhaul (I finally learned to code in C)

This release contains features that are difficult to test without a fresh install of Origin. If you are able to use the full import dialog after installing, give Travis the good news!

* **All import commands have been moved into an official X-Function dialog.** *This also allows users to create and save their own import settings using Origin's native themes functionality!*
* New [in-depth installation guide](./install_guide/) with screenshots.
* Updated file selection dialogs to start in folder containing current saved project.
* Updated CIF workflow to prevent errors when cancelling out of menus.
* (Feature Request: David) Changed default CuKa step size to 0.02
* Column selections for transformations are now done using Origin's native column selection instead of a UI.
* Q-Space columns now allow for column selection.
* Added CIF import preset for 11-ID-C March 2026
* (Feature Request: Kirill) \[BETA] Added [phase fraction analysis option](./instructions.md#beta-phase-fraction-analysis) for CIF imports.
* <ins>**Hotfix 1:**</ins> Improved phase fractions for more "realistic" relative intensities.

## Release 1.2.5

Installer: [OriginPXRD_Installer_v1.2.5.exe](./installer/release/OriginPXRD_Installer_v1.2.5.exe)
Zip Package: [OriginPXRD_v1.2.5.zip](./manual_install/OriginPXRD_v1.2.5.zip)
<!--end release link-->
The first public GitHub release.
* Improved file selection workflow to use Origin's native selection tools instead of custom tkinter window
* Added install option for processing In-Situ Beamtime data. Currently only compatible with temperature metadata (no flow options yet). Go to PXRD > In-Situ Processing
  * 11-ID-C (March 2026): Normalizes all patterns (normalized by data set, not by individual pattern) and extracts temperature from all metadata files. Adds temperature as a "Temp" row at the top.
* Added In-Situ Contour graph template. Configured to expect [0,1\] normalization and temperatures in "Temp" row. Reach out to Travis for help using this template.
* Added In-Situ Browser graph template. Useful for scrolling through many powder patterns at once.
