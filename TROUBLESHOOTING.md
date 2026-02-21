# Troubleshooting Guide

Common issues and solutions for my Personal AI Employee project.

## Table of Contents

- [Setup Issues](#setup-issues)
- [Watcher Problems](#watcher-problems)
- [Claude Code Issues](#claude-code-issues)
- [MCP Server Problems](#mcp-server-problems)
- [Obsidian Vault Issues](#obsidian-vault-issues)
- [API and Authentication](#api-and-authentication)
- [Performance Issues](#performance-issues)
- [Security Concerns](#security-concerns)

---

## Setup Issues

### Python Version Mismatch

**Problem**: `python --version` shows older version than 3.13

**Solution**:
```bash
# Install Python 3.13
# On Windows: Download from python.org
# On Mac: brew install python@3.13
# On Linux: sudo apt install python3.13

# Use specific version
python3.13 --version

# Create alias
alias python=python3.13
```

### UV Installation Fails

**Problem**: `uv` command not found

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Verify
uv --version
```

### Environment Variables Not Loading

**Problem**: `.env` file not being read

**Solution**:
```bash
# Check file exists
ls -la .env

# Verify format (no spaces around =)
# Correct: API_KEY=value
# Wrong: API_KEY = value

# Load manually for testing
export $(cat .env | xargs)

# Or use python-dotenv
pip install python-dotenv
```

---

## Watcher Problems

### Watcher Stops Running

**Problem**: Watcher script exits unexpectedly

**Solution**:
```bash
# Check logs
tail -f Bronze/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).log

# Run with error output
python watchers/filesystem_watcher.py 2>&1 | tee watcher_debug.log

# Use process manager
pip install supervisor
# Or
npm install -g pm2
pm2 start watchers/filesystem_watcher.py --interpreter python3
```

### Files Not Being Detected

**Problem**: New files in Inbox aren't triggering actions

**Solution**:
```bash
# Verify watcher is running
ps aux | grep watcher

# Check file permissions
ls -la Bronze/AI_Employee_Vault/Inbox

# Test with explicit file creation
touch Bronze/AI_Employee_Vault/Inbox/test.txt

# Check VAULT_PATH in .env
echo $VAULT_PATH

# Verify watchdog is installed
pip install watchdog
```

### Multiple Watcher Instances

**Problem**: Multiple watchers running, causing duplicates

**Solution**:
```bash
# Find all watcher processes
ps aux | grep watcher

# Kill all watchers
pkill -f filesystem_watcher

# Or kill specific PID
kill <PID>

# Prevent multiple instances
# Add to watcher script:
import fcntl
lock_file = open('/tmp/watcher.lock', 'w')
fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
```

---

## Claude Code Issues

### Claude Code Command Not Found

**Problem**: `claude: command not found`

**Solution**:
```bash
# Install Claude Code
npm install -g @anthropic/claude-code

# Check installation
which claude

# Add to PATH if needed
export PATH="$PATH:$HOME/.npm-global/bin"

# Restart terminal
```

### Claude Can't Read Vault Files

**Problem**: Claude says it can't access files

**Solution**:
```bash
# Run Claude from vault directory
cd Bronze/AI_Employee_Vault
claude

# Or use --cwd flag
claude --cwd=/path/to/vault

# Check file permissions
chmod -R 755 Bronze/AI_Employee_Vault

# Verify Claude has file system access
# Check Claude Code settings
```

### API Key Invalid

**Problem**: "Invalid API key" error

**Solution**:
```bash
# Verify API key in .env
cat .env | grep CLAUDE_API_KEY

# Check for extra spaces or quotes
# Should be: CLAUDE_API_KEY=sk-ant-...

# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01"

# Get new API key from console.anthropic.com
```

---

## MCP Server Problems

### MCP Server Won't Start

**Problem**: MCP server fails to start

**Solution**:
```bash
# Check Node.js version
node --version  # Should be v24+

# Install dependencies
cd mcp-servers/email-mcp
npm install

# Check for port conflicts
lsof -i :3000  # Replace with your port

# Run with debug output
DEBUG=* node index.js

# Check MCP configuration
cat ~/.config/claude-code/mcp.json
```

### Claude Can't Connect to MCP

**Problem**: "Failed to connect to MCP server"

**Solution**:
```bash
# Verify MCP server is running
ps aux | grep mcp

# Check absolute paths in config
# Wrong: "./mcp-servers/email-mcp/index.js"
# Right: "/full/path/to/mcp-servers/email-mcp/index.js"

# Test MCP server directly
curl http://localhost:3000/health

# Check Claude Code logs
tail -f ~/.claude-code/logs/mcp.log
```

### MCP Tools Not Available

**Problem**: Claude doesn't see MCP tools

**Solution**:
```bash
# Restart Claude Code
# Exit and restart

# Verify MCP config syntax
cat ~/.config/claude-code/mcp.json | jq .

# Check server logs
# Look for tool registration messages

# Test with simple MCP server first
npx @anthropic/mcp-server-example
```

---

## Obsidian Vault Issues

### Vault Won't Open

**Problem**: Obsidian can't open vault

**Solution**:
- Check folder exists: `ls -la Bronze/AI_Employee_Vault`
- Verify it's a directory, not a file
- Check permissions: `chmod 755 Bronze/AI_Employee_Vault`
- Try creating new vault and copying files
- Check Obsidian version (should be 1.10.6+)

### Files Not Syncing

**Problem**: Changes not appearing in vault

**Solution**:
- Close and reopen Obsidian
- Check file system permissions
- Disable conflicting plugins
- Check .obsidian/workspace file isn't corrupted
- Verify no file locks: `lsof | grep AI_Employee_Vault`

### Dashboard Not Updating

**Problem**: Dashboard.md shows old data

**Solution**:
```bash
# Check file modification time
stat Bronze/AI_Employee_Vault/Dashboard.md

# Verify write permissions
ls -la Bronze/AI_Employee_Vault/Dashboard.md

# Check if file is locked
lsof Bronze/AI_Employee_Vault/Dashboard.md

# Force refresh in Obsidian
# Close file and reopen
```

---

## API and Authentication

### Gmail API 403 Forbidden

**Problem**: Gmail API returns 403 error

**Solution**:
1. Enable Gmail API in Google Cloud Console
2. Configure OAuth consent screen
3. Add test users if in testing mode
4. Regenerate credentials
5. Check API quotas

```bash
# Test credentials
python -c "
from google.oauth2.credentials import Credentials
creds = Credentials.from_authorized_user_file('credentials.json')
print('Valid' if creds.valid else 'Invalid')
"
```

### LinkedIn API Rate Limit

**Problem**: "Rate limit exceeded" error

**Solution**:
```python
# Implement exponential backoff
import time

def with_rate_limit(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            time.sleep(60)  # Wait 1 minute
            return func(*args, **kwargs)
    return wrapper
```

### WhatsApp Session Expired

**Problem**: WhatsApp watcher can't connect

**Solution**:
```bash
# Delete old session
rm -rf /path/to/whatsapp-session

# Run watcher in headed mode to scan QR
# Edit watcher to set headless=False temporarily
python watchers/whatsapp_watcher.py

# Scan QR code with phone
# Session will be saved for future use
```

---

## Performance Issues

### High CPU Usage

**Problem**: Watchers consuming too much CPU

**Solution**:
```python
# Increase check interval
# In .env:
WATCHER_CHECK_INTERVAL=300  # 5 minutes instead of 60 seconds

# Optimize file operations
# Use os.scandir() instead of os.listdir()
# Implement caching for unchanged files
```

### Memory Leaks

**Problem**: Memory usage grows over time

**Solution**:
```python
# Add garbage collection
import gc

def cleanup():
    gc.collect()

# Call periodically in watcher loop

# Restart watchers daily
# Add to cron:
0 3 * * * pkill -f watcher && sleep 10 && python /path/to/watcher.py
```

### Slow Vault Operations

**Problem**: Reading/writing vault is slow

**Solution**:
- Move vault to SSD if on HDD
- Reduce number of files in single folder
- Implement file archiving for old tasks
- Use database for metadata instead of file scanning

---

## Security Concerns

### Credentials Exposed in Git

**Problem**: Accidentally committed .env file

**Solution**:
```bash
# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner
bfg --delete-files .env

# Force push (WARNING: destructive)
git push origin --force --all

# Rotate all exposed credentials immediately
```

### Unauthorized Access to Vault

**Problem**: Concerned about vault security

**Solution**:
```bash
# Encrypt vault
# Install git-crypt
git-crypt init

# Add to .gitattributes
*.md filter=git-crypt diff=git-crypt
.env filter=git-crypt diff=git-crypt

# Or use full disk encryption
# Windows: BitLocker
# Mac: FileVault
# Linux: LUKS
```

### MCP Server Security

**Problem**: MCP server exposed to network

**Solution**:
```javascript
// Bind to localhost only
server.listen(3000, '127.0.0.1', () => {
  console.log('MCP server listening on localhost:3000');
});

// Add authentication
const API_KEY = process.env.MCP_API_KEY;
app.use((req, res, next) => {
  if (req.headers['x-api-key'] !== API_KEY) {
    return res.status(401).send('Unauthorized');
  }
  next();
});
```

---

## Getting More Help

If these solutions don't work:

1. **Check Logs**: Always start with the logs
   ```bash
   tail -f Bronze/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).log
   ```

2. **Enable Debug Mode**: Set in .env
   ```bash
   DEBUG=true
   VERBOSE_LOGGING=true
   ```

3. **Join Community**: Wednesday research meetings at 10:00 PM

4. **Review Documentation**: Check tier-specific READMEs

5. **Test in Isolation**: Create minimal reproduction case

---

**Last Updated**: 2026-02-22
