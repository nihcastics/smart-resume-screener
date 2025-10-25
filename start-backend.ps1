# Start Backend Server
Write-Host "Starting Smart Resume Screener Backend on port 8000..." -ForegroundColor Green
Write-Host "Backend will run in a new window. Close that window to stop the server." -ForegroundColor Yellow
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
