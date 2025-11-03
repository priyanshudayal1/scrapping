# Start Instance 4 - Scripts 52-66
# Pages: 130,510 to 168,867

Write-Host "Starting Instance 4..." -ForegroundColor Green
Write-Host "Scripts: 52-66 (15 scripts)" -ForegroundColor Cyan
Write-Host "Pages: 130,510 to 168,867" -ForegroundColor Cyan
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
