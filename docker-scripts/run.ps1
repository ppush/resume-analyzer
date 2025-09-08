# PowerShell script for running Resume Analyzer in Docker

Write-Host "🚀 Starting Resume Analyzer in Docker..." -ForegroundColor Cyan

# Check that LM Studio is running
Write-Host "🔍 Checking LM Studio availability..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ LM Studio available on localhost:1234" -ForegroundColor Green
} catch {
    Write-Host "⚠️  LM Studio not available on localhost:1234" -ForegroundColor Yellow
    Write-Host "   Make sure LM Studio is running locally" -ForegroundColor White
    Write-Host "   or use docker-compose with LM Studio in container" -ForegroundColor White
}

# Create necessary folders
if (!(Test-Path "results")) { New-Item -ItemType Directory -Path "results" }
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }

# Start web service
Write-Host "🐳 Starting Resume Analyzer Web Service..." -ForegroundColor Cyan
docker-compose up --build

Write-Host "🎉 Resume Analyzer Web Service finished!" -ForegroundColor Green
Write-Host "🌐 Web service will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 API documentation: http://localhost:8000/docs" -ForegroundColor Yellow
