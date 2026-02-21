# Quick Start Guide

Get your Personal AI Employee up and running in under 30 minutes.

## Prerequisites Check

Before starting, verify you have:

```bash
# Check Claude Code
claude --version

# Check Python
python --version  # Should be 3.13+

# Check Node.js
node --version  # Should be v24+

# Check Git
git --version
```

If any are missing, install them from the [Prerequisites section](./README.md#prerequisites).

## Step 1: Clone and Setup (5 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd Personal_Ai_Employee

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# At minimum, set:
# - VAULT_PATH
# - CLAUDE_API_KEY
nano .env  # or use your preferred editor
```

## Step 2: Start with Bronze Tier (10 minutes)

```bash
# Navigate to Bronze tier
cd Bronze

# Install Python dependencies
pip install -r requirements.txt

# Or use UV (recommended)
uv pip install -r requirements.txt

# Verify setup
python test_setup.py
```

## Step 3: Configure Obsidian (5 minutes)

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `Bronze/AI_Employee_Vault`
4. Open `Dashboard.md` to see your dashboard

## Step 4: Test the Filesystem Watcher (5 minutes)

```bash
# Start the watcher
cd Bronze/watchers
python filesystem_watcher.py

# In another terminal, test it
cd Bronze/AI_Employee_Vault/Inbox
echo "Test task" > test_task.md

# Check Needs_Action folder - you should see a new file
```

## Step 5: Integrate Claude Code (5 minutes)

```bash
# Navigate to your vault
cd Bronze/AI_Employee_Vault

# Start Claude Code
claude

# In Claude, try:
# "Read the Dashboard.md file and summarize what you see"
# "Check the Needs_Action folder and create a plan for any tasks"
```

## Verification Checklist

After setup, verify:

- [ ] Obsidian vault opens without errors
- [ ] Dashboard.md displays correctly
- [ ] Filesystem watcher detects new files
- [ ] Files appear in Needs_Action folder
- [ ] Claude Code can read vault files
- [ ] Logs are being created in Logs folder

## Common Setup Issues

### Claude Code Not Found

```bash
# Install Claude Code globally
npm install -g @anthropic/claude-code

# Restart terminal
```

### Python Dependencies Fail

```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Watcher Doesn't Detect Files

```bash
# Check permissions
ls -la Bronze/AI_Employee_Vault/Inbox

# Verify VAULT_PATH in .env
echo $VAULT_PATH

# Check watcher is running
ps aux | grep filesystem_watcher
```

### Obsidian Won't Open Vault

- Make sure the path is correct
- Check folder permissions
- Try creating a new vault and copying files

## Next Steps

Once Bronze tier is working:

1. **Complete Bronze Requirements**
   - Create Company_Handbook.md with your rules
   - Test the full workflow (file → watcher → action → done)
   - Create your first Agent Skill

2. **Progress to Silver Tier**
   - Add Gmail watcher
   - Implement MCP server
   - Set up approval workflow

3. **Join the Community**
   - Attend Wednesday research meetings
   - Share your progress
   - Learn from others

## Quick Commands Reference

```bash
# Start filesystem watcher
cd Bronze/watchers && python filesystem_watcher.py

# Start Claude Code in vault
cd Bronze/AI_Employee_Vault && claude

# View logs
tail -f Bronze/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).log

# Check watcher status
ps aux | grep watcher

# Stop all watchers
pkill -f watcher
```

## Getting Help

If you're stuck:

1. Check the [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
2. Review the [Bronze Tier README](./Bronze/README.md)
3. Join Wednesday research meeting
4. Check the [CHANGELOG](./CHANGELOG.md) for known issues

## Time Estimates

- **Bronze Tier**: 8-12 hours total
- **Silver Tier**: 20-30 hours total
- **Gold Tier**: 40+ hours total
- **Platinum Tier**: 60+ hours total

Start with Bronze and progress at your own pace!

---

**Ready to build your AI Employee? Let's go!** 🚀
