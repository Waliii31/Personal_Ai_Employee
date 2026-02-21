#!/bin/bash
# Startup script for AI Employee File System Watcher

echo "==================================="
echo "AI Employee - File System Watcher"
echo "==================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_PATH="$SCRIPT_DIR/AI_Employee_Vault"

echo "Vault location: $VAULT_PATH"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if watchdog is installed
if ! python3 -c "import watchdog" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Starting File System Watcher..."
echo "Monitoring: $VAULT_PATH/Inbox"
echo ""
echo "Drop files into the Inbox folder to create tasks."
echo "Press Ctrl+C to stop."
echo ""

# Start the watcher
cd "$SCRIPT_DIR/watchers"
python3 filesystem_watcher.py "$VAULT_PATH"
