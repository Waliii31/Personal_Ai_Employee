@echo off
REM Startup script for AI Employee File System Watcher (Windows)

echo ===================================
echo AI Employee - File System Watcher
echo ===================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set VAULT_PATH=%SCRIPT_DIR%AI_Employee_Vault

echo Vault location: %VAULT_PATH%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed
    pause
    exit /b 1
)

REM Check if watchdog is installed
python -c "import watchdog" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Starting File System Watcher...
echo Monitoring: %VAULT_PATH%\Inbox
echo.
echo Drop files into the Inbox folder to create tasks.
echo Press Ctrl+C to stop.
echo.

REM Start the watcher
cd /d "%SCRIPT_DIR%watchers"
python filesystem_watcher.py "%VAULT_PATH%"

pause
