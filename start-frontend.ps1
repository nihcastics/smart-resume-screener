# Start Frontend Server
Write-Host "Starting Smart Resume Screener Frontend on port 5173..." -ForegroundColor Green
Write-Host "Frontend will run in a new window. Close that window to stop the server." -ForegroundColor Yellow
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm run dev"
