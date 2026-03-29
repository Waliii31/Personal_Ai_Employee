#!/bin/bash
# Linux/Mac Cron Setup Script for AI Employee

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_PATH="$SCRIPT_DIR/vault"
PYTHON_PATH="python3"

echo "========================================"
echo "AI Employee - Cron Setup"
echo "========================================"
echo ""
echo "Script Directory: $SCRIPT_DIR"
echo "Vault Path: $VAULT_PATH"
echo ""

# Create cron entries
CRON_ENTRIES="
# AI Employee - Daily Briefing (8 AM every day)
0 8 * * * cd $SCRIPT_DIR && $PYTHON_PATH orchestrator.py $VAULT_PATH --briefing >> $VAULT_PATH/Logs/cron.log 2>&1

# AI Employee - LinkedIn Content (9 AM every Monday)
0 9 * * 1 cd $SCRIPT_DIR && $PYTHON_PATH watchers/linkedin_automation.py $VAULT_PATH >> $VAULT_PATH/Logs/cron.log 2>&1

# AI Employee - Health Check (every 30 minutes)
*/30 * * * * cd $SCRIPT_DIR && $PYTHON_PATH orchestrator.py $VAULT_PATH --test >> $VAULT_PATH/Logs/cron.log 2>&1
"

echo "Cron entries to be added:"
echo "$CRON_ENTRIES"
echo ""

# Backup existing crontab
echo "Backing up existing crontab..."
crontab -l > "$SCRIPT_DIR/crontab.backup" 2>/dev/null || echo "No existing crontab"

# Add new entries
echo "Adding AI Employee cron entries..."
(crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -

if [ $? -eq 0 ]; then
    echo "[OK] Cron entries added successfully"
else
    echo "[ERROR] Failed to add cron entries"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Scheduled Tasks:"
echo "1. Daily Briefing - Every day at 8:00 AM"
echo "2. LinkedIn Content - Every Monday at 9:00 AM"
echo "3. Health Check - Every 30 minutes"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove AI Employee jobs: crontab -e (then delete the entries)"
echo ""
echo "Note: Watchers should be run as services"
echo "Use: python3 orchestrator.py $VAULT_PATH"
echo ""
