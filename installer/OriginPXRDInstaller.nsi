OutFile "OriginPXRDInstaller.exe"
RequestExecutionLevel user
SilentInstall normal
Caption "Origin PXRD Installer"

Var TempDir

Page instfiles InstFilesShow
Page finish

Section "Install"

    StrCpy $TempDir "$TEMP\OriginPXRD_$R0"
    CreateDirectory "$TempDir"

    SetOutPath "$TempDir"
    File /r "..\build\*.*"

    Exec 'cmd.exe /c start "" "$TempDir\install_project.opju"'

SectionEnd

Function InstFilesShow
    ; Change window title
    SendMessage $HWNDPARENT ${WM_SETTEXT} 0 "STR:Origin PXRD Installer"

    ; Change bottom-left branding text
    SetBrandingText "Installing Origin PXRD…"

    ; Change header text (control ID 1037)
    GetDlgItem $0 $HWNDPARENT 1037
    SendMessage $0 ${WM_SETTEXT} 0 "STR:Installing PXRD Tools"

    ; Change subheader text (control ID 1038)
    GetDlgItem $1 $HWNDPARENT 1038
    SendMessage $1 ${WM_SETTEXT} 0 "STR:Origin will launch automatically. After it loads, click Finish to clean up temporary files."
FunctionEnd

Function .onInstSuccess
    RMDir /r "$TempDir"
FunctionEnd