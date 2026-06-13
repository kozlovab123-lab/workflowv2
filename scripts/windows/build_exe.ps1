#!/usr/bin/env pwsh
# Build Langflow as a standalone Windows executable (dist\Langflow.exe).
# Prerequisites: Python 3.13 (see .python-version), uv, Node.js with npm.
# See BUILD_EXE.md for details.

$ErrorActionPreference = "Stop"

function Stop-LangflowBuildLocks {
    param([string]$ProjectRoot)

    $exePath = Join-Path $ProjectRoot "dist\Langflow\Langflow.exe"
    if (-not (Test-Path $exePath)) {
        $exePath = Join-Path $ProjectRoot "dist\Langflow.exe"
    }

    Write-Host "Stopping running Langflow processes (if any)..." -ForegroundColor Cyan
    Get-Process -Name "Langflow" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    $pathsToRemove = @($exePath)
    $onedir = Join-Path $ProjectRoot "dist\Langflow"
    if (Test-Path $onedir) {
        $pathsToRemove += $onedir
    }

    foreach ($target in $pathsToRemove) {
        if (-not (Test-Path $target)) { continue }
        $removed = $false
        foreach ($attempt in 1..8) {
            try {
                Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
                Write-Host "Removed previous build: $target" -ForegroundColor Green
                $removed = $true
                break
            } catch {
                Write-Host "File locked ($attempt/8): $target - close Langflow.exe / Langflow.bat and retrying..." -ForegroundColor Yellow
                Get-Process -Name "Langflow" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 3
            }
        }
        if (-not $removed) {
            throw "Cannot overwrite $target (access denied). Close Langflow.exe in Task Manager, then run build again."
        }
    }
}

function Invoke-Npm {
    param([string[]]$NpmArgs)
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        & npm @NpmArgs
        return
    }
    if (Get-Command npx -ErrorAction SilentlyContinue) {
        & npx --yes npm@latest @NpmArgs
        return
    }
    throw "npm not found. Install Node.js LTS from https://nodejs.org/ and ensure npm is on PATH."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Resolve-Path (Join-Path $scriptDir "..\..")

Write-Host "Langflow Windows EXE build" -ForegroundColor Green
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan

Set-Location $projectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    python -m pip install uv
}

Write-Host "`n[1/3] Installing Python dependencies (uv sync)..." -ForegroundColor Yellow
uv sync --frozen --group packaging
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/3] Building frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\src\frontend"
Invoke-Npm @("install")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Invoke-Npm @("run", "build")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Set-Location $projectRoot
$buildDir = if (Test-Path "src\frontend\build") { "src\frontend\build" } else { "src\frontend\dist" }
$targetDir = "src\backend\base\langflow\frontend"
if (-not (Test-Path $targetDir)) {
    New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
}
if (Test-Path "$targetDir\*") {
    Remove-Item "$targetDir\*" -Recurse -Force
}
Copy-Item "$buildDir\*" -Destination $targetDir -Recurse -Force
Write-Host "Frontend copied to $targetDir" -ForegroundColor Green

if (-not (Test-Path "$targetDir\index.html")) {
    Write-Host "ERROR: Frontend build missing index.html in $targetDir" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/3] Running PyInstaller (this may take 15-45+ minutes)..." -ForegroundColor Yellow
Stop-LangflowBuildLocks -ProjectRoot $projectRoot
uv run pyinstaller --noconfirm --clean "$scriptDir\langflow.spec"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$onedirExe = Join-Path $projectRoot "dist\Langflow\Langflow.exe"
$onefileExe = Join-Path $projectRoot "dist\Langflow.exe"
$exePath = if (Test-Path $onedirExe) { $onedirExe } elseif (Test-Path $onefileExe) { $onefileExe } else { $null }

Copy-Item -Path "$scriptDir\Langflow.bat" -Destination (Join-Path $projectRoot "dist\Langflow.bat") -Force
if (Test-Path (Join-Path $projectRoot "dist\Langflow")) {
    Copy-Item -Path "$scriptDir\Langflow.bat" -Destination (Join-Path $projectRoot "dist\Langflow\Langflow.bat") -Force
}

if ($exePath) {
    $sizeMb = [math]::Round((Get-Item $exePath).Length / 1MB, 1)
    Write-Host "`nBuild succeeded!" -ForegroundColor Green
    Write-Host ("Executable: {0} (launcher {1} MB)" -f $exePath, $sizeMb) -ForegroundColor Cyan
    Write-Host "Start: dist\Langflow.bat  (or dist\Langflow\Langflow.bat for onedir)" -ForegroundColor Cyan
    Write-Host "Boot log: $env:USERPROFILE\.langflow\langflow-exe-boot.log" -ForegroundColor Cyan
    Write-Host "Main log: $env:USERPROFILE\.langflow\langflow-exe.log" -ForegroundColor Cyan
    Write-Host "Browser: http://127.0.0.1:7860 (after server is ready)" -ForegroundColor Cyan
} else {
    Write-Host "ERROR: Langflow.exe was not created under dist\" -ForegroundColor Red
    exit 1
}
