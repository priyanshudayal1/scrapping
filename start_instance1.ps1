# Start Instance 1 - Scripts 1-17
# Pages: 1 to 43,503

Write-Host "Starting Instance 1..." -ForegroundColor Green
Write-Host "Scripts: 1-17 (17 scripts)" -ForegroundColor Cyan
Write-Host "Pages: 1 to 43,503" -ForegroundColor Cyan
Write-Host ""

# Copy environment file
Copy-Item -Path ".env.instance1" -Destination "api+ui\.env" -Force
Write-Host "Environment configured for Instance 1" -ForegroundColor Green

# Navigate to API directory
Set-Location "api+ui"

# Start API server
Write-Host "Starting API Server on port 5000..." -ForegroundColor Yellow
python api_server_v2.py
