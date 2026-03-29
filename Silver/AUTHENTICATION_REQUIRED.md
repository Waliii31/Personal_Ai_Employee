# Gmail Authentication - Manual Steps Required

## The Fix is Complete! ✅

The path issue has been resolved. The Gmail watcher now correctly finds `credentials.json` in the Silver directory.

## Next Step: Authenticate (You Must Do This)

**Run this command in your terminal:**

```bash
cd D:\Personal_Ai_Employee\Silver\watchers
python gmail_watcher.py ../vault
```

## What Will Happen:

1. **Browser Opens Automatically**
   - A browser window will open
   - You'll see Google's OAuth consent screen

2. **Sign In**
   - Sign in with your Gmail account
   - Choose the account you want to use

3. **Grant Permissions**
   - Google will ask: "AI Employee Gmail wants to access your Gmail"
   - Click "Allow" or "Continue"

4. **Success Message**
   - Browser will show: "The authentication flow has completed"
   - Terminal will show: "Gmail authentication successful"

5. **Stop the Watcher**
   - Press `Ctrl+C` in the terminal
   - The `token.pickle` file is now saved

## After Authentication:

You'll see this in your terminal:
```
2026-02-24 XX:XX:XX - GmailWatcher - INFO - Gmail authentication successful
2026-02-24 XX:XX:XX - GmailWatcher - INFO - Starting GmailWatcher
2026-02-24 XX:XX:XX - GmailWatcher - INFO - Monitoring vault: D:\Personal_Ai_Employee\Silver\vault
```

Press `Ctrl+C` to stop it. The authentication is saved in `token.pickle` and you won't need to do this again.

## Verify Authentication:

After completing the above, run:
```bash
cd D:\Personal_Ai_Employee\Silver
python test_gmail_setup.py
```

You should see:
```
[OK] credentials.json found
[OK] token.pickle found (Already authenticated)
```

## Then You Can:

1. **Start the full system:**
   ```bash
   python orchestrator.py ./vault
   ```

2. **Or test just Gmail watcher:**
   ```bash
   cd watchers
   python gmail_watcher.py ../vault
   ```

## Troubleshooting:

**Browser doesn't open?**
- Check your firewall settings
- Make sure you have a default browser set
- Try running as administrator

**"Access blocked" error?**
- Your app needs to be verified by Google (for production)
- For testing, click "Advanced" → "Go to AI Employee Gmail (unsafe)"
- This is normal for development apps

**Still having issues?**
- Check `vault/Logs/GmailWatcher.log` for errors
- Make sure credentials.json is valid
- Try deleting token.pickle and re-authenticating

---

**Status:** Path issue fixed ✅
**Next:** You need to authenticate manually (see above)
