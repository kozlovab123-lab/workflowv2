@echo off
title LangflowV2
REM Launcher in project root — works from Explorer double-click (no Cursor).
cd /d "%~dp0"

echo ========================================
echo   LangflowV2 launcher
echo ========================================
echo Start:   %DATE% %TIME%
echo.

set "RUN_SCRIPT=%~dp0scripts\windows\run_workflowv2.bat"
if not exist "%RUN_SCRIPT%" (
    echo ERROR: Script not found:
    echo   %RUN_SCRIPT%
    echo.
    echo This .bat must stay in the workflowv2 project root folder
    echo   ...\workflowv2\LangflowV2-Start.bat
    echo.
    pause
    exit /b 1
)

call "%RUN_SCRIPT%"
set "EC=%ERRORLEVEL%"
if %EC% neq 0 (
    echo.
    echo Launcher finished with error code %EC%
    pause
)
exit /b %EC%
