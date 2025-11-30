@echo off
echo Starting Code Review Agent...

echo.
echo Starting Backend...
start "Backend" cmd /k "cd backend_full && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend_full && npm run dev"

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause