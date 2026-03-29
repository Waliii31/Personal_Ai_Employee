@echo off
REM Windows Task Scheduler Setup Script for AI Employee
REM Run this script as Administrator

echo ========================================
echo AI Employee - Windows Scheduler Setup
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set VAULT_PATH=%SCRIPT_DIR%vault
set PYTHON_PATH=python

echo Script Directory: %SCRIPT_DIR%
echo Vault Path: %VAULT_PATH%
echo.

REM Create daily briefing task
echo Creating daily briefing task...
schtasks /create /tn "AI_Employee_Daily_Briefing" /tr "%PYTHON_PATH% %SCRIPT_DIR%orchestrator.py %VAULT_PATH% --briefing" /sc daily /st 08:00 /f
if %errorlevel% equ 0 (
    echo [OK] Daily briefing task created
) else (
    echo [ERROR] Failed to create daily briefing task
)

REM Create LinkedIn content generation task (weekly on Monday)
echo Creating LinkedIn content generation task...
schtasks /create /tn "AI_Employee_LinkedIn_Weekly" /tr "%PYTHON_PATH% %SCRIPT_DIR%watchers\linkedin_automation.py %VAULT_PATH%" /sc weekly /d MON /st 09:00 /f
if %errorlevel% equ 0 (
    echo [OK] LinkedIn weekly task created
) else (
    echo [ERROR] Failed to create LinkedIn task
)

REM Create health check task (every 30 minutes)
echo Creating health check task...
schtasks /create /tn "AI_Employee_Health_Check" /tr "%PYTHON_PATH% %SCRIPT_DIR%orchestrator.py %VAULT_PATH% --test" /sc minute /mo 30 /f
if %errorlevel% equ 0 (
    echo [OK] Health check task created
) else (
    echo [ERROR] Failed to create health check task
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Scheduled Tasks Created:
echo 1. Daily Briefing - Every day at 8:00 AM
echo 2. LinkedIn Content - Every Monday at 9:00 AM
echo 3. Health Check - Every 30 minutes
echo.
echo To view tasks: schtasks /query /tn "AI_Employee*"
echo To delete tasks: schtasks /delete /tn "AI_Employee*" /f
echo.
echo Note: Watchers should be run manually or as services
echo Use: python orchestrator.py %VAULT_PATH%
echo.
pause
