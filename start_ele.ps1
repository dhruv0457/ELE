# ELE Agent - Single Command Launcher
# Opens backend in new window, then launches CLI

Write-Host "Starting ELE Agent..." -ForegroundColor Cyan

# Kill existing python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Start backend in NEW persistent window
$backendProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", "start", "ELE Backend", "E:\ANACONDA\envs\ele-agent\python.exe", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info" `
    -WorkingDirectory "D:\ELE\backend" `
    -PassThru

Write-Host "Backend window opened (PID: $($backendProc.Id))" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt 30 -and -not $ready) {
    Start-Sleep -Seconds 2
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch { }
}

if (-not $ready) {
    Write-Host "Backend failed to start!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Backend ready! Starting CLI..." -ForegroundColor Green

# Launch CLI (blocks)
& "E:\ANACONDA\envs\ele-agent\python.exe" -m src.app

Write-Host "ELE Agent stopped." -ForegroundColor Cyan