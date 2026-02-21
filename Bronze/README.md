# Bronze Tier - Personal AI Employee

## Overview
This is a Bronze tier implementation of a Personal AI Employee using Claude Code and Obsidian for task management and automation.

## Project Structure
```
Bronze/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Main dashboard
│   ├── Company_Handbook.md     # Operating rules
│   ├── Inbox/                  # Drop files here
│   ├── Needs_Action/           # Files requiring processing
│   ├── Done/                   # Completed tasks
│   ├── Plans/                  # Task plans
│   ├── Logs/                   # Activity logs
│   ├── Pending_Approval/       # Awaiting approval
│   ├── Approved/               # Approved actions
│   └── Rejected/               # Rejected actions
├── watchers/                   # Monitoring scripts
│   ├── base_watcher.py         # Base watcher class
│   └── filesystem_watcher.py   # File system monitor
└── .claude/skills/             # Claude Code skills
```

## Prerequisites
- Python 3.13+
- Claude Code CLI
- Obsidian (optional, for GUI)
- UV (Python package manager)

## Setup Instructions

### 1. Install Dependencies
```bash
# Install UV if not already installed
pip install uv

# Create virtual environment and install dependencies
cd D:/Personal_Ai_Employee/Bronze
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install watchdog
```

### 2. Configure Obsidian (Optional)
1. Open Obsidian
2. Open vault: `D:/Personal_Ai_Employee/Bronze/AI_Employee_Vault`
3. Review Dashboard.md and Company_Handbook.md

### 3. Start the File System Watcher
```bash
python watchers/filesystem_watcher.py
```

### 4. Test the System
1. Drop a file into `AI_Employee_Vault/Inbox/`
2. The watcher will detect it and create an action file in `Needs_Action/`
3. Use Claude Code to process the action file

## Bronze Tier Features
✅ Obsidian vault with Dashboard.md and Company_Handbook.md
✅ File system watcher monitoring Inbox folder
✅ Basic folder structure for task management
✅ Claude Code integration for reading/writing vault
✅ Agent Skills for AI functionality

## Usage

### Dropping Files for Processing
1. Place any file in `AI_Employee_Vault/Inbox/`
2. The watcher automatically creates a task in `Needs_Action/`
3. Claude Code processes the task based on Company_Handbook rules

### Using Claude Code
```bash
# Navigate to vault
cd AI_Employee_Vault

# Ask Claude to process pending tasks
claude "Check Needs_Action folder and process any pending tasks"

# Update dashboard
claude "Update Dashboard.md with current status"
```

## Next Steps (Silver Tier)
- Add Gmail watcher
- Add WhatsApp watcher
- Implement MCP servers for external actions
- Add scheduling with cron/Task Scheduler
- Implement human-in-the-loop approval workflow

## Troubleshooting

### Watcher Not Starting
- Ensure Python 3.13+ is installed
- Install watchdog: `uv pip install watchdog`
- Check file permissions on vault folders

### Claude Code Not Reading Vault
- Ensure you're in the vault directory
- Use absolute paths if needed
- Verify file permissions

## Security Notes
- Never commit credentials or sensitive data
- Review Company_Handbook.md for approval rules
- All actions are logged in Logs/ folder

---
Built for Personal AI Employee Hackathon 2026
