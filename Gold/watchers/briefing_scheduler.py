"""
Briefing Scheduler Watcher
Triggers weekly CEO briefing generation every Sunday at 11 PM
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta


# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'Silver' / 'watchers'))
from base_watcher import BaseWatcher


class BriefingScheduler(BaseWatcher):
    """Schedules weekly CEO briefing generation"""

    def __init__(self, vault_path: str, check_interval: int = 3600):
        """
        Initialize briefing scheduler

        Args:
            vault_path: Path to vault
            check_interval: Seconds between checks (default: 3600 = 1 hour)
        """
        super().__init__(vault_path, check_interval)
        self.briefings_dir = self.vault_path / 'Briefings'
        self.briefings_dir.mkdir(parents=True, exist_ok=True)

        # Track last briefing generation
        self.last_briefing_file = self.briefings_dir / '.last_briefing'
        self.last_briefing = self._load_last_briefing()

    def _load_last_briefing(self) -> datetime:
        """Load last briefing timestamp"""
        if self.last_briefing_file.exists():
            try:
                timestamp = self.last_briefing_file.read_text().strip()
                return datetime.fromisoformat(timestamp)
            except Exception:
                pass
        return datetime.min

    def _save_last_briefing(self):
        """Save current briefing timestamp"""
        self.last_briefing_file.write_text(datetime.now().isoformat())

    def check_for_updates(self) -> list:
        """
        Check if briefing should be generated

        Triggers every Sunday at 11 PM (23:00)

        Returns:
            List with 'generate_briefing' if time to generate
        """
        now = datetime.now()

        # Check if it's Sunday (weekday 6)
        if now.weekday() != 6:
            return []

        # Check if it's between 11 PM and midnight
        if now.hour != 23:
            return []

        # Check if we already generated briefing today
        if self.last_briefing.date() == now.date():
            return []

        self.logger.info('Time to generate weekly CEO briefing')
        return ['generate_briefing']

    def create_action_file(self, item) -> Path:
        """
        Create action file to trigger briefing generation

        Args:
            item: 'generate_briefing' indicator

        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'BRIEFING_{timestamp}.md'
        filepath = self.needs_action / filename

        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        content = f"""---
type: business_audit
task_type: weekly_briefing
priority: high
created: {datetime.now().isoformat()}
date_range_start: {start_date.strftime('%Y-%m-%d')}
date_range_end: {end_date.strftime('%Y-%m-%d')}
---

# Generate Weekly CEO Briefing

## Task

Generate comprehensive weekly CEO briefing for the period:
**{start_date.strftime('%B %d')} to {end_date.strftime('%B %d, %Y')}**

## Required Sections

1. **Executive Summary** - One-line overview of the week
2. **Financial Performance** - Revenue, expenses, profit, receivables
3. **Completed Tasks** - List of tasks completed this week
4. **Bottlenecks** - Tasks that took longer than expected
5. **Subscription Audit** - Unused subscriptions and potential savings
6. **Proactive Suggestions** - Cost optimization and action items

## Data Sources

- Odoo financial data (cached in `Accounting/`)
- Completed tasks (from `Done/` folder)
- Bank transactions (for subscription audit)

## Instructions for Claude

Use the **business-auditor** skill to generate this briefing:

```bash
python Gold/skills/business-auditor/business_auditor.py \\
  --vault Gold/vault \\
  --report-type weekly_briefing
```

The briefing should be saved to `Briefings/CEO_BRIEFING_YYYYMMDD.md`

## Completion Criteria

- Briefing file created in `Briefings/` folder
- All required sections present
- Financial data accurate (matches Odoo)
- Actionable suggestions provided
- Move this file to `Done/` when complete
"""

        filepath.write_text(content)

        # Update last briefing timestamp
        self._save_last_briefing()
        self.last_briefing = datetime.now()

        return filepath


def main():
    """Main entry point"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get vault path
    vault_path = Path(__file__).parent.parent / 'vault'

    # Create and run scheduler
    # Check every hour (3600 seconds)
    scheduler = BriefingScheduler(str(vault_path), check_interval=3600)

    print(f"[Briefing Scheduler] Starting...")
    print(f"[Briefing Scheduler] Will generate briefing every Sunday at 11 PM")
    print(f"[Briefing Scheduler] Vault: {vault_path}")

    scheduler.run()


if __name__ == '__main__':
    main()
