@echo off
echo ======================================================================
echo   VISTAR-2.5D: Adaptive Variable Resolution 2.5D LiDAR Mapping
echo   Smart India Hackathon 2026 (Problem Statement: SIH26053)
echo ======================================================================
echo.

if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
) else (
  set "PYTHON=python"
)

echo [1/2] Starting Python FastAPI Backend on port 8000...
start "VISTAR-2.5D Backend" cmd /k "%PYTHON% -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Starting React Vite Frontend on port 5173...
cd frontend
start "VISTAR-2.5D Frontend" cmd /k "npm run dev"

echo.
echo Launching prototype in default browser at http://localhost:5173/ ...
timeout /t 3 >nul
start http://localhost:5173/

echo.
echo Prototype is active! Press Ctrl+C in the launched windows to stop.
