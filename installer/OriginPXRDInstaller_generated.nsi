!define APPNAME "Origin PXRD Tools"
!define COMPANY "Kovnir Group - Iowa State Dept of Chemistry"
!define VERSION "1.3.5-26-gad3017e"

; -----------------------------
; Version metadata (fixes "Name")
; -----------------------------
Name "${APPNAME} 1.3.5-26-gad3017e"
OutFile "release\OriginPXRD_Installer_v1.3.5-26-gad3017e.exe"

VIProductVersion "1.3.5.26"
VIFileVersion    "1.3.5.26"

VIAddVersionKey "ProductName"        "${APPNAME}"
VIAddVersionKey "FileDescription"    "${APPNAME} Installer"
VIAddVersionKey "CompanyName"        "${COMPANY}"
VIAddVersionKey "LegalCopyright"     "© ${COMPANY}"
VIAddVersionKey "ProductVersion"     "1.3.5-26-gad3017e"
VIAddVersionKey "FileVersion"        "1.3.5-26-gad3017e"
VIAddVersionKey "InternalName"       "${APPNAME}"
VIAddVersionKey "OriginalFilename"   "OriginPXRD_Installer_v1.3.5-26-gad3017e.exe"

RequestExecutionLevel user
SetCompressor /SOLID lzma

; -----------------------------
; Minimal UI: only InstFiles page
; -----------------------------
Page instfiles

Var TempDir

Section "Install"

    ; Create a unique temp directory
    StrCpy $TempDir "$TEMP\OriginPXRD_1.3.5-26-gad3017e"
    CreateDirectory "$TempDir"

    ; Extract build folder contents into temp dir
    SetOutPath "$TempDir"
    File /r "..\build\*.*"

    ; Launch OPJU using Windows file association
    Exec 'cmd.exe /c start "" "$TempDir\install_project.opju"'

SectionEnd