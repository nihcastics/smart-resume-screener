# Start Both Backend and Frontend Servers
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Smart Resume Screener - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend
Write-Host "Starting Backend Server (port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; Write-Host 'Backend Server - Press Ctrl+C to stop' -ForegroundColor Yellow; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend Server (port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; Write-Host 'Frontend Server - Press Ctrl+C to stop' -ForegroundColor Yellow; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Servers Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend UI:     http://localhost:5173" -ForegroundColor White
Write-Host "Backend API:     http://localhost:8000" -ForegroundColor White
Write-Host "API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Note: Two new windows have opened for the servers." -ForegroundColor Yellow
Write-Host "      Close those windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
