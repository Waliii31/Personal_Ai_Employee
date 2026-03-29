#!/bin/bash

# Cloud Deployment Script for AI Employee Platinum Tier
# This script sets up the AI Employee system on a cloud VM (tested on Oracle Cloud Free Tier)

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/opt/ai-employee"
LOG_FILE="/var/log/ai-employee-deploy.log"
SERVICE_NAME="ai-employee"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]$(date '+%Y-%m-%d %H:%M:%S')${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]$(date '+%Y-%m-%d %H:%M:%S')${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]$(date '+%Y-%m-%d %H:%M:%S')${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log "Running as root - good!"
    else
        error "This script must be run as root. Use sudo."
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    log "Installing system dependencies..."

    # Detect OS
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y python3 python3-pip nodejs npm git curl wget unzip
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS
        yum update -y
        yum install -y python3 python3-pip nodejs npm git curl wget unzip
    else
        error "Unsupported OS. Please install dependencies manually."
        exit 1
    fi

    # Install Playwright dependencies (for WhatsApp watcher)
    if command -v apt-get &> /dev/null; then
        apt-get install -y chromium-browser
    elif command -v yum &> /dev/null; then
        yum install -y chromium
    fi

    log "System dependencies installed."
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."

    pip3 install --upgrade pip
    pip3 install -r "$PROJECT_DIR/requirements.txt"

    # Install Playwright and browsers
    python3 -m playwright install chromium

    log "Python dependencies installed."
}

# Install Node.js dependencies
install_node_deps() {
    log "Installing Node.js dependencies..."

    cd "$PROJECT_DIR"
    npm install -g pm2  # Process manager for keeping services running

    # Install MCP server dependencies if they exist
    for mcp_dir in mcp-servers/*/; do
        if [ -d "$mcp_dir" ] && [ -f "$mcp_dir/package.json" ]; then
            log "Installing dependencies for $mcp_dir"
            cd "$mcp_dir"
            npm install
            cd "$PROJECT_DIR"
        fi
    done

    log "Node.js dependencies installed."
}

# Create project directory and copy files
setup_project() {
    log "Setting up project directory..."

    # Create project directory if it doesn't exist
    mkdir -p "$PROJECT_DIR"

    # Copy all Platinum tier files to the project directory
    # (Assuming we're running from the Platinum directory)
    rsync -av --exclude='deploy_cloud.sh' --exclude='*.log' . "$PROJECT_DIR/"

    # Set proper ownership
    chown -R $(whoami):$(whoami) "$PROJECT_DIR"

    log "Project directory set up at $PROJECT_DIR"
}

# Configure environment
configure_environment() {
    log "Configuring environment..."

    cd "$PROJECT_DIR"

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warn ".env file not found. Please create one based on .env.example with your credentials."
        warn "Example: cp .env.example .env && nano .env"
    else
        # Source environment variables
        export $(grep -v '^#' .env | xargs)
        log "Environment variables loaded from .env"
    fi

    # Create vault directories if they don't exist
    mkdir -p vault/{Needs_Action,Done,Pending_Approval,Approved,Rejected,In_Progress,Plans,Logs,Briefings,Accounting,Updates}

    log "Environment configured."
}

# Set up PM2 for process management
setup_pm2() {
    log "Setting up PM2 for process management..."

    cd "$PROJECT_DIR"

    # Start the orchestrator and watchers with PM2
    pm2 start orchestrator.py --name "ai-employee-orchestrator" --interpreter python3 -- --vault ./vault
    pm2 start watchers/gmail_watcher.py --name "gmail-watcher" --interpreter python3 -- --vault ./vault --interval 120
    pm2 start watchers/whatsapp_watcher.py --name "whatsapp-watcher" --interpreter python3 -- --vault ./vault --interval 30
    pm2 start watchers/finance_watcher.py --name "finance-watcher" --interpreter python3 -- --vault ./vault --interval 300
    pm2 start watchers/filesystem_watcher.py --name "filesystem-watcher" --interpreter python3 -- --vault ./vault --watch-dirs ./watched_dirs --interval 30

    # Save the PM2 configuration
    pm2 save

    # Set PM2 to start on boot
    pm2 startup

    log "PM2 processes started and configured for auto-start."
    log "View process status with: pm2 status"
    log "View logs with: pm2 logs"
}

# Create systemd service (alternative to PM2)
create_systemd_service() {
    log "Creating systemd service..."

    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=AI Employee Orchestrator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=/usr/bin/python3 $PROJECT_DIR/orchestrator.py --vault $PROJECT_DIR/vault
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable the service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    # Don't start yet, as PM2 is preferred

    log "Systemd service created at $SERVICE_FILE"
}

# Security hardening
security_hardening() {
    log "Applying security hardening..."

    # Create a dedicated user for the AI employee (optional but recommended)
    if ! id "ai-employee" &>/dev/null; then
        useradd -r -s /bin/false ai-employee
        chown -R ai-employee:ai-employee "$PROJECT_DIR"
        log "Created dedicated user 'ai-employee'"
    fi

    # Set secure permissions
    chmod 750 "$PROJECT_DIR"
    chmod 600 "$PROJECT_DIR/.env" 2>/dev/null || true
    chmod 600 "$PROJECT_DIR/vault/gmail_credentials.json" 2>/dev/null || true

    log "Security hardening applied."
}

# Health check function
health_check() {
    log "Performing health check..."

    # Check if PM2 processes are running
    if command -v pm2 &> /dev/null; then
        pm2_status=$(pm2 jlist)
        if echo "$pm2_status" | grep -q '"pm2_env":{"status":"online"'; then
            log "✅ PM2 processes are running"
        else
            warn "⚠️ Some PM2 processes may not be running. Check with: pm2 status"
        fi
    else
        warn "PM2 not found. Please install and configure it manually."
    fi

    # Check if required directories exist
    required_dirs=("Needs_Action" "Done" "Pending_Approval" "Approved" "Rejected" "In_Progress" "Plans" "Logs")
    for dir in "${required_dirs[@]}"; do
        if [ -d "vault/$dir" ]; then
            log "✅ Vault directory $dir exists"
        else
            warn "⚠️ Vault directory vault/$dir missing"
        fi
    done
}

# Display completion message
show_completion_message() {
    log ""
    log "==========================================="
    log "🎉 AI EMPLOYEE PLATINUM TIER DEPLOYMENT COMPLETE! 🎉"
    log "==========================================="
    log ""
    log "Your AI Employee is now deployed and running!"
    log ""
    log "📊 MONITORING:"
    log "  View process status: pm2 status"
    log "  View logs: pm2 logs (or pm2 logs <app-name> for specific app)"
    log "  Monitor with: pm2 monit"
    log ""
    log "🔄 MANAGEMENT:"
    log "  Restart all: pm2 restart all"
    log "  Stop all: pm2 stop all"
    log "  Delete all: pm2 delete all"
    log ""
    log "📁 VAULT LOCATION: $PROJECT_DIR/vault"
    log "   - Needs Action: $PROJECT_DIR/vault/Needs_Action"
    log "   - Pending Approval: $PROJECT_DIR/vault/Pending_Approval"
    log "   - Completed: $PROJECT_DIR/vault/Done"
    log ""
    log "🔧 CONFIGURATION FILES:"
    log "   - Main config: $PROJECT_DIR/claude_config.json"
    log "   - MCP config: $PROJECT_DIR/mcp-config.json"
    log "   - Environment: $PROJECT_DIR/.env"
    log ""
    log "🔐 SECURITY:"
    log "   - Ensure your .env file contains proper credentials"
    log "   - Review firewall settings to restrict access as needed"
    log "   - Monitor logs regularly for any suspicious activity"
    log ""
    log "📈 NEXT STEPS:"
    log "   1. Configure your Gmail API credentials"
    log "   2. Set up your Odoo ERP integration (if needed)"
    log "   3. Review and customize Company_Handbook.md for your rules"
    log "   4. Test the system with sample tasks"
    log "   5. Set up monitoring and alerts"
    log ""
    log "For troubleshooting, check logs at: $LOG_FILE and PM2 logs"
    log "==========================================="
}

# Main execution
main() {
    log "Starting AI Employee Platinum Tier cloud deployment..."

    check_root
    setup_project
    install_system_deps
    configure_environment
    install_python_deps
    install_node_deps
    security_hardening
    setup_pm2
    create_systemd_service
    health_check
    show_completion_message

    log "Deployment script completed successfully!"
}

# Run main function
main "$@"