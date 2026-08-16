<# 
.SYNOPSIS
    Start ELE Agent locally for development
.DESCRIPTION
    Starts backend (FastAPI), web (Next.js), and desktop (Electron) in development mode
#>

param(
    [switch]$BackendOnly,
    [switch]$WebOnly,
    [switch]$DesktopOnly,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Write-Header($msg) {
    Write-Host "`n=== $msg ===" -ForegroundColor Cyan
}

function Write-Success($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-Error($msg) {
    Write-Host "[ERR] $msg" -ForegroundColor Red
}

function Write-Info($msg) {
    Write-Host "  $msg" -ForegroundColor Gray
}

# Check prerequisites
Write-Header "Checking Prerequisites"

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found. Please install Python 3.11+"
    exit 1
}
Write-Success "Python: $pythonVersion"

$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Node.js not found. Please install Node.js 20+"
    exit 1
}
Write-Success "Node.js: $nodeVersion"

$npmVersion = npm --version 2>&1
Write-Success "npm: $npmVersion"

# Check .env file
$envFile = Join-Path $rootPath ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "`n.env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item (Join-Path $rootPath ".env.example") $envFile
    Write-Warning "Please edit .env with your API keys before continuing!"
    Write-Host "Required: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY" -ForegroundColor Yellow
    Read-Host "Press Enter after editing .env to continue..."
}

# Install dependencies
if (-not $SkipInstall) {
    Write-Header "Installing Dependencies"

    # Backend
    if (-not $WebOnly -and -not $DesktopOnly) {
        Write-Info "Installing backend dependencies..."
        Set-Location (Join-Path $rootPath "backend")
        if (-not (Test-Path ".venv")) {
            python -m venv .venv
        }
        .\.venv\Scripts\Activate.ps1
        pip install -r requirements.txt -q
        pip install -r requirements-dev.txt -q
        Write-Success "Backend dependencies installed"
    }

    # Web
    if (-not $BackendOnly -and -not $DesktopOnly) {
        Write-Info "Installing web dependencies..."
        Set-Location (Join-Path $rootPath "web")
        npm install
        Write-Success "Web dependencies installed"
    }

    # Desktop
    if (-not $BackendOnly -and -not $WebOnly) {
        Write-Info "Installing desktop dependencies..."
        Set-Location (Join-Path $rootPath "desktop")
        npm install
        Write-Success "Desktop dependencies installed"
    }

    # CLI
    Write-Info "Installing CLI..."
    Set-Location (Join-Path $rootPath "cli")
    pip install -e . -q
    Write-Success "CLI installed"

    # Initialize Database
    if (-not $WebOnly -and -not $DesktopOnly) {
        Write-Info "Initializing local database..."
        Set-Location (Join-Path $rootPath "backend")
        .\.venv\Scripts\Activate.ps1
        python setup_local.py
        Write-Success "Database initialized"
    }
}

Set-Location $rootPath

# Start services
Write-Header "Starting Services"

$processes = @()

if (-not $WebOnly -and -not $DesktopOnly) {
    Write-Info "Starting Backend (FastAPI) on http://localhost:8000..."
    $backendProc = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$rootPath\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000" -PassThru
    $processes += $backendProc
    Start-Sleep 3
    Write-Success "Backend started (PID: $($backendProc.Id))"
}

if (-not $BackendOnly -and -not $DesktopOnly) {
    Write-Info "Starting Web (Next.js) on http://localhost:3000..."
    $webProc = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$rootPath\web'; npm run dev" -PassThru
    $processes += $webProc
    Start-Sleep 3
    Write-Success "Web started (PID: $($webProc.Id))"
}

if (-not $BackendOnly -and -not $WebOnly) {
    Write-Info "Starting Desktop (Electron)..."
    $desktopProc = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$rootPath\desktop'; npm run dev" -PassThru
    $processes += $desktopProc
    Write-Success "Desktop started (PID: $($desktopProc.Id))"
}

Write-Header "All Services Running"
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Web App:      http://localhost:3000" -ForegroundColor Green
Write-Host "Desktop:      Electron window should open" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop all services..." -ForegroundColor Yellow

# Wait for interrupt
try {
    while ($true) {
        Start-Sleep 1
    }
}
finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    foreach ($proc in $processes) {
        if (-not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force
        }
    }
    Write-Success "All services stopped"
}