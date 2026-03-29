#!/usr/bin/env python3
"""
Setup script for the AI Employee Platinum tier system
This script will install dependencies, configure the environment, and prepare the system for operation
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def install_python_dependencies():
    """Install required Python packages"""
    logger.info("Installing Python dependencies...")

    try:
        # Install packages from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Python dependencies: {e}")
        return False

    # Install playwright separately as it requires additional setup
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])
        logger.info("Playwright installed and browsers downloaded successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Playwright: {e}")
        return False

    return True


def create_directories():
    """Create necessary directories for the AI Employee system"""
    logger.info("Creating directory structure...")

    directories = [
        "watchers",
        "mcp-servers",
        "skills",
        "vault/Needs_Action",
        "vault/Done",
        "vault/Pending_Approval",
        "vault/Approved",
        "vault/Rejected",
        "vault/In_Progress",
        "vault/Plans",
        "vault/Logs",
        "vault/Briefings",
        "vault/Accounting",
        "vault/Updates"
    ]

    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

    return True


def create_sample_env_file():
    """Create a sample .env file with environment variables"""
    logger.info("Creating sample .env file...")

    env_content = """# AI Employee Environment Variables
# Copy this file to .env and fill in your actual values

# Gmail API Configuration
GMAIL_CLIENT_ID=your_gmail_client_id_here
GMAIL_CLIENT_SECRET=your_gmail_client_secret_here
GMAIL_API_KEY=your_gmail_api_key_here

# Bank API Configuration (example)
BANK_API_URL=https://api.yourbank.com
BANK_API_KEY=your_bank_api_key_here
BANK_ACCOUNT_ID=your_account_id_here

# Claude Code Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# Cloud Deployment Configuration
CLOUD_VM_HOST=your_cloud_vm_host
CLOUD_VM_USER=your_username
CLOUD_VM_KEY_PATH=path/to/your/private/key

# Odoo ERP Configuration
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Security Settings
DEV_MODE=true  # Set to false for production
DRY_RUN=true   # Set to false to allow actual actions
"""

    with open(".env.example", "w") as f:
        f.write(env_content)

    logger.info("Sample .env file created as .env.example")
    logger.info("Please copy this to .env and add your actual credentials")


def create_gitignore():
    """Create a comprehensive .gitignore file"""
    logger.info("Creating .gitignore file...")

    gitignore_content = """# Dependencies
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
.venv/
env.bak/
venv.bak/

# Virtual environments
.venv/
.envrc
.env.local
.env.staging
.env.production

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
Icon?
.dsb

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.example

# Secrets
*.key
*.pem
*.crt
*.cert
secrets/
tokens/
keys/

# Database
*.db
*.sqlite
*.sqlite3

# Build outputs
dist/
build/
*.egg-info/
coverage/

# Temporary files
/tmp/
temp/
*.tmp
*.temp

# Vault sync exclusion (except markdown files)
# Exclude everything in vault except .md files
vault/*
!vault/*.md
!vault/**/*.md

# But exclude sensitive vault files
vault/.env
vault/tokens/
vault/secrets/
vault/whatsapp_session/

# Process IDs
*.pid
/tmp/
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)

    logger.info(".gitignore file created")


def create_systemd_service():
    """Create a systemd service file for Linux systems"""
    logger.info("Creating systemd service file...")

    service_content = """[Unit]
Description=AI Employee Orchestrator
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory=/path/to/ai-employee
EnvironmentFile=/path/to/ai-employee/.env
ExecStart=/usr/bin/python3 /path/to/ai-employee/orchestrator.py --vault /path/to/ai-employee/vault
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    # Write to a template file that needs to be customized
    with open("ai-employee.service.template", "w") as f:
        f.write(service_content)

    logger.info("Systemd service template created as ai-employee.service.template")
    logger.info("Customize this file with your paths and copy to /etc/systemd/system/")


def create_pm2_ecosystem():
    """Create a PM2 ecosystem file for process management"""
    logger.info("Creating PM2 ecosystem file...")

    ecosystem_content = """module.exports = {
  apps: [{
    name: 'ai-employee-orchestrator',
    script: './orchestrator.py',
    interpreter: 'python3',
    args: '--vault ./vault',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      VAULT_PATH: './vault'
    }
  }, {
    name: 'gmail-watcher',
    script: './watchers/gmail_watcher.py',
    interpreter: 'python3',
    args: '--vault ./vault --interval 120',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '512M'
  }, {
    name: 'whatsapp-watcher',
    script: './watchers/whatsapp_watcher.py',
    interpreter: 'python3',
    args: '--vault ./vault --interval 30',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '512M'
  }]
};
"""

    with open("ecosystem.config.js", "w") as f:
        f.write(ecosystem_content)

    logger.info("PM2 ecosystem file created as ecosystem.config.js")


def setup_mcp_servers():
    """Setup placeholder MCP servers"""
    logger.info("Setting up MCP server placeholders...")

    # Create MCP servers directory structure
    mcp_dirs = [
        "mcp-servers/email-mcp",
        "mcp-servers/browser-mcp",
        "mcp-servers/filesystem-mcp"
    ]

    for mcp_dir in mcp_dirs:
        Path(mcp_dir).mkdir(parents=True, exist_ok=True)

    # Create placeholder files
    email_mcp_content = """// Email MCP Server
// Placeholder for email operations

const express = require('express');
const app = express();

app.use(express.json());

// Send email capability
app.post('/send-email', (req, res) => {
  const { to, subject, body } = req.body;

  // Implementation would go here
  console.log(`Would send email to: ${to}, subject: ${subject}`);

  res.json({ success: true, message: 'Email sent' });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Email MCP server running on port ${PORT}`);
});
"""

    with open("mcp-servers/email-mcp/index.js", "w") as f:
        f.write(email_mcp_content)

    logger.info("Placeholder MCP servers created")


def main():
    parser = argparse.ArgumentParser(description='Setup AI Employee Platinum tier system')
    parser.add_argument('--skip-dependencies', action='store_true',
                       help='Skip installing Python dependencies')
    parser.add_argument('--skip-vault', action='store_true',
                       help='Skip creating vault directories')

    args = parser.parse_args()

    logger.info("Starting AI Employee Platinum tier setup...")

    # Create directories
    if not args.skip_vault:
        if not create_directories():
            logger.error("Failed to create directories")
            return 1

    # Install dependencies
    if not args.skip_dependencies:
        if not install_python_dependencies():
            logger.error("Failed to install dependencies")
            return 1

    # Create configuration files
    create_sample_env_file()
    create_gitignore()
    create_systemd_service()
    create_pm2_ecosystem()
    setup_mcp_servers()

    logger.info("")
    logger.info("="*60)
    logger.info("AI Employee Platinum tier setup completed!")
    logger.info("="*60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Copy .env.example to .env and add your credentials")
    logger.info("2. Configure your MCP servers in the mcp-servers directory")
    logger.info("3. Set up your Gmail API credentials")
    logger.info("4. Run the orchestrator with: python orchestrator.py --vault ./vault")
    logger.info("")
    logger.info("For cloud deployment:")
    logger.info("- Use the systemd service file for Linux systems")
    logger.info("- Use the PM2 ecosystem file for process management")
    logger.info("- Configure your cloud VM with the necessary credentials")
    logger.info("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())