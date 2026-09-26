# VISTAR-2.5D: Adaptive Variable Resolution 2.5D LiDAR Mapping
# Smart India Hackathon 2026 (Problem Statement: SIH26053)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  VISTAR-2.5D: Adaptive Variable Resolution 2.5D LiDAR Mapping" -ForegroundColor White
Write-Host "  Smart India Hackathon 2026 (SIH26053)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/2] Launching Python FastAPI Backend on port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

Write-Host "[2/2] Launching Vite React Frontend on port 5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir/frontend'; npm run dev"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173/"

Write-Host "`nPrototype running at http://localhost:5173/" -ForegroundColor Cyan
