# 🌱 Flourish - Development Start Script

Write-Host "🌱 Starting Flourish Application..." -ForegroundColor Green
Write-Host ""

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonInstalled) {
    Write-Host "❌ Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Python is installed: $(python --version)" -ForegroundColor Green

# Check Node.js installation
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Cyan
$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeInstalled) {
    Write-Host "❌ Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Node.js is installed: $(node --version)" -ForegroundColor Green

# Check if backend dependencies are installed
Write-Host "🔍 Checking backend dependencies..." -ForegroundColor Cyan
if (-not (Test-Path "apps\api\__pycache__")) {
    Write-Host "⚠️  Backend dependencies may not be installed" -ForegroundColor Yellow
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    Push-Location apps\api
    python -m pip install -r requirements.txt
    Pop-Location
}
Write-Host "✅ Backend dependencies ready" -ForegroundColor Green

# Check if frontend dependencies are installed
Write-Host "🔍 Checking frontend dependencies..." -ForegroundColor Cyan
if (-not (Test-Path "apps\web\node_modules")) {
    Write-Host "⚠️  Frontend dependencies not installed" -ForegroundColor Yellow
    Write-Host "Installing Node dependencies..." -ForegroundColor Cyan
    Push-Location apps\web
    npm install
    Pop-Location
}
Write-Host "✅ Frontend dependencies ready" -ForegroundColor Green

# Check Firebase configuration
Write-Host "🔥 Checking Firebase configuration..." -ForegroundColor Cyan
if (-not (Test-Path "apps\api\firebase-service-account.json")) {
    Write-Host "⚠️  Firebase service account key not found!" -ForegroundColor Yellow
    Write-Host "Please add firebase-service-account.json to apps\api\" -ForegroundColor Yellow
} else {
    Write-Host "✅ Firebase configuration found" -ForegroundColor Green
}

# Check if Ollama is installed (optional)
Write-Host "🤖 Checking Ollama installation (optional)..." -ForegroundColor Cyan
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaInstalled) {
    Write-Host "⚠️  Ollama is not installed (AI features will be limited)" -ForegroundColor Yellow
    Write-Host "Install from: https://ollama.ai" -ForegroundColor DarkGray
} else {
    Write-Host "✅ Ollama is installed" -ForegroundColor Green
    
    # Start Ollama server in background if not running
    $ollamaRunning = Test-Port -Port 11434
    if (-not $ollamaRunning) {
        Write-Host "Starting Ollama server..." -ForegroundColor Cyan
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 2
    }
    
    # Check if llama3 model is available
    $models = ollama list 2>$null
    if ($models -notmatch "llama3") {
        Write-Host "⚠️  llama3 model not found" -ForegroundColor Yellow
        Write-Host "Run 'ollama pull llama3' to enable AI features" -ForegroundColor DarkGray
    } else {
        Write-Host "✅ llama3 model is available" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Green
Write-Host ""

# Check if backend port is already in use
if (Test-Port -Port 8000) {
    Write-Host "⚠️  Port 8000 is already in use!" -ForegroundColor Yellow
    Write-Host "Please stop the existing process or change the port." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
}

# Check if frontend port is already in use
if (Test-Port -Port 5173) {
    Write-Host "⚠️  Port 5173 is already in use!" -ForegroundColor Yellow
    Write-Host "Please stop the existing process or change the port." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
}

# Start Backend API
Write-Host "🔧 Starting Backend API (Port 8000)..." -ForegroundColor Cyan
$backendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Write-Host '🌱 Flourish Backend API' -ForegroundColor Green; cd '$PWD\apps\api'; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "💻 Starting Frontend (Port 5173)..." -ForegroundColor Cyan
$frontendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Write-Host '🌱 Flourish Frontend' -ForegroundColor Green; cd '$PWD\apps\web'; npm run dev"
) -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "📝 Access the application at:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   ⚙️  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   📚 API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Press any key to open the application in your browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "🌱 Happy gardening!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tip: Close the terminal windows to stop the services" -ForegroundColor DarkGray
Write-Host ""
