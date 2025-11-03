# Start Instance 3 - Scripts 35-51
# Pages: 87,007 to 130,509

Write-Host "Starting Instance 3..." -ForegroundColor Green
Write-Host "Scripts: 35-51 (17 scripts)" -ForegroundColor Cyan
Write-Host "Pages: 87,007 to 130,509" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists in api+ui directory
if (Test-Path "api+ui\.env") {
    Write-Host "Environment file found" -ForegroundColor Green
} else {
    Write-Host "Warning: No .env file found in api+ui directory" -ForegroundColor Yellow
    Write-Host "The API server will use default settings" -ForegroundColor Yellow
}

# Navigate to API directory
Set-Location "api+ui"

# Start API server
Write-Host "Starting API Server on port 5000..." -ForegroundColor Yellow
python api_server_v2.py
