"""
Initialize Gold Tier Vault Structure
Creates all necessary directories and placeholder files
"""

from pathlib import Path
import json


def init_vault(vault_path: str = 'vault'):
    """Initialize vault directory structure"""
    vault = Path(vault_path)

    # Create main directories
    directories = [
        'Needs_Action',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Done',
        'Accounting',
        'Social_Media/Drafts',
        'Briefings',
        'Logs/audit',
        'Logs/errors',
        'Logs/performance',
        'Logs/loop_state',
    ]

    for directory in directories:
        dir_path = vault / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f'[OK] Created {directory}/')

    # Create Dashboard.md
    dashboard = vault / 'Dashboard.md'
    if not dashboard.exists():
        dashboard.write_text("""# Gold Tier Dashboard

## System Status
- Orchestrator: Running
- Watchers: 8 active
- MCP Servers: 2 connected

## Recent Activity
- Last briefing: Pending
- Pending approvals: 0
- Tasks completed today: 0

## Quick Links
- [Needs Action](Needs_Action/)
- [Pending Approval](Pending_Approval/)
- [Briefings](Briefings/)
- [Audit Logs](Logs/audit/)

## Financial Summary
- Revenue (MTD): $0.00
- Expenses (MTD): $0.00
- Profit (MTD): $0.00

*Last updated: System initialization*
""")
        print('[OK] Created Dashboard.md')

    # Create .gitkeep files for empty directories
    for directory in directories:
        gitkeep = vault / directory / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.touch()

    # Create sample task
    sample_task = vault / 'Needs_Action' / 'SAMPLE_TASK.md'
    if not sample_task.exists():
        sample_task.write_text("""---
type: sample
created: 2026-03-14
priority: low
---

# Sample Task

This is a sample task file to demonstrate the vault structure.

## Instructions

1. Delete this file when you're ready to start
2. Create real tasks in this folder
3. Claude will process them automatically

## Task Types

- `accounting` - Financial tasks (invoices, expenses)
- `social_media` - Social media posts
- `business_audit` - Generate briefings
- `email` - Email responses
- `general` - Other tasks
""")
        print('[OK] Created sample task')

    print('\n[SUCCESS] Vault initialization complete!')
    print(f'Vault location: {vault.absolute()}')


if __name__ == '__main__':
    init_vault()
