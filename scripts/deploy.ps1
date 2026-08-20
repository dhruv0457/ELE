# ==============================================================================
# ELE Agent - Production Deployment Automation Script (Windows)
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   ELE AGENT — Production Stack Deployment (Windows)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# Verify Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[X] Docker is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Docker detected." -ForegroundColor Green

# Ensure .env file
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[!] Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "[X] .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

# Build and start
Write-Host "[+] Building container images..." -ForegroundColor Cyan
docker compose build --pull

Write-Host "[+] Launching ELE Agent production services..." -ForegroundColor Cyan
docker compose up -d

# Check health
Write-Host "[+] Verifying service health..." -ForegroundColor Cyan
$healthy = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($res.status -eq "ok" -or $res.status -eq "healthy" -or $res) {
            $healthy = $true
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
}

if ($healthy) {
    Write-Host "`n=================================================================" -ForegroundColor Green
    Write-Host "   ELE Agent Production Stack is Live!" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "   * Web Dashboard:  http://localhost:3000" -ForegroundColor White
    Write-Host "   * Backend API:    http://localhost:8000" -ForegroundColor White
    Write-Host "   * Health Check:   http://localhost:8000/health" -ForegroundColor White
    Write-Host "`nLogs:        docker compose logs -f" -ForegroundColor Gray
    Write-Host "Stop:        docker compose down" -ForegroundColor Gray
} else {
    Write-Host "[!] Containers started. Check logs with 'docker compose logs'." -ForegroundColor Yellow
}
