@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ============================================
echo     Origin PXRD Plugin Installer Builder
echo ============================================
echo.

cd ..

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: This folder is not a Git repository.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('git describe --tags --always') do set CURRENT_VERSION=%%v

echo Current version: %CURRENT_VERSION%
echo.

set /p BUMP="Do you want to create a new version tag? (current: %CURRENT_VERSION%) (y/n): "

if /I "%BUMP%"=="y" (
    echo.
    set /p NEWTAG="Enter new version tag (example: v1.4.3): "

    set "NEWTAG=!NEWTAG: =!"

    if "!NEWTAG!"=="" (
        echo ERROR: No tag entered.
        pause
        exit /b 1
    )

    echo.
    echo Creating tag !NEWTAG!...
    git commit --allow-empty -m "Release bump"
    git tag !NEWTAG!
    git push origin !NEWTAG!

    echo.
    echo Tag !NEWTAG! created and pushed successfully.
    echo.

    set VERSION=!NEWTAG!
) else (
    echo Keeping existing version: %CURRENT_VERSION%
    echo.
    set VERSION=%CURRENT_VERSION%
)

set /p CONFIRM="Generate installer now? (y/n): "

if /I not "%CONFIRM%"=="y" (
    echo Installer generation cancelled.
    pause
    exit /b 0
)

echo.
echo Building NSIS installer...
echo.

set "ROOT=%cd%"
set "INSTALLER_DIR=%ROOT%\installer"
set "RELEASE_DIR=%INSTALLER_DIR%\release"

if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

pushd "%INSTALLER_DIR%"
makensis.exe /DVERSION=%VERSION% OriginPXRDInstaller.nsi
popd

move "%INSTALLER_DIR%\OriginPXRDInstaller.exe" "%RELEASE_DIR%\OriginPXRDInstaller_%VERSION%.exe" >nul

echo.
echo ============================================
echo   Installer built successfully:
echo   %RELEASE_DIR%\OriginPXRDInstaller_%VERSION%.exe
echo ============================================
echo.
pause
exit /b 0