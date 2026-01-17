<#
.SYNOPSIS
    Cross-platform pre-commit hook setup for Windows

.DESCRIPTION
    This script installs Gitleaks and pre-commit hooks for secret scanning.
    See .agent/docs/secret-scanning-setup.md for full documentation.

.EXAMPLE
    .\tools\setup-hooks.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$GITLEAKS_VERSION = "8.21.2"

function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Err { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-Command {
    param([string]$Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-GitleaksWithWinget {
    if (Test-Command "winget") {
        Write-Status "Installing Gitleaks via winget..."
        winget install Gitleaks.Gitleaks --silent
        return $true
    }
    return $false
}

function Install-GitleaksWithChoco {
    if (Test-Command "choco") {
        Write-Status "Installing Gitleaks via Chocolatey..."
        choco install gitleaks -y
        return $true
    }
    return $false
}

function Install-GitleaksWithScoop {
    if (Test-Command "scoop") {
        Write-Status "Installing Gitleaks via Scoop..."
        scoop install gitleaks
        return $true
    }
    return $false
}

function Install-GitleaksManual {
    Write-Status "Downloading Gitleaks v$GITLEAKS_VERSION..."

    $arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x32" }
    $zipName = "gitleaks_${GITLEAKS_VERSION}_windows_${arch}.zip"
    $url = "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/${zipName}"
    $downloadPath = Join-Path $env:TEMP $zipName
    $extractPath = Join-Path $env:TEMP "gitleaks-extract"

    # Download
    Invoke-WebRequest -Uri $url -OutFile $downloadPath -UseBasicParsing

    # Extract
    if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath

    # Install to user's local bin
    $installDir = Join-Path $env:LOCALAPPDATA "Programs\gitleaks"
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }

    Copy-Item (Join-Path $extractPath "gitleaks.exe") -Destination $installDir -Force

    # Add to PATH if not already there
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$installDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$userPath;$installDir", "User")
        $env:PATH = "$env:PATH;$installDir"
        Write-Status "Added $installDir to user PATH"
    }

    # Cleanup
    Remove-Item $downloadPath -Force -ErrorAction SilentlyContinue
    Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue

    Write-Success "Gitleaks installed to $installDir"
}

function Install-Gitleaks {
    # Try package managers in order of preference
    if (Install-GitleaksWithWinget) { return }
    if (Install-GitleaksWithChoco) { return }
    if (Install-GitleaksWithScoop) { return }

    # Fall back to manual install
    Write-Warning "No package manager found, using manual install..."
    Install-GitleaksManual
}

function Install-PreCommit {
    Write-Status "Installing pre-commit via pip..."

    if (Test-Command "pip") {
        pip install pre-commit
    } elseif (Test-Command "pip3") {
        pip3 install pre-commit
    } else {
        Write-Err "pip not found. Please install Python and pip first."
        Write-Err "Download Python: https://www.python.org/downloads/"
        exit 1
    }
}

# Main
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Pre-commit Hook Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "  Secret Scanning with Gitleaks" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check/Install Gitleaks
if (Test-Command "gitleaks") {
    $version = & gitleaks version 2>$null
    Write-Success "Gitleaks already installed: $version"
} else {
    Write-Warning "Gitleaks not found. Installing..."
    Install-Gitleaks

    # Refresh PATH for current session
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
}

# Check/Install pre-commit
if (Test-Command "pre-commit") {
    $version = & pre-commit --version 2>$null
    Write-Success "pre-commit already installed: $version"
} else {
    Write-Warning "pre-commit not found. Installing..."
    Install-PreCommit
}

# Ensure we're in the git repository root
if (-not (Test-Path ".pre-commit-config.yaml")) {
    Write-Err "Cannot find .pre-commit-config.yaml"
    Write-Err "Please run this script from the project root directory."
    exit 1
}

# Install pre-commit hooks
Write-Status "Installing pre-commit hooks..."
& pre-commit install

# Run initial scan
Write-Status "Running initial scan (this may take a moment)..."
$scanResult = & pre-commit run --all-files 2>&1
$scanExitCode = $LASTEXITCODE

if ($scanExitCode -eq 0) {
    Write-Success "All checks passed!"
} else {
    Write-Output $scanResult
    Write-Warning "Some checks failed or fixed files. Review the output above."
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Success "Setup complete!"
Write-Host ""
Write-Host "Your commits will now be automatically scanned for:"
Write-Host "  🔐 Secrets and credentials (Gitleaks)"
Write-Host "  🐘 Large files (>5MB)"
Write-Host "  ✅ JSON/YAML syntax errors"
Write-Host "  🔑 Private keys"
Write-Host ""
Write-Host "To manually scan: pre-commit run --all-files"
Write-Host "To bypass (emergency only): git commit --no-verify"
Write-Host "==================================================" -ForegroundColor Cyan
