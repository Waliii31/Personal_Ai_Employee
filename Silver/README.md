# Silver Tier: Functional Assistant

**Estimated Time**: 20-30 hours
**Status**: 🔄 In Progress

## Overview

The Silver Tier builds upon the Bronze foundation to create a functional AI assistant with multiple data sources, automated posting capabilities, and human-in-the-loop approval workflows.

## Prerequisites

✅ Complete all Bronze Tier requirements first:
- Working Obsidian vault
- At least one functional Watcher script
- Claude Code integration
- Basic folder structure

## Silver Tier Requirements

### 1. Multiple Watcher Scripts (2+)

I need to implement at least two of the following watchers:

- [ ] **Gmail Watcher** - Monitor important emails
- [ ] **WhatsApp Watcher** - Track urgent messages
- [ ] **LinkedIn Watcher** - Monitor professional network

**Location**: `./watchers/`

### 2. Automated LinkedIn Posting

- [ ] Create LinkedIn posting automation
- [ ] Generate business content automatically
- [ ] Schedule posts for optimal engagement
- [ ] Track post performance

**Purpose**: Generate sales leads and business visibility

### 3. Claude Reasoning Loop

- [ ] Implement Plan.md file generation
- [ ] Create structured task breakdown
- [ ] Add progress tracking
- [ ] Enable multi-step reasoning

**Location**: `./vault/Plans/`

### 4. MCP Server Implementation

I need to build at least one working MCP server:

- [ ] **Email MCP** - Send emails programmatically
- [ ] **Social Media MCP** - Post to LinkedIn/Twitter
- [ ] **Calendar MCP** - Schedule events

**Location**: `./mcp-servers/`

### 5. Human-in-the-Loop Workflow

- [ ] Create approval request system
- [ ] Implement /Pending_Approval folder monitoring
- [ ] Add approval/rejection logic
- [ ] Log all approval decisions

**Critical for**: Sensitive actions requiring my review

### 6. Scheduling System

- [ ] Set up cron jobs (Linux/Mac) or Task Scheduler (Windows)
- [ ] Schedule daily briefings
- [ ] Automate watcher startup
- [ ] Implement health checks

### 7. Agent Skills

- [ ] Convert all AI functionality to Agent Skills
- [ ] Create skill documentation
- [ ] Test skill invocation
- [ ] Version control skills

**Location**: `./skills/`

## Folder Structure

```
Silver/
├── README.md                    # This file
├── vault/                       # Extended Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Plans/                   # NEW: Claude-generated plans
│   ├── Pending_Approval/        # NEW: Approval requests
│   ├── Approved/
│   ├── Rejected/
│   ├── Done/
│   └── Logs/
├── watchers/                    # Multiple watcher scripts
│   ├── base_watcher.py
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   └── linkedin_watcher.py
├── mcp-servers/                 # MCP server implementations
│   ├── email-mcp/
│   ├── social-mcp/
│   └── calendar-mcp/
├── skills/                      # Agent Skills
│   ├── email-handler/
│   ├── linkedin-poster/
│   └── task-planner/
└── orchestrator.py              # Master coordination script
```

## Implementation Guide

### Step 1: Add More Watchers

Start by implementing the Gmail and WhatsApp watchers:

```python
# watchers/gmail_watcher.py
from base_watcher import BaseWatcher
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str):
        super().__init__(vault_path, check_interval=120)
        # Implementation details in Bronze tier docs
```

### Step 2: Build LinkedIn Automation

Create a LinkedIn posting system:

```python
# skills/linkedin-poster/
# Use LinkedIn API or browser automation
# Generate business content
# Schedule posts
```

### Step 3: Implement MCP Server

Choose one MCP server to implement first (Email recommended):

```bash
cd mcp-servers/email-mcp
npm init -y
npm install @anthropic/mcp
# Follow MCP documentation
```

### Step 4: Set Up Approval Workflow

Create the approval monitoring system:

```python
# orchestrator.py
def monitor_approvals():
    # Watch /Pending_Approval folder
    # Detect file moves to /Approved
    # Trigger corresponding MCP action
    # Log results
```

### Step 5: Configure Scheduling

**Windows (Task Scheduler)**:
```bash
# Create scheduled task for daily briefing
schtasks /create /tn "AI_Employee_Briefing" /tr "python orchestrator.py --briefing" /sc daily /st 08:00
```

**Linux/Mac (cron)**:
```bash
# Add to crontab
0 8 * * * cd /path/to/Silver && python orchestrator.py --briefing
```

## Testing Checklist

- [ ] All watchers run continuously without crashing
- [ ] LinkedIn posts are generated and published
- [ ] Plan.md files are created for complex tasks
- [ ] MCP server responds to Claude Code requests
- [ ] Approval workflow prevents unauthorized actions
- [ ] Scheduled tasks execute on time
- [ ] All functionality is available as Agent Skills

## Security Considerations

### Credential Management

```bash
# .env file (NEVER commit)
GMAIL_CLIENT_ID=your_id
GMAIL_CLIENT_SECRET=your_secret
LINKEDIN_ACCESS_TOKEN=your_token
WHATSAPP_SESSION_PATH=/secure/path
```

### Approval Thresholds

Define what requires my approval:

| Action | Auto-Approve | Requires Approval |
|--------|--------------|-------------------|
| Email replies | Known contacts | New contacts, bulk |
| LinkedIn posts | Scheduled drafts | Immediate posts |
| Calendar events | Personal | Business meetings |

## Common Issues

### Watcher Crashes
**Problem**: Watchers stop running overnight
**Solution**: Use PM2 or supervisord for process management

### API Rate Limits
**Problem**: Too many API calls
**Solution**: Implement exponential backoff and caching

### MCP Connection Fails
**Problem**: Claude Code can't connect to MCP
**Solution**: Check absolute paths in mcp.json config

## Next Steps

Once Silver Tier is complete, I can progress to:
- **Gold Tier**: Full business integration with Odoo accounting
- Advanced multi-platform social media
- Comprehensive CEO briefings

## Resources

- [MCP Server Development](https://modelcontextprotocol.io/quickstart)
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart)
- [LinkedIn API Docs](https://docs.microsoft.com/en-us/linkedin/)
- [Playwright Automation](https://playwright.dev/python/docs/intro)

---

**My Progress**: Track completion in the main README.md
