# Start Instance 2 - Scripts 18-34
# Pages: 43,504 to 87,006

Write-Host "Starting Instance 2..." -ForegroundColor Green
Write-Host "Scripts: 18-34 (17 scripts)" -ForegroundColor Cyan
Write-Host "Pages: 43,504 to 87,006" -ForegroundColor Cyan
Write-Host ""

# Copy environment file
Copy-Item -Path ".env.instance2" -Destination "api+ui\.env" -Force
Write-Host "✓ Environment configured for Instance 2" -ForegroundColor Green

# Navigate to API directory
Set-Location "api+ui"

# Start API server
Write-Host "Starting API Server on port 5000..." -ForegroundColor Yellow
python api_server_v2.py
