@echo off
title WorkflowV2
setlocal EnableExtensions

REM Project root = two levels up from scripts\windows
cd /d "%~dp0..\.."
if errorlevel 1 (
    echo ERROR: Cannot find project root from %~dp0
    pause
    exit /b 1
)
set "PROJECT_ROOT=%CD%"

echo ========================================
echo   WorkflowV2 (from source)
echo   Copy of langflow-work
echo ========================================
echo.
echo Start:   %DATE% %TIME%
echo Project: %PROJECT_ROOT%
echo Config:  %USERPROFILE%\.langflow\.env
echo Log:     %USERPROFILE%\.langflow\langflow.log
echo URL:     http://127.0.0.1:7860  (or port from banner below)
echo.
echo Keep this window open while WorkflowV2 is running.
echo.

REM --- Find uv (Explorer often has a smaller PATH than Cursor terminal) ---
set "UV_CMD="
where uv >nul 2>&1 && set "UV_CMD=uv"
if not defined UV_CMD if exist "%USERPROFILE%\.local\bin\uv.exe" set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
if not defined UV_CMD if exist "%LOCALAPPDATA%\Programs\uv\uv.exe" set "UV_CMD=%LOCALAPPDATA%\Programs\uv\uv.exe"
if not defined UV_CMD if exist "%USERPROFILE%\.cargo\bin\uv.exe" set "UV_CMD=%USERPROFILE%\.cargo\bin\uv.exe"

if not defined UV_CMD (
    echo ERROR: uv not found.
    echo.
    echo Double-click uses a different PATH than Cursor. Install uv, then open a NEW cmd:
    echo   winget install astral-sh.uv
    echo.
    echo Or run once in cmd:
    echo   setx PATH "%%USERPROFILE%%\.local\bin;%%PATH%%"
    echo.
    pause
    exit /b 1
)
echo Using: %UV_CMD%
echo.

set "ENV_FILE=%USERPROFILE%\.langflow\.env"
if not exist "%ENV_FILE%" (
    echo NOTE: %ENV_FILE% not found — using defaults.
    echo.
)

if not exist "%PROJECT_ROOT%\src\backend\base\langflow\frontend\index.html" (
    echo ERROR: Frontend not built.
    echo Run once: %PROJECT_ROOT%\scripts\windows\build_frontend_only.bat
    echo.
    pause
    exit /b 1
)

echo Syncing Python dependencies (first time may take several minutes)...
"%UV_CMD%" sync --frozen
if errorlevel 1 (
    echo.
    echo ERROR: uv sync failed. Try in cmd:
    echo   cd /d "%PROJECT_ROOT%"
    echo   uv sync
    echo.
    pause
    exit /b 1
)

echo.
echo Starting server...
echo.

REM Stop stale Langflow on port 7860 so code and .env changes apply.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":7860 .*LISTENING"') do (
    echo Stopping old process PID %%p on port 7860...
    taskkill /PID %%p /F >nul 2>&1
)

if exist "%ENV_FILE%" (
    "%UV_CMD%" run langflow run --log-level error --env-file "%ENV_FILE%"
) else (
    echo WARNING: %ENV_FILE% missing - DB and credentials may use project defaults.
    "%UV_CMD%" run langflow run --log-level error
)

set "EC=%ERRORLEVEL%"
echo.
echo WorkflowV2 stopped. Exit code: %EC%
pause
exit /b %EC%
