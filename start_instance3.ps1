# Start Instance 3 - Scripts 35-51
# Pages: 87,007 to 130,509

Write-Host "Starting Instance 3..." -ForegroundColor Green
Write-Host "Scripts: 35-51 (17 scripts)" -ForegroundColor Cyan
Write-Host "Pages: 87,007 to 130,509" -ForegroundColor Cyan
Write-Host ""

# Copy environment file
Copy-Item -Path ".env.instance3" -Destination "api+ui\.env" -Force
Write-Host "✓ Environment configured for Instance 3" -ForegroundColor Green

# Navigate to API directory
Set-Location "api+ui"

# Start API server
Write-Host "Starting API Server on port 5000..." -ForegroundColor Yellow
python api_server_v2.py
