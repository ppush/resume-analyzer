# PowerShell script for running Resume Analyzer in development mode

Write-Host "🛠️  Starting Resume Analyzer in development mode..." -ForegroundColor Cyan

# Create necessary folders
if (!(Test-Path "results")) { New-Item -ItemType Directory -Path "results" }
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }

# Start web service for development
Write-Host "🐳 Starting Resume Analyzer Web Service for development..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml up --build

Write-Host "🎉 Resume Analyzer Web Service for development finished!" -ForegroundColor Green
Write-Host "🌐 Web service will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 API documentation: http://localhost:8000/docs" -ForegroundColor Yellow
