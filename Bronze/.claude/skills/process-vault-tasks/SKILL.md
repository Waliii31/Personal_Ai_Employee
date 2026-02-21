# Process Vault Tasks

Process pending tasks in the AI Employee vault by reading files from Needs_Action, analyzing them according to Company Handbook rules, and taking appropriate actions.

## What this skill does

This skill enables Claude Code to act as an AI Employee by:
1. Reading files from the Needs_Action folder
2. Analyzing them according to Company_Handbook.md rules
3. Creating action plans in the Plans folder
4. Processing tasks and moving completed items to Done
5. Updating the Dashboard with current status

## When to use this skill

Use this skill when you need to:
- Process pending tasks in the vault
- Check for new items requiring attention
- Update the dashboard with current status
- Execute the AI Employee workflow

## How it works

The skill follows this workflow:
1. **Read Company Handbook** - Understand operating rules and approval thresholds
2. **Check Needs_Action folder** - Find pending tasks
3. **Analyze each task** - Determine required actions based on handbook rules
4. **Create action plans** - Document steps in Plans folder
5. **Execute safe actions** - Process items that don't require approval
6. **Request approval** - Move sensitive items to Pending_Approval
7. **Update Dashboard** - Reflect current system status
8. **Move to Done** - Archive completed tasks with timestamps

## Example usage

```bash
# Process all pending tasks
/process-vault-tasks

# Process with specific focus
/process-vault-tasks "Focus on high priority items"
```

## Vault structure expected

```
AI_Employee_Vault/
├── Dashboard.md              # System status
├── Company_Handbook.md       # Operating rules
├── Needs_Action/            # Pending tasks
├── Plans/                   # Action plans
├── Done/                    # Completed tasks
├── Pending_Approval/        # Awaiting human approval
└── Logs/                    # Activity logs
```

## Safety features

- Always follows Company_Handbook.md rules
- Requires approval for sensitive actions
- Logs all activities
- Never acts on financial or communication tasks without approval
