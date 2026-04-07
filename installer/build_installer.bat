@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ============================================
echo     Origin PXRD Plugin Installer Builder
echo ============================================
echo.

cd ..

:: Check if we are inside a git repo
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: This folder is not a Git repository.
    pause
    exit /b 1
)

:: Get current version from git describe
for /f "delims=" %%v in ('git describe --tags --always') do set CURRENT_VERSION=%%v

echo Current version: %CURRENT_VERSION%
echo.

:: Ask whether to bump version, showing current version inline
set /p BUMP="Do you want to create a new version tag? (current: %CURRENT_VERSION%) (y/n): "

if /I "%BUMP%"=="y" (
    echo.
    set /p NEWTAG="Enter new version tag (example: v1.4.3): "

    :: Trim spaces (prevents false 'empty' detection)
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
    if errorlevel 1 (
        echo ERROR: Failed to create tag.
        pause
        exit /b 1
    )

    echo Pushing tag to origin...
    git push origin !NEWTAG!
    if errorlevel 1 (
        echo ERROR: Failed to push tag.
        pause
        exit /b 1
    )

    echo.
    echo Tag !NEWTAG! created and pushed successfully.
    echo.
) else (
    echo Keeping existing version: %CURRENT_VERSION%
    echo.
)

:: Confirm installer generation
set /p CONFIRM="Generate installer now? (y/n): "

if /I not "%CONFIRM%"=="y" (
    echo Installer generation cancelled.
    pause
    exit /b 0
)

echo.
echo Running generate_installer.py...
echo.

python "installer/generate_installer.py"
if errorlevel 1 (
    echo ERROR: Installer generation failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo      Installer generation complete
echo ============================================
pause
exit