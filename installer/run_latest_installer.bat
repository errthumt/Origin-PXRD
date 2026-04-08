@echo off
setlocal enabledelayedexpansion

REM Folder where installers are created
set "RELEASE_DIR=%~dp0release"

REM Find newest .exe in the release folder
for /f "delims=" %%F in ('dir "%RELEASE_DIR%\*.exe" /b /a:-d /o:-d') do (
    set "LATEST=%%F"
    goto :found
)

echo No installer found in %RELEASE_DIR%
exit /b 1

:found
echo Launching newest installer: %LATEST%
start "" "%RELEASE_DIR%\%LATEST%"