@echo off
REM Monte Carlo Simulations - Windows Startup Script

echo.
echo 🎰 Starting Monte Carlo Simulations...
echo.

REM Check if backend virtual environment exists
if not exist "backend\venv" (
    if not exist "backend\env" (
        echo 📦 Installing backend dependencies...
        cd backend
        python -m venv venv
        call venv\Scripts\activate.bat
        pip install -r requirements.txt
        cd ..
    )
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo 🚀 Starting backend server...
cd backend
if exist "venv" (
    start "Backend Server" cmd /k "venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) else (
    start "Backend Server" cmd /k "env\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
)
cd ..

echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo 🚀 Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ✅ All services started!
echo.
echo 📍 Access points:
echo    Frontend:  http://localhost:5173
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo.
echo Press any key to exit and stop all services...
pause > nul
