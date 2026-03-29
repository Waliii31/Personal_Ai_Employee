# Gmail Setup Guide

## Step 1: Get Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app"
   - Name it "AI Employee Gmail"
   - Click "Create"
5. Download the credentials:
   - Click the download icon next to your OAuth client
   - Save as `credentials.json`

## Step 2: Place Credentials File

**IMPORTANT:** Place `credentials.json` in the Silver directory root:

```
Silver/
├── credentials.json          <-- Place here
├── watchers/
│   └── gmail_watcher.py
└── vault/
```

**Correct path:** `D:\Personal_Ai_Employee\Silver\credentials.json`

## Step 3: Authenticate

Run the Gmail watcher to authenticate:

```bash
cd D:\Personal_Ai_Employee\Silver\watchers
python gmail_watcher.py ../vault
```

This will:
1. Open your browser
2. Ask you to sign in to Google
3. Request permission to access Gmail
4. Save `token.pickle` in Silver directory

**After authentication:**
- Press Ctrl+C to stop the watcher
- `token.pickle` will be saved for future use
- You won't need to authenticate again unless token expires

## Step 4: Verify

Check that these files exist in Silver directory:
- `credentials.json` (you placed this)
- `token.pickle` (created after authentication)

## Troubleshooting

### Error: "Credentials file not found"
**Problem:** credentials.json is not in the correct location

**Solution:**
```bash
# Check current location
cd D:\Personal_Ai_Employee\Silver
ls credentials.json

# If not found, move it to Silver directory
# Make sure it's in: D:\Personal_Ai_Employee\Silver\credentials.json
```

### Error: "Token file not found"
**Problem:** You haven't authenticated yet

**Solution:** Run the watcher once to authenticate (Step 3 above)

### Error: "Invalid grant"
**Problem:** Token has expired

**Solution:**
```bash
# Delete old token and re-authenticate
cd D:\Personal_Ai_Employee\Silver
rm token.pickle
cd watchers
python gmail_watcher.py ../vault
```

### Browser doesn't open
**Problem:** Port might be blocked

**Solution:** Check firewall settings or try a different network

## Security Notes

- Never commit `credentials.json` to git
- Never commit `token.pickle` to git
- These files are already in `.gitignore`
- Keep these files secure and private

## Testing

After authentication, test the watcher:

```bash
cd D:\Personal_Ai_Employee\Silver\watchers
python gmail_watcher.py ../vault
```

You should see:
```
2026-02-24 XX:XX:XX - GmailWatcher - INFO - Gmail authentication successful
2026-02-24 XX:XX:XX - GmailWatcher - INFO - Starting GmailWatcher
2026-02-24 XX:XX:XX - GmailWatcher - INFO - Monitoring vault: ...
```

Press Ctrl+C to stop.

## Next Steps

Once Gmail is working:
1. Configure the MCP server (see mcp-servers/email-mcp/README.md)
2. Start the orchestrator to run all watchers
3. Test email processing with Claude Code
