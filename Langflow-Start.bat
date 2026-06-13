@echo off
REM Legacy launcher name — redirects to WorkflowV2-Start.bat (copy of langflow-work).
cd /d "%~dp0"
call "%~dp0WorkflowV2-Start.bat"
exit /b %ERRORLEVEL%
