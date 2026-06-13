#!/usr/bin/env pwsh
# Run WorkflowV2 from source (copy of langflow-work).
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $projectRoot

Write-Host "WorkflowV2 — copy of langflow-work" -ForegroundColor Cyan
Write-Host "Syncing dependencies..." -ForegroundColor Cyan
uv sync --frozen
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$frontendIndex = Join-Path $projectRoot "src\backend\base\langflow\frontend\index.html"
if (-not (Test-Path $frontendIndex)) {
    Write-Host "Building frontend (first time)..." -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "build_frontend_only.ps1")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$envFile = Join-Path $env:USERPROFILE ".langflow\.env"
$runArgs = @("run", "--log-level", "error")
if (Test-Path $envFile) {
    Write-Host "Using env file: $envFile" -ForegroundColor Cyan
    $runArgs += @("--env-file", $envFile)
}
$runArgs += $args

Write-Host "Starting WorkflowV2 (see banner for URL; default http://127.0.0.1:7860)" -ForegroundColor Green
uv run langflow @runArgs
