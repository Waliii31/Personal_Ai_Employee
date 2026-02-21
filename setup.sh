#!/bin/bash
# Setup script for Personal AI Employee project
# Run this after cloning the repository

set -e  # Exit on error

echo "=================================="
echo "Personal AI Employee Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3.13+ required but not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js v24+ required but not found"
    exit 1
fi

# Check Claude Code
if command -v claude &> /dev/null; then
    echo -e "${GREEN}✓${NC} Claude Code found"
else
    echo -e "${YELLOW}⚠${NC} Claude Code not found. Install with: npm install -g @anthropic/claude-code"
fi

# Check Git
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git found"
else
    echo -e "${RED}✗${NC} Git required but not found"
    exit 1
fi

echo ""
echo "Setting up environment..."

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from template"
    echo -e "${YELLOW}⚠${NC} Please edit .env with your actual credentials"
else
    echo -e "${YELLOW}⚠${NC} .env already exists, skipping"
fi

# Install Python dependencies for Bronze tier
echo ""
echo "Installing Bronze tier dependencies..."
cd Bronze

if command -v uv &> /dev/null; then
    echo "Using UV for faster installation..."
    uv pip install -r requirements.txt
else
    echo "Using pip..."
    pip install -r requirements.txt
fi

echo -e "${GREEN}✓${NC} Bronze tier dependencies installed"

cd ..

# Create necessary directories
echo ""
echo "Creating directory structure..."

mkdir -p Bronze/AI_Employee_Vault/{Inbox,Needs_Action,Plans,Pending_Approval,Approved,Rejected,Done,Logs}
mkdir -p Silver/{vault,watchers,mcp-servers,skills}
mkdir -p Gold/{vault,watchers,mcp-servers,odoo-integration,skills}
mkdir -p Platinum/{cloud-deployment,local-agent,sync-architecture}
mkdir -p docs/{architecture,guides,examples}

echo -e "${GREEN}✓${NC} Directory structure created"

# Initialize git if not already initialized
if [ ! -d .git ]; then
    echo ""
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Personal AI Employee project setup"
    echo -e "${GREEN}✓${NC} Git repository initialized"
else
    echo -e "${YELLOW}⚠${NC} Git repository already initialized"
fi

# Create initial log file
LOG_FILE="Bronze/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Setup completed" > "$LOG_FILE"
echo -e "${GREEN}✓${NC} Initial log file created"

# Summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Open Bronze/AI_Employee_Vault in Obsidian"
echo "3. Test the filesystem watcher:"
echo "   cd Bronze/watchers && python filesystem_watcher.py"
echo "4. Read QUICKSTART.md for detailed instructions"
echo ""
echo "Join the community:"
echo "- Wednesday meetings at 10:00 PM"
echo "- Zoom: https://us06web.zoom.us/j/87188707642"
echo ""
echo -e "${GREEN}Happy building!${NC}"
