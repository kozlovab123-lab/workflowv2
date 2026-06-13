#!/usr/bin/env pwsh
# Legacy launcher — redirects to run_workflowv2.ps1 (copy of langflow-work).
& (Join-Path $PSScriptRoot "run_workflowv2.ps1") @args
exit $LASTEXITCODE
