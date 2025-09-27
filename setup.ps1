# Review Radar - Project Setup Script
# This script sets up the entire project environment

# Stop on first error
$ErrorActionPreference = 'Stop'

Write-Host '🚀 Setting up Review Radar project...' -ForegroundColor Cyan

# Function to check if command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Check prerequisites
Write-Host '✅ Checking prerequisites...' -ForegroundColor Green

# Check Python
if (-not (Test-CommandExists python)) {
    Write-Host '❌ Python not found. Please install Python 3.10 or newer.' -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version
Write-Host "   Found: $pythonVersion" -ForegroundColor Gray

# Check Node.js
if (-not (Test-CommandExists node)) {
    Write-Host '❌ Node.js not found. Please install Node.js 18 or newer.' -ForegroundColor Red
    exit 1
}

$nodeVersion = node --version
Write-Host "   Found: Node.js $nodeVersion" -ForegroundColor Gray

# Check npm
if (-not (Test-CommandExists npm)) {
    Write-Host '❌ npm not found. Please install npm.' -ForegroundColor Red
    exit 1
}

$npmVersion = npm --version
Write-Host "   Found: npm $npmVersion" -ForegroundColor Gray

# Setup Python virtual environment
Write-Host '🐍 Setting up Python virtual environment...' -ForegroundColor Green

if (-not (Test-Path 'venv')) {
    Write-Host '   Creating new virtual environment...' -ForegroundColor Gray
    python -m venv venv
} else {
    Write-Host '   Virtual environment already exists.' -ForegroundColor Gray
}

# Activate virtual environment
Write-Host '   Activating virtual environment...' -ForegroundColor Gray
& 'venv\Scripts\activate.ps1'

# Install Python dependencies
Write-Host '📦 Installing Python dependencies...' -ForegroundColor Green
if (Test-Path 'requirements.txt') {
    pip install -r requirements.txt
} else {
    Write-Host '   requirements.txt not found. Installing core packages...' -ForegroundColor Yellow
    pip install fastapi uvicorn sqlalchemy playwright python-dotenv
}

# Install Playwright browsers
Write-Host '🌐 Installing Playwright browser...' -ForegroundColor Green
try {
    python -m playwright install chromium
} catch {
    Write-Host '   Failed to install Playwright browsers. You may need to install them manually.' -ForegroundColor Yellow
    Write-Host '   Run: python -m playwright install chromium' -ForegroundColor Yellow
}

# Setup frontend
Write-Host '🖥️ Setting up frontend...' -ForegroundColor Green
Push-Location frontend
try {
    Write-Host '   Installing npm packages...' -ForegroundColor Gray
    npm install
    
    # Build frontend assets if needed
    # Write-Host '   Building frontend assets...' -ForegroundColor Gray
    # npm run build
} catch {
    Write-Host '❌ Error installing frontend dependencies. See error above.' -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

# Initialize database if needed
Write-Host '🗃️ Setting up database...' -ForegroundColor Green
Push-Location backend
try {
    # Create directories if they don't exist
    if (-not (Test-Path 'debug_screenshots')) {
        mkdir debug_screenshots | Out-Null
    }
    
    # Run database setup or migration script if it exists
    if (Test-Path 'setup_db.py') {
        Write-Host '   Initializing database...' -ForegroundColor Gray
        python setup_db.py
    } else {
        Write-Host '   No database setup script found. Database will be created on first run.' -ForegroundColor Yellow
    }
} catch {
    Write-Host '❌ Error setting up database. See error above.' -ForegroundColor Red
} finally {
    Pop-Location
}

Write-Host '✨ Setup complete! ✨' -ForegroundColor Cyan
Write-Host ''
Write-Host 'To start the backend server:' -ForegroundColor Green
Write-Host '1. cd backend' -ForegroundColor Yellow
Write-Host '2. ..\venv\Scripts\activate' -ForegroundColor Yellow 
Write-Host '3. python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000' -ForegroundColor Yellow
Write-Host ''
Write-Host 'To start the frontend development server:' -ForegroundColor Green
Write-Host '1. cd frontend' -ForegroundColor Yellow
Write-Host '2. npm run dev' -ForegroundColor Yellow
Write-Host ''
Write-Host 'API Documentation will be available at:' -ForegroundColor Green
Write-Host 'http://localhost:8000/docs' -ForegroundColor Yellow