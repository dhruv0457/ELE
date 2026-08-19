@echo off
REM ELE Agent - Single Command Launcher
REM Usage: ele

cd /d D:\ELE

echo Starting ELE Agent...

REM Kill any existing python processes
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start backend in NEW window that STAYS OPEN using PowerShell Start-Process
powershell -Command "Start-Process -FilePath 'E:\ANACONDA\envs\ele-agent\python.exe' -ArgumentList '-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info' -WorkingDirectory 'D:\ELE\backend' -WindowStyle Normal"

REM Wait for backend to be ready using PowerShell
echo Waiting for backend to start...
powershell -Command "$maxAttempts = 30; $attempt = 0; do { Start-Sleep -Seconds 2; $attempt++; try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3 -ErrorAction Stop -UseBasicParsing; if ($response.StatusCode -eq 200) { exit 0 } } catch { } } while ($attempt -lt $maxAttempts); exit 1"
if errorlevel 1 (
    echo Backend failed to start!
    pause
    exit /b 1
)

echo Backend ready! Starting CLI...

REM Launch CLI in THIS window - from CLI directory
cd /d D:\ELE\cli
E:\ANACONDA\envs\ele-agent\python.exe -m src.app