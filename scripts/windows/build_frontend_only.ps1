#!/usr/bin/env pwsh

Write-Host "Starting Langflow frontend build process..." -ForegroundColor Green

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Resolve-Path (Join-Path $scriptDir "..\..")

# Step 1: Install frontend dependencies
Write-Host "`nStep 1: Installing frontend dependencies..." -ForegroundColor Yellow
try {
    Set-Location (Join-Path $projectRoot "src\frontend")
    Write-Host "Running npm install..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed"
    }
} catch {
    Write-Host "Error in frontend dependency installation: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Build frontend
Write-Host "`nStep 2: Building frontend..." -ForegroundColor Yellow
try {
    Write-Host "Running npm run build..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "npm run build failed"
    }
} catch {
    Write-Host "Error in frontend build: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Copy build files
Write-Host "`nStep 3: Copying build files to backend..." -ForegroundColor Yellow
try {
    Set-Location $projectRoot

    # Determine build directory
    $buildDir = if (Test-Path "src\frontend\build") {
        "src\frontend\build"
    } elseif (Test-Path "src\frontend\dist") {
        "src\frontend\dist"
    } else {
        throw "Neither build nor dist directory found in src\frontend"
    }

    $targetDir = "src\backend\base\langflow\frontend"
    Write-Host "Copying from $buildDir to $targetDir"

    # Create target directory if it doesn't exist
    if (-not (Test-Path $targetDir)) {
        New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
    }

    # Remove existing files in target directory (FORCES CLEAN REPLACEMENT)
    Write-Host "Removing existing files from target directory..." -ForegroundColor Cyan
    if (Test-Path "$targetDir\*") {
        Remove-Item "$targetDir\*" -Recurse -Force
    }

    # Copy all files from build directory
    Copy-Item "$buildDir\*" -Destination $targetDir -Recurse -Force
    Write-Host "Build files copied successfully!" -ForegroundColor Green

} catch {
    Write-Host "Error copying files: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nFrontend build process completed!" -ForegroundColor Green
Write-Host "You can now run: Langflow-Start.bat or scripts\windows\run_langflow.bat" -ForegroundColor Cyan