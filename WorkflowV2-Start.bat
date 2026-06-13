@echo off
REM Alias launcher — redirects to LangflowV2-Start.bat.
cd /d "%~dp0"
call "%~dp0LangflowV2-Start.bat"
exit /b %ERRORLEVEL%
