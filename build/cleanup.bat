@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo setting target:
set "TARGET=%~1"
echo %TARGET%

echo WARNING: Origin PXRD - Cleaning up installation files. Please leave this window open.
timeout /t 10 >nul

:retry
echo Attempting cleanup of "%TARGET%"...
rmdir /s /q "%TARGET%" 2>nul

if exist "%TARGET%" (
    echo.
    echo Cleanup could not complete because the installer or Origin are still running.
    echo Please save your work, close the installer, and end all Origin processes in task manager.
    echo Then press any key to retry cleanup.
    pause >nul
    goto retry
) else (
    echo.
    echo Cleanup successful.
    del "%~f0"
)