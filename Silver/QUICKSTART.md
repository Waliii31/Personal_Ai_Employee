# Quick Start Guide - Silver Tier

Get your AI Employee running in 15 minutes!

## Prerequisites
- Python 3.x installed
- Node.js installed (for MCP server)
- Gmail account
- Google Cloud account (free tier)

## Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Install Node.js packages for MCP server
cd mcp-servers/email-mcp
npm install
cd ../..
```

## Step 2: Set Up Gmail API (5 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project: "AI Employee"
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials as `credentials.json`
6. Place in Silver directory root

## Step 3: Authenticate Gmail (2 minutes)

```bash
# Run Gmail watcher once to authenticate
cd watchers
python gmail_watcher.py ../vault
```

This will:
- Open browser for OAuth consent
- Save token.json for future use
- You can press Ctrl+C after authentication

## Step 4: Test Everything (1 minute)

```bash
# Run the test suite
python test_silver_tier.py ./vault
```

Expected output: `*** SILVER TIER COMPLETE! ***`

## Step 5: Configure Claude Code (3 minutes)

Add to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["D:/Personal_Ai_Employee/Silver/mcp-servers/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "D:/Personal_Ai_Employee/Silver/credentials.json",
        "GMAIL_TOKEN_PATH": "D:/Personal_Ai_Employee/Silver/token.json"
      }
    }
  }
}
```

**Important:** Use absolute paths!

## Step 6: Start Your AI Employee (1 minute)

```bash
# Start all watchers and automation
python orchestrator.py ./vault
```

You should see:
```
AI Employee Orchestrator - Silver Tier
Starting gmail watcher...
Starting whatsapp watcher...
Starting approval watcher...
All components started successfully!
```

## Step 7: Set Up Scheduling (Optional, 1 minute)

**Windows:**
```bash
setup_scheduler.bat
```

**Linux/Mac:**
```bash
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

## You're Done! 🎉

Your AI Employee is now running and will:
- Monitor your Gmail for important emails
- Watch for urgent WhatsApp messages
- Generate LinkedIn content weekly
- Create action plans for complex tasks
- Request approval for sensitive actions
- Generate daily briefings at 8 AM

## 

1. Drop a file in `vault/Inbox/`
2. Check `vault/Needs_Action/` for the task
3. Try in Claude Code: "Please process my pending vault tasks"

## Common Issues

**"Credentials file not found"**
- Make sure credentials.json is in Silver directory
- Check the path in settings.local.json

**"Token file not found"**
- Run Gmail watcher once to authenticate
- Follow the browser OAuth flow

**"MCP server not connecting"**
- Verify Node.js is installed: `node --version`
- Check absolute paths in settings.local.json
- Restart Claude Code

## Next Steps

- Review `vault/Dashboard.md` for system status
- Check `vault/Logs/` for activity logs
- Move items to `Pending_Approval` to test approval workflow
- Generate LinkedIn posts: `python watchers/linkedin_automation.py ./vault`

## Getting Help

- Check logs in `vault/Logs/`
- Run test suite: `python test_silver_tier.py`
- Review README.md for detailed documentation
- Check COMPLETION_SUMMARY.md for full implementation details

---

**Time to Complete:** ~15 minutes
**Difficulty:** Easy
**Status:** Production Ready
