# 🚀 Get Started with Gold Tier

Welcome to your **Gold Tier Personal AI Employee**! This guide will get you up and running in 30 minutes.

## What You Have

A fully autonomous business operations system with:
- 💰 **Odoo Accounting** - Invoice creation, expense tracking, financial reports
- 📱 **Social Media** - Facebook, Instagram, Twitter automation
- 📊 **CEO Briefings** - Weekly business intelligence and optimization
- 🤖 **Autonomous Operation** - Multi-step task completion with Ralph Wiggum loop
- 🛡️ **Error Recovery** - Automatic retry and graceful degradation
- 📝 **Audit Logging** - Complete audit trail with 90-day retention

## Quick Start (30 Minutes)

### Step 1: Run Setup Script (10 minutes)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install all dependencies
- Initialize vault structure
- Create .env file
- Validate setup

### Step 2: Configure Credentials (5 minutes)

Edit `.env` with your credentials:

```bash
# Required for basic functionality
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=api@localhost
ODOO_PASSWORD=your_password

# Optional - add when ready
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_USER_ID=your_user_id
INSTAGRAM_ACCESS_TOKEN=your_token
TWITTER_BEARER_TOKEN=your_token
```

### Step 3: Start Odoo (10 minutes)

```bash
cd odoo-integration
docker-compose up -d
```

Wait 2-3 minutes, then open http://localhost:8069

**Initial Setup:**
1. Create database: `odoo`
2. Set admin password
3. Install "Accounting" module
4. Create API user: `api@localhost`

See [odoo-integration/setup_guide.md](odoo-integration/setup_guide.md) for details.

### Step 4: Test Connection (5 minutes)

Configure Claude Code MCP settings in `~/.config/claude/mcp_settings.json`:

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

Test in Claude Code:
```
Use the Odoo MCP server to get a financial summary
```

## Your First Tasks

### Create an Invoice

Copy the example:
```bash
cp vault/Needs_Action/examples/EXAMPLE_INVOICE.md vault/Needs_Action/INVOICE_001.md
```

Edit with your customer details, then in Claude Code:
```
Process the INVOICE_001 task in vault/Needs_Action/
```

Claude will create an approval request. Review and move to `Approved/` to execute.

### Post to Social Media

Copy the example:
```bash
cp vault/Needs_Action/examples/EXAMPLE_SOCIAL_POST.md vault/Needs_Action/POST_001.md
```

Edit with your content, then process with Claude Code.

### Generate CEO Briefing

The briefing runs automatically every Sunday at 11 PM. To generate manually:

```bash
python skills/business-auditor/business_auditor.py --vault vault --report-type weekly_briefing
```

## Running the System

### Option 1: Full Orchestrator (Recommended)

Start all watchers:
```bash
python orchestrator.py
```

This runs:
- Odoo sync (every hour)
- Social media monitoring (every 5 minutes)
- Briefing scheduler (Sunday 11 PM)
- Approval workflow (every minute)

Press Ctrl+C to stop.

### Option 2: Individual Components

Run specific watchers:
```bash
# Odoo sync
python watchers/odoo_sync_watcher.py

# Facebook monitoring
python watchers/facebook_watcher.py

# CEO briefing
python watchers/briefing_scheduler.py
```

## Understanding the Workflow

### 1. Task Creation
- Create `.md` file in `vault/Needs_Action/`
- Include frontmatter with task type
- Add task details in markdown

### 2. Processing
- Claude reads task file
- Invokes appropriate skill
- Skill creates approval request

### 3. Approval
- Review request in `vault/Pending_Approval/`
- Move to `Approved/` to execute
- Move to `Rejected/` to cancel

### 4. Execution
- Approval workflow watcher detects approval
- Executes via MCP server
- Logs to audit trail
- Moves task to `Done/`

## Key Directories

```
vault/
├── Needs_Action/      # New tasks go here
├── Pending_Approval/  # Review and approve here
├── Approved/          # Approved actions (auto-processed)
├── Rejected/          # Rejected actions (archived)
├── Done/              # Completed tasks
├── Accounting/        # Cached Odoo data
├── Social_Media/      # Post drafts and analytics
├── Briefings/         # CEO briefings
└── Logs/              # Audit and error logs
```

## Monitoring

### View Audit Logs
```bash
# Today's audit log
cat vault/Logs/audit/$(date +%Y-%m-%d).json | jq

# Last 7 days summary
python -c "from audit_logger import AuditLogger; print(AuditLogger('vault').generate_summary(7))"
```

### View Error Logs
```bash
cat vault/Logs/errors/errors_$(date +%Y-%m-%d).json | jq
```

### Check System Status
```bash
# Validate setup
python validate_setup.py

# View orchestrator log
tail -f vault/Logs/orchestrator.log
```

## Troubleshooting

### Odoo Won't Start
```bash
docker-compose -f odoo-integration/docker-compose.yml logs odoo
docker-compose -f odoo-integration/docker-compose.yml restart
```

### MCP Connection Fails
- Verify Odoo is running: http://localhost:8069
- Check credentials in `.env`
- Ensure API user has accounting permissions
- Restart Claude Code

### Watcher Not Running
- Check orchestrator logs
- Verify watcher enabled in `orchestrator_config.json`
- Check for Python import errors

## Security Checklist

- [ ] `.env` file created and not committed to git
- [ ] Odoo admin password is strong
- [ ] API user has minimal required permissions
- [ ] Social media tokens are valid and secure
- [ ] Approval workflow is enabled
- [ ] Audit logging is enabled

## Next Steps

1. **Test Basic Functionality**
   - Create test invoice
   - Post test social media message
   - Generate test briefing

2. **Configure Social Media** (Optional)
   - Get API credentials
   - Add to `.env`
   - Test posting

3. **Enable Automation**
   - Start orchestrator
   - Let it run for a week
   - Review first CEO briefing

4. **Production Use**
   - Create real tasks
   - Review approvals carefully
   - Monitor audit logs
   - Adjust configuration as needed

## Documentation

- **[README.md](README.md)** - Complete overview
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)** - Implementation details
- **Skills:** See `skills/*/SKILL.md`
- **MCP Servers:** See `mcp-servers/*/README.md`

## Getting Help

1. Check documentation in respective folders
2. Review audit logs for errors
3. Run validation: `python validate_setup.py`
4. Check ARCHITECTURE.md for system design

## Success Metrics

After one week, you should see:
- ✅ Invoices created via approval workflow
- ✅ Social media posts published
- ✅ First CEO briefing generated
- ✅ Audit logs capturing all actions
- ✅ Error recovery handling failures
- ✅ Tasks completing autonomously

## Congratulations! 🎉

You now have a fully autonomous business operations system. Start with simple tasks and gradually increase automation as you gain confidence.

**The Gold Tier is ready for production use!**

---

**Need help?** Check the documentation or review the audit logs.
**Ready for more?** Platinum Tier adds 24/7 cloud deployment.
