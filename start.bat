@echo off
setlocal enabledelayedexpansion

:: 🌱 Flourish - Development Start Script
echo.
echo ======================================
echo    🌱 Flourish Development Starter
echo ======================================
echo.

:: Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.9+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python is installed
python --version

:: Check Node.js installation
echo.
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js 18+ from: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js is installed
node --version

:: Check backend dependencies
echo.
echo [3/5] Checking backend dependencies...
if not exist "apps\api\__pycache__" (
    echo [INFO] Installing Python dependencies...
    cd apps\api
    python -m pip install -r requirements.txt
    cd ..\..
)
echo [OK] Backend dependencies ready

:: Check frontend dependencies
echo.
echo [4/5] Checking frontend dependencies...
if not exist "apps\web\node_modules" (
    echo [INFO] Installing Node dependencies...
    cd apps\web
    call npm install
    cd ..\..
)
echo [OK] Frontend dependencies ready

:: Check Firebase configuration
echo.
echo [5/5] Checking Firebase configuration...
if not exist "apps\api\firebase-service-account.json" (
    echo [WARNING] Firebase service account key not found!
    echo Please add firebase-service-account.json to apps\api\
) else (
    echo [OK] Firebase configuration found
)

:: Check Ollama (optional)
echo.
echo [Optional] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Ollama is not installed - AI features will be limited
    echo Install from: https://ollama.ai
) else (
    echo [OK] Ollama is installed
    ollama --version
)

echo.
echo ======================================
echo    🚀 Starting Services
echo ======================================
echo.

:: Start Backend API
echo Starting Backend API on port 8000...
start "Flourish Backend API" cmd /k "cd /d %CD%\apps\api && echo 🌱 Flourish Backend API && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start Frontend
echo Starting Frontend on port 5173...
start "Flourish Frontend" cmd /k "cd /d %CD%\apps\web && echo 🌱 Flourish Frontend && npm run dev"

:: Wait for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ======================================
echo    ✅ Services Started Successfully!
echo ======================================
echo.
echo Access the application at:
echo   🌐 Frontend:  http://localhost:5173
echo   ⚙️  Backend:   http://localhost:8000
echo   📚 API Docs:  http://localhost:8000/docs
echo.
echo Press any key to open the application...
pause >nul

:: Open browser
start http://localhost:5173

echo.
echo 🌱 Happy gardening!
echo.
echo 💡 Tip: Close the terminal windows to stop the services
echo.
pause
