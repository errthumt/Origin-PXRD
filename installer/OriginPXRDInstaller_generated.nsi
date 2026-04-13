!define APPNAME "Origin PXRD Tools"
!define COMPANY "Kovnir Group - Iowa State Dept of Chemistry"
!define VERSION "1.3.0"

; -----------------------------
; Version metadata (fixes "Name")
; -----------------------------
Name "${APPNAME} 1.3.0"
OutFile "release\OriginPXRD_Installer_v1.3.0.exe"

VIProductVersion "1.3.0.0"
VIFileVersion    "1.3.0.0"

VIAddVersionKey "ProductName"        "${APPNAME}"
VIAddVersionKey "FileDescription"    "${APPNAME} Installer"
VIAddVersionKey "CompanyName"        "${COMPANY}"
VIAddVersionKey "LegalCopyright"     "© ${COMPANY}"
VIAddVersionKey "ProductVersion"     "1.3.0"
VIAddVersionKey "FileVersion"        "1.3.0"
VIAddVersionKey "InternalName"       "${APPNAME}"
VIAddVersionKey "OriginalFilename"   "OriginPXRD_Installer_v1.3.0.exe"

RequestExecutionLevel user
SetCompressor /SOLID lzma

; -----------------------------
; Minimal UI: only InstFiles page
; -----------------------------
Page instfiles

Var TempDir

Section "Install"

    ; Create a unique temp directory
    StrCpy $TempDir "$TEMP\OriginPXRD_1.3.0"
    CreateDirectory "$TempDir"

    ; Extract build folder contents into temp dir
    SetOutPath "$TempDir"
    File /r "..\build\*.*"

    ; Launch OPJU using Windows file association
    Exec 'cmd.exe /c start "" "$TempDir\install_project.opju"'

SectionEnd