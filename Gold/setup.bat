@echo off
REM Gold Tier Setup Script for Windows
REM Automates the initial setup process

echo ==========================================
echo Gold Tier Setup Script
echo ==========================================
echo.

REM Check prerequisites
echo [1/7] Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    exit /b 1
)

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop
    exit /b 1
)

echo [OK] All prerequisites found
echo.

REM Install Python dependencies
echo [2/7] Installing Python dependencies...
pip install -r requirements.txt
echo [OK] Python dependencies installed
echo.

REM Install Odoo MCP dependencies
echo [3/7] Installing Odoo MCP dependencies...
cd mcp-servers\odoo-mcp
call npm install
cd ..\..
echo [OK] Odoo MCP dependencies installed
echo.

REM Install Social Media MCP dependencies
echo [4/7] Installing Social Media MCP dependencies...
cd mcp-servers\social-media-mcp
call npm install
cd ..\..
echo [OK] Social Media MCP dependencies installed
echo.

REM Initialize vault
echo [5/7] Initializing vault structure...
python init_vault.py
echo [OK] Vault initialized
echo.

REM Create .env from example
echo [6/7] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo [OK] .env created from template
    echo [ACTION REQUIRED] Edit .env with your credentials
) else (
    echo [SKIP] .env already exists
)
echo.

REM Validate setup
echo [7/7] Validating setup...
python validate_setup.py
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env with your credentials
echo 2. Start Odoo: cd odoo-integration ^&^& docker-compose up -d
echo 3. Configure Odoo at http://localhost:8069
echo 4. Follow QUICKSTART.md for detailed instructions
echo.

pause
