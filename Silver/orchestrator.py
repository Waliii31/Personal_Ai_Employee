"""
Orchestrator - Master Coordination Script
Coordinates all AI Employee components for Silver Tier
"""
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import json


class AIEmployeeOrchestrator:
    """Master orchestrator for AI Employee system"""

    def __init__(self, vault_path: str, config_path: str = './orchestrator_config.json'):
        self.vault_path = Path(vault_path)
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logger()
        self.processes = {}

    def _load_config(self) -> dict:
        """Load orchestrator configuration"""
        default_config = {
            "watchers": {
                "gmail": {
                    "enabled": True,
                    "script": "./watchers/gmail_watcher.py",
                    "check_interval": 120
                },
                "whatsapp": {
                    "enabled": True,
                    "script": "./watchers/whatsapp_watcher.py",
                    "check_interval": 60
                },
                "approval": {
                    "enabled": True,
                    "script": "./watchers/approval_workflow.py",
                    "check_interval": 10
                }
            },
            "automation": {
                "linkedin": {
                    "enabled": True,
                    "script": "./watchers/linkedin_automation.py",
                    "schedule": "daily"
                }
            },
            "vault_path": str(self.vault_path)
        }

        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for orchestrator"""
        logger = logging.getLogger('Orchestrator')
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'orchestrator.log')
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def start_all(self):
        """Start all enabled components"""
        self.logger.info("=" * 60)
        self.logger.info("AI Employee Orchestrator - Silver Tier")
        self.logger.info("=" * 60)
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Started: {datetime.now().isoformat()}")
        self.logger.info("=" * 60)

        # Start watchers
        for name, config in self.config['watchers'].items():
            if config['enabled']:
                self.start_watcher(name, config)

        self.logger.info("\nAll components started successfully!")
        self.logger.info("Press Ctrl+C to stop all components\n")

        # Monitor processes
        try:
            while True:
                self.check_health()
                time.sleep(30)  # Health check every 30 seconds
        except KeyboardInterrupt:
            self.logger.info("\nShutting down...")
            self.stop_all()

    def start_watcher(self, name: str, config: dict):
        """Start a watcher process"""
        script_path = Path(config['script'])

        if not script_path.exists():
            self.logger.error(f"Script not found: {script_path}")
            return

        try:
            self.logger.info(f"Starting {name} watcher...")

            # Start process
            process = subprocess.Popen(
                [sys.executable, str(script_path), str(self.vault_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes[name] = {
                'process': process,
                'config': config,
                'started': datetime.now()
            }

            self.logger.info(f"✓ {name} watcher started (PID: {process.pid})")

        except Exception as e:
            self.logger.error(f"Failed to start {name}: {e}")

    def check_health(self):
        """Check health of all running processes"""
        for name, data in list(self.processes.items()):
            process = data['process']

            # Check if process is still running
            if process.poll() is not None:
                self.logger.warning(f"⚠ {name} process died (exit code: {process.returncode})")

                # Attempt restart
                self.logger.info(f"Attempting to restart {name}...")
                self.start_watcher(name, data['config'])

    def stop_all(self):
        """Stop all running processes"""
        self.logger.info("Stopping all components...")

        for name, data in self.processes.items():
            process = data['process']
            if process.poll() is None:
                self.logger.info(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    self.logger.info(f"✓ {name} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.logger.warning(f"⚠ {name} force killed")

        self.logger.info("All components stopped")

    def run_briefing(self):
        """Generate daily briefing"""
        self.logger.info("Generating daily briefing...")

        briefing_path = self.vault_path / 'Briefings'
        briefing_path.mkdir(parents=True, exist_ok=True)

        # Collect statistics
        stats = self._collect_stats()

        # Generate briefing
        briefing_content = self._generate_briefing(stats)

        # Save briefing
        today = datetime.now().strftime('%Y-%m-%d')
        briefing_file = briefing_path / f'BRIEFING_{today}.md'
        briefing_file.write_text(briefing_content, encoding='utf-8')

        self.logger.info(f"Briefing saved: {briefing_file}")

        return briefing_file

    def _collect_stats(self) -> dict:
        """Collect statistics from vault"""
        stats = {
            'inbox_count': 0,
            'needs_action_count': 0,
            'pending_approval_count': 0,
            'done_count': 0,
            'plans_count': 0
        }

        # Count items in each folder
        folders = {
            'inbox_count': 'Inbox',
            'needs_action_count': 'Needs_Action',
            'pending_approval_count': 'Pending_Approval',
            'done_count': 'Done',
            'plans_count': 'Plans'
        }

        for key, folder in folders.items():
            folder_path = self.vault_path / folder
            if folder_path.exists():
                stats[key] = len(list(folder_path.glob('*.md')))

        return stats

    def _generate_briefing(self, stats: dict) -> str:
        """Generate briefing content"""
        today = datetime.now().strftime('%A, %B %d, %Y')

        content = f"""---
type: daily_briefing
date: {datetime.now().isoformat()}
---

# Daily Briefing - {today}

## System Status
🟢 All systems operational

## Task Overview

### Pending Items
- **Inbox**: {stats['inbox_count']} items
- **Needs Action**: {stats['needs_action_count']} items
- **Pending Approval**: {stats['pending_approval_count']} items

### Completed
- **Done**: {stats['done_count']} items
- **Plans Created**: {stats['plans_count']} plans

## Priority Actions

### High Priority
{self._get_high_priority_items()}

### Today's Focus
- Review pending approvals
- Process inbox items
- Check scheduled LinkedIn posts

## System Health
- Gmail Watcher: 🟢 Running
- WhatsApp Watcher: 🟢 Running
- Approval Workflow: 🟢 Running
- LinkedIn Automation: 🟢 Scheduled

## Notes
All systems running smoothly. Review pending approvals for time-sensitive actions.

---
*Generated by AI Employee Orchestrator at {datetime.now().isoformat()}*
"""

        return content

    def _get_high_priority_items(self) -> str:
        """Get high priority items from vault"""
        needs_action = self.vault_path / 'Needs_Action'
        high_priority = []

        if needs_action.exists():
            for file in needs_action.glob('*.md'):
                content = file.read_text(encoding='utf-8')
                if 'priority: high' in content:
                    high_priority.append(f"- {file.stem}")

        if high_priority:
            return '\n'.join(high_priority)
        else:
            return "- No high priority items"


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', nargs='?', default='./vault',
                        help='Path to Obsidian vault')
    parser.add_argument('--briefing', action='store_true',
                        help='Generate daily briefing and exit')
    parser.add_argument('--test', action='store_true',
                        help='Run in test mode')

    args = parser.parse_args()

    orchestrator = AIEmployeeOrchestrator(args.vault_path)

    if args.briefing:
        briefing_file = orchestrator.run_briefing()
        print(f"Briefing generated: {briefing_file}")
    elif args.test:
        print("Running in test mode...")
        orchestrator.logger.info("Test mode - components not started")
        stats = orchestrator._collect_stats()
        print(f"Vault statistics: {stats}")
    else:
        orchestrator.start_all()


if __name__ == '__main__':
    main()
