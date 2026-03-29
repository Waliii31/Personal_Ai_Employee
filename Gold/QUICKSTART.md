# Gold Tier Quick Start Guide

Get your autonomous business operations running in 30 minutes.

## Prerequisites

- Python 3.8+
- Node.js 18+
- Docker Desktop installed and running
- Git

## Step 1: Install Dependencies (5 minutes)

```bash
cd Gold

# Install Python dependencies
pip install -r requirements.txt

# Install Odoo MCP server dependencies
cd mcp-servers/odoo-mcp
npm install
cd ../..

# Install Social Media MCP server dependencies
cd mcp-servers/social-media-mcp
npm install
cd ../..
```

## Step 2: Start Odoo (10 minutes)

```bash
# Start Odoo containers
cd odoo-integration
docker-compose up -d
cd ..

# Wait 2-3 minutes for Odoo to initialize
# Check status
docker-compose -f odoo-integration/docker-compose.yml ps
```

Open http://localhost:8069 in your browser:

1. **Create Database**
   - Master Password: `admin`
   - Database Name: `odoo`
   - Email: your email
   - Password: choose a strong password
   - Language: English
   - Country: Your country
   - Demo data: Uncheck (for production)

2. **Install Accounting Module**
   - Go to Apps menu
   - Remove "Apps" filter
   - Search for "Accounting"
   - Click Install

3. **Create API User**
   - Settings → Users & Companies → Users
   - Create new user: `API User`
   - Email: `api@localhost`
   - Access Rights: Check "Accounting" and "Administration/Settings"
   - Save and set password

## Step 3: Configure Environment Variables (5 minutes)

```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required for basic functionality:**
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=api@localhost
ODOO_PASSWORD=your_api_user_password
```

**Optional (for social media features):**
- Facebook: Get Page ID and Access Token from Facebook Developer Console
- Instagram: Get Business Account ID and Access Token
- Twitter: Get API credentials from Twitter Developer Portal

## Step 4: Initialize Vault (2 minutes)

```bash
python init_vault.py
```

This creates:
- All necessary directories
- Dashboard.md
- Sample task file
- .gitkeep files

## Step 5: Test Odoo MCP Server (3 minutes)

```bash
cd mcp-servers/odoo-mcp

# Test connection
node -e "
const { OdooClient } = require('./odoo_client.js');
const client = new OdooClient(
  'http://localhost:8069',
  'odoo',
  'api@localhost',
  'wali2005'
);
client.authenticate().then(() => {
  console.log('✓ Odoo connection successful!');
  process.exit(0);
}).catch(err => {
  console.error('✗ Connection failed:', err.message);
  process.exit(1);
});
"

cd ../..
```

## Step 6: Configure Claude Code MCP Settings (5 minutes)

Add to `~/.config/claude/mcp_settings.json` (or Windows equivalent):

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:/Personal_Ai_Employee/Gold/mcp-servers/odoo-mcp/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "api@localhost",
        "ODOO_PASSWORD": "your_password"
      }
    }
  }
}
```

**Note:** Adjust the path to match your installation directory.

## Step 7: Test with Claude Code (5 minutes)

Open Claude Code and try:

```
Use the Odoo MCP server to get a financial summary
```

Expected response: Financial data from your Odoo instance.

## Quick Test: Create an Invoice

Create a test task file:

```bash
cat > vault/Needs_Action/TEST_INVOICE.md << 'EOF'
---
type: accounting
task_type: create_invoice
customer_name: Test Customer
---

# Create Test Invoice

Invoice lines:
- Consulting services: 5 hours @ $100/hr
- Software license: 1 @ $200

Due date: 2026-04-30
EOF
```

Then in Claude Code:

```
Process the TEST_INVOICE task in vault/Needs_Action/
```

Claude will:
1. Read the task file
2. Use the accounting-assistant skill
3. Create an approval request in Pending_Approval/
4. Wait for your approval

To approve:
```bash
# Move to Approved folder
mv vault/Pending_Approval/APPROVAL_*.md vault/Approved/
```

The approval workflow watcher will execute the invoice creation via Odoo MCP.

## Optional: Start Full Orchestrator

For continuous monitoring:

```bash
python orchestrator.py --config orchestrator_config.json
```

This starts all watchers:
- Odoo sync (every hour)
- Briefing scheduler (Sunday 11 PM)
- Approval workflow (every minute)
- Social media watchers (if configured)

Press Ctrl+C to stop.

## Troubleshooting

### Odoo won't start
```bash
# Check Docker is running
docker ps

# View Odoo logs
docker-compose -f odoo-integration/docker-compose.yml logs odoo

# Restart
docker-compose -f odoo-integration/docker-compose.yml restart
```

### MCP server connection fails
- Verify Odoo is running: http://localhost:8069
- Check credentials in .env
- Ensure API user has accounting permissions
- Check firewall isn't blocking port 8069

### Claude Code can't find MCP server
- Verify path in mcp_settings.json is absolute
- Check Node.js is in PATH
- Restart Claude Code after config changes

## Next Steps

1. **Create real invoices** - Replace test data with actual customers
2. **Set up social media** - Add Facebook/Instagram/Twitter credentials
3. **Enable CEO briefing** - Will run automatically every Sunday
4. **Explore skills** - Check `skills/*/SKILL.md` for documentation

## Getting Help

- Architecture: See [ARCHITECTURE.md](ARCHITECTURE.md)
- Full README: See [README.md](README.md)
- Skill docs: See `skills/*/SKILL.md`
- MCP docs: See `mcp-servers/*/README.md`

## Security Reminder

- Never commit `.env` to git
- Keep Odoo local (don't expose to internet)
- Review all approval requests before approving
- Audit logs are in `vault/Logs/audit/`

---

**Estimated total time: 30 minutes**

You now have a working Gold Tier autonomous business operations system!
