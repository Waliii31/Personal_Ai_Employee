# Email MCP Server

## Overview
This MCP server provides email sending capabilities to Claude Code via the Gmail API.

## Features
- Send new emails
- Reply to existing email threads
- Retrieve email details
- Support for CC and BCC

## Setup

### 1. Install Dependencies
```bash
cd mcp-servers/email-mcp
npm install
```

### 2. Configure Gmail API

**Get Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials as `credentials.json`
6. Place in the Silver directory root

**Authenticate:**
```bash
# Run the Gmail watcher once to authenticate
cd ../../watchers
python gmail_watcher.py ../vault
```

This will open a browser for OAuth consent and save `token.json`.

### 3. Configure Claude Code

Add to your `.claude/settings.local.json`:

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

**Important:** Use absolute paths in the configuration.

### 4. Test the Server

```bash
# Test directly
node index.js

# Or via Claude Code
# In Claude Code, the server will be available automatically
```

## Usage in Claude Code

Once configured, Claude Code can use these tools:

### Send Email
```
Please send an email to john@example.com with subject "Meeting Follow-up"
and body "Thanks for the great meeting today!"
```

### Reply to Email
```
Reply to message ID abc123 in thread xyz789 with: "I'll get back to you tomorrow."
```

### Get Email Details
```
Get the details of email message ID abc123
```

## Tools Available

### 1. send_email
Send a new email via Gmail.

**Parameters:**
- `to` (required): Recipient email address
- `subject` (required): Email subject
- `body` (required): Email body (plain text or HTML)
- `cc` (optional): CC recipients (comma-separated)
- `bcc` (optional): BCC recipients (comma-separated)

### 2. send_reply
Reply to an existing email thread.

**Parameters:**
- `thread_id` (required): Gmail thread ID
- `message_id` (required): Gmail message ID to reply to
- `body` (required): Reply content

### 3. get_email
Retrieve email details by ID.

**Parameters:**
- `message_id` (required): Gmail message ID

## Security Notes

- Never commit `credentials.json` or `token.json`
- Add to `.gitignore`:
  ```
  credentials.json
  token.json
  token.pickle
  ```
- Use environment variables for sensitive paths
- Regularly review OAuth permissions

## Troubleshooting

**Error: Credentials file not found**
- Ensure `credentials.json` is in the correct location
- Check the path in `settings.local.json`

**Error: Token file not found**
- Run Gmail watcher first to authenticate
- Or manually run OAuth flow

**Error: Invalid grant**
- Token may have expired
- Delete `token.json` and re-authenticate

**MCP server not connecting**
- Check absolute paths in configuration
- Verify Node.js is installed
- Check server logs in Claude Code

## Development

To modify the server:

1. Edit `index.js`
2. Restart Claude Code to reload the server
3. Test with Claude Code commands

## Integration with Approval Workflow

Emails requiring approval will:
1. Be created as drafts in `/Pending_Approval`
2. Wait for user to move to `/Approved`
3. Trigger MCP server to send
4. Log result in `/Logs`

See the orchestrator documentation for details.
