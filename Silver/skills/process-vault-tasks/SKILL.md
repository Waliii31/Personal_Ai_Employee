# Process Vault Tasks Skill

This skill enables Claude Code to process tasks in the AI Employee vault.

## Description

Monitors and processes tasks from the Obsidian vault, including:
- Reading tasks from Inbox and Needs_Action folders
- Creating Plan.md files for complex tasks
- Moving completed tasks to Done folder
- Logging all actions

## Usage

Invoke this skill when you need to:
- Process pending tasks in the vault
- Create action plans for complex work
- Organize and prioritize vault items

## Examples

```
/process-vault-tasks
```

Or in conversation:
```
Please process the pending tasks in my vault
```

## What It Does

1. Scans Inbox and Needs_Action folders
2. Analyzes each task
3. Creates structured plans for complex tasks
4. Moves completed items to Done
5. Updates Dashboard.md with current status

## Requirements

- Vault must exist at configured path
- Proper folder structure (Inbox, Needs_Action, Done, Plans)
- Write permissions to vault directory
