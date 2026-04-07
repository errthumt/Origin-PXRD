!define APPNAME "Origin PXRD Tools"
!define COMPANY "Kovnir Group - Iowa State Dept of Chemistry"
!define VERSION "1.2.1-2-g8c001ab"

; -----------------------------
; Version metadata (fixes "Name")
; -----------------------------
Name "${APPNAME} 1.2.1-2-g8c001ab"
OutFile "release\OriginPXRDInstaller_1.2.1-2-g8c001ab.exe"

VIProductVersion "1.2.1.2"
VIFileVersion    "1.2.1.2"

VIAddVersionKey "ProductName"        "${APPNAME}"
VIAddVersionKey "FileDescription"    "${APPNAME} Installer"
VIAddVersionKey "CompanyName"        "${COMPANY}"
VIAddVersionKey "LegalCopyright"     "© ${COMPANY}"
VIAddVersionKey "ProductVersion"     "1.2.1-2-g8c001ab"
VIAddVersionKey "FileVersion"        "1.2.1-2-g8c001ab"
VIAddVersionKey "InternalName"       "${APPNAME}"
VIAddVersionKey "OriginalFilename"   "OriginPXRDInstaller_1.2.1-2-g8c001ab.exe"

RequestExecutionLevel user
SetCompressor /SOLID lzma

; -----------------------------
; Minimal UI: only InstFiles page
; -----------------------------
Page instfiles

Var TempDir

Section "Install"

    ; Create a unique temp directory
    StrCpy $TempDir "$TEMP\OriginPXRD_1.2.1-2-g8c001ab"
    CreateDirectory "$TempDir"

    ; Extract build folder contents into temp dir
    SetOutPath "$TempDir"
    File /r "..\build\*.*"

    ; Launch OPJU using Windows file association
    Exec 'cmd.exe /c start "" "$TempDir\install_project.opju"'

SectionEnd