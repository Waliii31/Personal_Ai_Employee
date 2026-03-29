@echo off
REM Local Setup Script for AI Employee Platinum Tier on Windows

setlocal enabledelayedexpansion

echo ========================================================
echo    AI Employee Platinum Tier - Local Setup
echo ========================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: This script must be run as Administrator
    echo Right-click on this file and select "Run as administrator"
    pause
    exit /b 1
)

REM Configuration
set PROJECT_DIR=%~dp0
set LOG_FILE=%PROJECT_DIR%setup_local.log
set PYTHON_CMD=python
set PIP_CMD=pip

echo Starting AI Employee Platinum Tier local setup...
echo Project Directory: %PROJECT_DIR%
echo.

REM Function to log messages
echo [%date% %time%] Starting local setup... >> "%LOG_FILE%"

REM Check if Python is installed
echo Checking Python installation...
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.13+ and ensure it's in your PATH
    echo Log file: %LOG_FILE%
    pause
    exit /b 1
)
echo Python version:
%PYTHON_CMD% --version
echo [%date% %time%] Python found: && %PYTHON_CMD% --version >> "%LOG_FILE%"

REM Check if pip is installed
echo Checking pip installation...
%PIP_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed or not in PATH
    echo Please ensure pip is available with Python installation
    echo Log file: %LOG_FILE%
    pause
    exit /b 1
)
echo [%date% %time%] Pip found >> "%LOG_FILE%"

REM Install Python dependencies
echo Installing Python dependencies from requirements.txt...
%PIP_CMD% install --upgrade pip >> "%LOG_FILE%" 2>&1
%PIP_CMD% install -r "%PROJECT_DIR%requirements.txt" >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    echo Check the log file: %LOG_FILE%
    pause
    exit /b 1
)
echo [%date% %time%] Python dependencies installed >> "%LOG_FILE%"

REM Install Playwright browsers
echo Installing Playwright browsers...
%PYTHON_CMD% -m playwright install chromium >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo Warning: Failed to install Playwright browsers
    echo This may affect the WhatsApp watcher functionality
    echo [%date% %time%] Playwright install failed >> "%LOG_FILE%"
) else (
    echo [%date% %time%] Playwright browsers installed >> "%LOG_FILE%"
)

REM Create vault directories
echo Creating vault directory structure...
if not exist "%PROJECT_DIR%vault" mkdir "%PROJECT_DIR%vault"
if not exist "%PROJECT_DIR%vault\Needs_Action" mkdir "%PROJECT_DIR%vault\Needs_Action"
if not exist "%PROJECT_DIR%vault\Done" mkdir "%PROJECT_DIR%vault\Done"
if not exist "%PROJECT_DIR%vault\Pending_Approval" mkdir "%PROJECT_DIR%vault\Pending_Approval"
if not exist "%PROJECT_DIR%vault\Approved" mkdir "%PROJECT_DIR%vault\Approved"
if not exist "%PROJECT_DIR%vault\Rejected" mkdir "%PROJECT_DIR%vault\Rejected"
if not exist "%PROJECT_DIR%vault\In_Progress" mkdir "%PROJECT_DIR%vault\In_Progress"
if not exist "%PROJECT_DIR%vault\Plans" mkdir "%PROJECT_DIR%vault\Plans"
if not exist "%PROJECT_DIR%vault\Logs" mkdir "%PROJECT_DIR%vault\Logs"
if not exist "%PROJECT_DIR%vault\Briefings" mkdir "%PROJECT_DIR%vault\Briefings"
if not exist "%PROJECT_DIR%vault\Accounting" mkdir "%PROJECT_DIR%vault\Accounting"
if not exist "%PROJECT_DIR%vault\Updates" mkdir "%PROJECT_DIR%vault\Updates"

echo [%date% %time%] Vault directories created >> "%LOG_FILE%"

REM Check for Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Node.js is not installed or not in PATH
    echo MCP servers and some features will not work without Node.js
    echo Please install Node.js v24+ LTS from https://nodejs.org/
    echo [%date% %time%] Node.js not found >> "%LOG_FILE%"
) else (
    echo Node.js version:
    node --version
    echo [%date% %time%] Node.js found >> "%LOG_FILE%"

    REM Install PM2 globally
    echo Installing PM2 process manager...
    npm install -g pm2 >> "%LOG_FILE%" 2>&1
    if %errorlevel% neq 0 (
        echo Warning: Failed to install PM2
        echo [%date% %time%] PM2 install failed >> "%LOG_FILE%"
    ) else (
        echo [%date% %time%] PM2 installed >> "%LOG_FILE%"
    )
)

REM Create example .env file if it doesn't exist
if not exist "%PROJECT_DIR%.env" (
    echo Creating example .env file...
    echo Copying .env.example to .env
    copy "%PROJECT_DIR%.env.example" "%PROJECT_DIR%.env" >nul 2>&1
    if %errorlevel% eq 0 (
        echo [%date% %time%] Created .env file >> "%LOG_FILE%"
    ) else (
        REM Create a minimal .env if example doesn't exist
        echo DEV_MODE=true>"%PROJECT_DIR%.env"
        echo DRY_RUN=true>>"%PROJECT_DIR%.env"
        echo [%date% %time%] Created minimal .env file >> "%LOG_FILE%"
    )
)

REM Create MCP server directories
echo Setting up MCP server placeholders...
if not exist "%PROJECT_DIR%mcp-servers" mkdir "%PROJECT_DIR%mcp-servers"
if not exist "%PROJECT_DIR%mcp-servers\email-mcp" mkdir "%PROJECT_DIR%mcp-servers\email-mcp"
if not exist "%PROJECT_DIR%mcp-servers\browser-mcp" mkdir "%PROJECT_DIR%mcp-servers\browser-mcp"
if not exist "%PROJECT_DIR%mcp-servers\filesystem-mcp" mkdir "%PROJECT_DIR%mcp-servers\filesystem-mcp"

REM Create placeholder package.json files
echo {"name": "email-mcp", "version": "1.0.0", "description": "Email MCP Server"} > "%PROJECT_DIR%mcp-servers\email-mcp\package.json"
echo {"name": "browser-mcp", "version": "1.0.0", "description": "Browser MCP Server"} > "%PROJECT_DIR%mcp-servers\browser-mcp\package.json"
echo {"name": "filesystem-mcp", "version": "1.0.0", "description": "Filesystem MCP Server"} > "%PROJECT_DIR%mcp-servers\filesystem-mcp\package.json"

echo [%date% %time%] MCP servers setup >> "%LOG_FILE%"

REM Final status check
echo.
echo Checking setup status...

REM Verify Python modules
echo Verifying Python modules...
%PYTHON_CMD% -c "import requests, googleapiclient, playwright" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo [%date% %time%] Python modules verified successfully >> "%LOG_FILE%"
    set PYTHON_OK=1
) else (
    echo [%date% %time%] Some Python modules missing >> "%LOG_FILE%"
    set PYTHON_OK=0
)

REM Verify directories
set DIRS_OK=1
for %%d in ("Needs_Action", "Done", "Pending_Approval", "Approved", "Rejected", "In_Progress", "Plans", "Logs") do (
    if not exist "%PROJECT_DIR%vault\%%d" (
        echo Missing vault directory: %%d
        set DIRS_OK=0
    )
)

echo [%date% %time%] Directory check completed >> "%LOG_FILE%"

REM Completion message
echo.
echo ========================================================
echo    SETUP COMPLETED
echo ========================================================
echo.
echo Status:
echo - Python modules: %PYTHON_OK% (1=OK, 0=Missing)
echo - Vault directories: %DIRS_OK% (1=OK, 0=Missing)
echo - Log file: %LOG_FILE%
echo.
echo NEXT STEPS:
echo 1. Edit %PROJECT_DIR%.env with your credentials
echo 2. Configure Gmail API credentials if needed
echo 3. Install Node.js if you plan to use MCP servers
echo 4. Run the orchestrator: python orchestrator.py --vault ./vault
echo.
echo To start the AI Employee:
echo   python orchestrator.py --vault ./vault
echo.
echo To run individual watchers:
echo   python watchers\gmail_watcher.py --vault ./vault
echo   python watchers\whatsapp_watcher.py --vault ./vault
echo   python watchers\finance_watcher.py --vault ./vault
echo   python watchers\filesystem_watcher.py --vault ./vault --watch-dirs C:\Downloads
echo ========================================================
echo.

echo [%date% %time%] Setup completed >> "%LOG_FILE%"
pause