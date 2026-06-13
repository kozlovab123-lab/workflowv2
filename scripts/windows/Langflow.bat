@echo off
title Langflow
setlocal

REM Prefer onedir layout (dist\Langflow\Langflow.exe), then legacy onefile (dist\Langflow.exe).
set "EXE="
if exist "%~dp0Langflow\Langflow.exe" set "EXE=%~dp0Langflow\Langflow.exe"
if exist "%~dp0Langflow.exe" if not defined EXE set "EXE=%~dp0Langflow.exe"

if not defined EXE (
    echo ERROR: Langflow.exe not found.
    echo Expected: %~dp0Langflow\Langflow.exe  or  %~dp0Langflow.exe
    pause
    exit /b 1
)

cd /d "%~dp0"

echo ========================================
echo   Langflow
echo ========================================
echo.
echo Executable: %EXE%
echo Browser:    http://127.0.0.1:7860
echo Boot log:   %USERPROFILE%\.langflow\langflow-exe-boot.log
echo Main log:   %USERPROFILE%\.langflow\langflow-exe.log
echo.
echo First start may take 1-3 minutes. Keep this window open.
echo.

"%EXE%" run

echo.
echo Langflow stopped. Exit code: %ERRORLEVEL%
echo Check logs in %USERPROFILE%\.langflow\ if the site did not open.
pause
