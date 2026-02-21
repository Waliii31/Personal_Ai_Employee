# Quick Start Guide - Bronze Tier AI Employee

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
# Navigate to the Bronze directory
cd D:/Personal_Ai_Employee/Bronze

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Start the File System Watcher
**On Windows:**
```bash
start_watcher.bat
```

**On Mac/Linux:**
```bash
chmod +x start_watcher.sh
./start_watcher.sh
```

### Step 3: Test the System
1. Open a new terminal/command prompt
2. Drop a test file into the Inbox:
   ```bash
   echo "Test document for processing" > AI_Employee_Vault/Inbox/test.txt
   ```
3. Check the `Needs_Action` folder - you should see a new markdown file created!

### Step 4: Process Tasks with Claude Code
```bash
# Navigate to the vault
cd AI_Employee_Vault

# Use the Agent Skill to process tasks
claude /process-vault-tasks

# Or manually ask Claude
claude "Check the Needs_Action folder and process any pending tasks according to Company_Handbook.md rules"
```

## 📋 Common Commands

### Check System Status
```bash
cd AI_Employee_Vault
claude "Read Dashboard.md and give me a status update"
```

### Process Specific Task
```bash
cd AI_Employee_Vault
claude "Process the file FILE_20260222_120000_test.txt.md in Needs_Action folder"
```

### Update Dashboard
```bash
cd AI_Employee_Vault
claude "Update Dashboard.md with current statistics from all folders"
```

## 🎯 Workflow Example

1. **Drop a file** → `Inbox/document.pdf`
2. **Watcher detects** → Creates `Needs_Action/FILE_20260222_120000_document.pdf.md`
3. **Claude processes** → Analyzes the file and creates a plan
4. **Action taken** → Moves to `Done/` when complete
5. **Dashboard updated** → Shows latest activity

## 🔍 Folder Structure

```
AI_Employee_Vault/
├── 📊 Dashboard.md           # Your control center
├── 📖 Company_Handbook.md    # Operating rules
├── 📥 Inbox/                 # Drop files here
├── ⚡ Needs_Action/          # Tasks to process
├── ✅ Done/                  # Completed tasks
├── 📝 Plans/                 # Action plans
├── ⏳ Pending_Approval/      # Awaiting your approval
├── ✔️ Approved/              # Approved actions
├── ❌ Rejected/              # Rejected actions
└── 📋 Logs/                  # Activity logs
```

## 💡 Tips

- **Keep the watcher running** in the background for automatic monitoring
- **Review Dashboard.md daily** to stay updated
- **Check Company_Handbook.md** to understand how the AI makes decisions
- **Use the /process-vault-tasks skill** for automated processing
- **Always review Pending_Approval** before approving sensitive actions

## 🐛 Troubleshooting

**Watcher not starting?**
- Ensure Python 3.13+ is installed: `python --version`
- Install watchdog: `pip install watchdog`

**Claude not finding files?**
- Make sure you're in the `AI_Employee_Vault` directory
- Use absolute paths if needed

**No action files created?**
- Check if the watcher is running
- Verify file permissions on the Inbox folder
- Check the Logs folder for error messages

## 🎓 Next Steps

Once comfortable with Bronze tier:
- **Silver Tier**: Add Gmail and WhatsApp watchers
- **Gold Tier**: Integrate Odoo accounting and social media
- **Platinum Tier**: Deploy to cloud for 24/7 operation

---
**Congratulations! Your AI Employee is ready to work.** 🎉
