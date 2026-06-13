@echo off
REM Legacy launcher name — redirects to run_workflowv2.bat (copy of langflow-work).
call "%~dp0run_workflowv2.bat"
exit /b %ERRORLEVEL%
