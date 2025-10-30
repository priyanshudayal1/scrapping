# Start Instance 4 - Scripts 52-66
# Pages: 130,510 to 168,867

Write-Host "Starting Instance 4..." -ForegroundColor Green
Write-Host "Scripts: 52-66 (15 scripts)" -ForegroundColor Cyan
Write-Host "Pages: 130,510 to 168,867" -ForegroundColor Cyan
Write-Host ""

# Copy environment file
Copy-Item -Path ".env.instance4" -Destination "api+ui\.env" -Force
Write-Host "✓ Environment configured for Instance 4" -ForegroundColor Green

# Navigate to API directory
Set-Location "api+ui"

# Start API server
Write-Host "Starting API Server on port 5000..." -ForegroundColor Yellow
python api_server_v2.py
