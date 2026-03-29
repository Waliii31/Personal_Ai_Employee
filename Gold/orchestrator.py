"""
Gold Tier Orchestrator
Enhanced orchestrator with all Gold Tier watchers and capabilities
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
import json
import logging


class GoldOrchestrator:
    """Main orchestrator for Gold Tier Personal AI Employee"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.vault_path = Path(self.config['vault_path'])
        self.watchers = []
        self.running = False
        self.logger = self._setup_logger()

    def _load_config(self) -> dict:
        """Load orchestrator configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f'Config file not found: {self.config_path}')

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _setup_logger(self) -> logging.Logger:
        """Setup orchestrator logger"""
        logger = logging.getLogger('GoldOrchestrator')
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

    def initialize_watchers(self):
        """Initialize all configured watchers"""
        self.logger.info('Initializing watchers...')

        for watcher_config in self.config.get('watchers', []):
            if not watcher_config.get('enabled', True):
                self.logger.info(f'Skipping disabled watcher: {watcher_config["name"]}')
                continue

            try:
                watcher = self._create_watcher(watcher_config)
                if watcher:
                    self.watchers.append({
                        'name': watcher_config['name'],
                        'instance': watcher,
                        'thread': None,
                    })
                    self.logger.info(f'Initialized watcher: {watcher_config["name"]}')
            except Exception as e:
                self.logger.error(f'Failed to initialize {watcher_config["name"]}: {e}')

        self.logger.info(f'Initialized {len(self.watchers)} watchers')

    def _create_watcher(self, config: dict):
        """Create watcher instance from config"""
        watcher_type = config['type']
        vault_path = str(self.vault_path)

        # Import watcher classes
        sys.path.append(str(Path(__file__).parent / 'watchers'))
        sys.path.append(str(Path(__file__).parent.parent / 'Silver' / 'watchers'))

        if watcher_type == 'gmail':
            from gmail_watcher import GmailWatcher
            # Would need Gmail credentials
            return None  # Placeholder

        elif watcher_type == 'whatsapp':
            from whatsapp_watcher import WhatsAppWatcher
            # Would need WhatsApp setup
            return None  # Placeholder

        elif watcher_type == 'facebook':
            from facebook_watcher import FacebookWatcher
            # Would need Facebook API client
            return None  # Placeholder

        elif watcher_type == 'instagram':
            from instagram_watcher import InstagramWatcher
            # Would need Instagram API client
            return None  # Placeholder

        elif watcher_type == 'twitter':
            from twitter_watcher import TwitterWatcher
            # Would need Twitter API client
            return None  # Placeholder

        elif watcher_type == 'odoo_sync':
            from odoo_sync_watcher import OdooSyncWatcher
            # Would need Odoo client
            return None  # Placeholder

        elif watcher_type == 'briefing_scheduler':
            from briefing_scheduler import BriefingScheduler
            return BriefingScheduler(vault_path, config.get('check_interval', 3600))

        elif watcher_type == 'approval_workflow':
            from approval_workflow import ApprovalWorkflow
            return ApprovalWorkflow(vault_path, config.get('check_interval', 60))

        return None

    def start(self):
        """Start all watchers"""
        self.logger.info('Starting Gold Tier Orchestrator...')
        self.running = True

        # Start each watcher in its own thread
        for watcher in self.watchers:
            if watcher['instance']:
                thread = threading.Thread(
                    target=watcher['instance'].run,
                    name=watcher['name'],
                    daemon=True
                )
                thread.start()
                watcher['thread'] = thread
                self.logger.info(f'Started watcher: {watcher["name"]}')

        self.logger.info('All watchers started')
        self.logger.info('Press Ctrl+C to stop')

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Received shutdown signal')
            self.stop()

    def stop(self):
        """Stop all watchers"""
        self.logger.info('Stopping orchestrator...')
        self.running = False

        # Wait for threads to finish
        for watcher in self.watchers:
            if watcher['thread'] and watcher['thread'].is_alive():
                self.logger.info(f'Waiting for {watcher["name"]} to stop...')
                watcher['thread'].join(timeout=5)

        self.logger.info('Orchestrator stopped')

    def status(self) -> dict:
        """Get orchestrator status"""
        return {
            'running': self.running,
            'watchers': [
                {
                    'name': w['name'],
                    'active': w['thread'].is_alive() if w['thread'] else False,
                }
                for w in self.watchers
            ],
            'vault_path': str(self.vault_path),
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Gold Tier Orchestrator')
    parser.add_argument(
        '--config',
        default='orchestrator_config.json',
        help='Path to config file'
    )

    args = parser.parse_args()

    # Create and start orchestrator
    orchestrator = GoldOrchestrator(args.config)
    orchestrator.initialize_watchers()
    orchestrator.start()


if __name__ == '__main__':
    main()
