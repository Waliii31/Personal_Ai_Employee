@echo off
REM Setup script for Personal AI Employee project (Windows)
REM Run this after cloning the repository

echo ==================================
echo Personal AI Employee Setup
echo ==================================
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found
) else (
    echo [ERROR] Python 3.13+ required but not found
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js found
) else (
    echo [ERROR] Node.js v24+ required but not found
    exit /b 1
)

REM Check Claude Code
claude --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Claude Code found
) else (
    echo [WARNING] Claude Code not found. Install with: npm install -g @anthropic/claude-code
)

REM Check Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git found
) else (
    echo [ERROR] Git required but not found
    exit /b 1
)

echo.
echo Setting up environment...

REM Create .env from template if it doesn't exist
if not exist .env (
    copy .env.example .env
    echo [OK] Created .env file from template
    echo [WARNING] Please edit .env with your actual credentials
) else (
    echo [WARNING] .env already exists, skipping
)

REM Install Python dependencies for Bronze tier
echo.
echo Installing Bronze tier dependencies...
cd Bronze

REM Check if UV is available
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using UV for faster installation...
    uv pip install -r requirements.txt
) else (
    echo Using pip...
    pip install -r requirements.txt
)

echo [OK] Bronze tier dependencies installed

cd ..

REM Create necessary directories
echo.
echo Creating directory structure...

mkdir Bronze\AI_Employee_Vault\Inbox 2>nul
mkdir Bronze\AI_Employee_Vault\Needs_Action 2>nul
mkdir Bronze\AI_Employee_Vault\Plans 2>nul
mkdir Bronze\AI_Employee_Vault\Pending_Approval 2>nul
mkdir Bronze\AI_Employee_Vault\Approved 2>nul
mkdir Bronze\AI_Employee_Vault\Rejected 2>nul
mkdir Bronze\AI_Employee_Vault\Done 2>nul
mkdir Bronze\AI_Employee_Vault\Logs 2>nul

mkdir Silver\vault 2>nul
mkdir Silver\watchers 2>nul
mkdir Silver\mcp-servers 2>nul
mkdir Silver\skills 2>nul

mkdir Gold\vault 2>nul
mkdir Gold\watchers 2>nul
mkdir Gold\mcp-servers 2>nul
mkdir Gold\odoo-integration 2>nul
mkdir Gold\skills 2>nul

mkdir Platinum\cloud-deployment 2>nul
mkdir Platinum\local-agent 2>nul
mkdir Platinum\sync-architecture 2>nul

mkdir docs\architecture 2>nul
mkdir docs\guides 2>nul
mkdir docs\examples 2>nul

echo [OK] Directory structure created

REM Initialize git if not already initialized
if not exist .git (
    echo.
    echo Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit: Personal AI Employee project setup"
    echo [OK] Git repository initialized
) else (
    echo [WARNING] Git repository already initialized
)

REM Create initial log file
echo %date% %time% - Setup completed > Bronze\AI_Employee_Vault\Logs\%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.log
echo [OK] Initial log file created

REM Summary
echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env with your credentials
echo 2. Open Bronze\AI_Employee_Vault in Obsidian
echo 3. Test the filesystem watcher:
echo    cd Bronze\watchers ^&^& python filesystem_watcher.py
echo 4. Read QUICKSTART.md for detailed instructions
echo.
echo Join the community:
echo - Wednesday meetings at 10:00 PM
echo - Zoom: https://us06web.zoom.us/j/87188707642
echo.
echo Happy building!
echo.
pause
