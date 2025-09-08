# PowerShell script for building Resume Analyzer Docker image

Write-Host "🐳 Building Resume Analyzer Docker image..." -ForegroundColor Cyan

# Build image
docker build -t resume-analyzer:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image built successfully!" -ForegroundColor Green
    Write-Host "📦 Image name: resume-analyzer:latest" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🚀 To run use:" -ForegroundColor Cyan
    Write-Host "   docker-compose up" -ForegroundColor White
    Write-Host "   or" -ForegroundColor White
    Write-Host "   docker run -it resume-analyzer:latest" -ForegroundColor White
} else {
    Write-Host "❌ Error building image!" -ForegroundColor Red
    exit 1
}
