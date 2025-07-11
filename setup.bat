@echo off
REM Smart Code Tutor Setup Script for Windows
echo 🚀 Smart Code Tutor Setup Script (Windows)
echo =======================================

set "command=%1"
if "%command%"=="" set "command=setup"

if "%command%"=="setup" goto :setup
if "%command%"=="start" goto :start
if "%command%"=="backend" goto :backend
if "%command%"=="frontend" goto :frontend
if "%command%"=="clean" goto :clean
if "%command%"=="help" goto :help
goto :unknown

:setup
echo [INFO] Checking requirements...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is required but not installed
    exit /b 1
)
echo [SUCCESS] Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is required but not installed
    exit /b 1
)
echo [SUCCESS] Node.js found

REM Check pnpm
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pnpm not found. Installing...
    npm install -g pnpm
)
echo [SUCCESS] pnpm found

echo [INFO] Installing root dependencies...
pnpm install

echo [INFO] Setting up backend...
cd backend
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if exist "requirements-minimal.txt" (
    python -m pip install -r requirements-minimal.txt
) else (
    python -m pip install -r requirements.txt
)
if not exist ".env" (
    copy .env.example .env
    echo [WARNING] Please update .env file with your API keys
)
cd ..

echo [INFO] Setting up frontend...
cd frontend
pnpm install
cd ..

echo [SUCCESS] Setup completed successfully!
echo.
echo To start the application, run:
echo   setup.bat start
goto :end

:start
echo [INFO] Starting Smart Code Tutor...
pnpm dev
goto :end

:backend
echo [INFO] Starting backend only...
cd backend
call venv\Scripts\activate.bat
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
goto :end

:frontend
echo [INFO] Starting frontend only...
cd frontend
pnpm dev
goto :end

:clean
echo [INFO] Cleaning up...
rmdir /s /q backend\venv 2>nul
rmdir /s /q frontend\node_modules 2>nul
rmdir /s /q node_modules 2>nul
rmdir /s /q backend\__pycache__ 2>nul
echo [SUCCESS] Cleanup completed
goto :end

:help
echo Smart Code Tutor Setup Script (Windows)
echo.
echo Usage: setup.bat [command]
echo.
echo Commands:
echo   setup     - Full setup (default)
echo   start     - Start the application
echo   backend   - Start backend only
echo   frontend  - Start frontend only
echo   clean     - Clean all dependencies
echo   help      - Show this help
goto :end

:unknown
echo [ERROR] Unknown command: %command%
echo Run 'setup.bat help' for available commands
exit /b 1

:end 