"""
Odoo Sync Watcher
Periodically syncs Odoo financial data to local vault for offline access
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'Silver' / 'watchers'))
from base_watcher import BaseWatcher


class OdooSyncWatcher(BaseWatcher):
    """Syncs Odoo data to vault for offline access and faster queries"""

    def __init__(self, vault_path: str, odoo_client, check_interval: int = 3600):
        """
        Initialize Odoo sync watcher

        Args:
            vault_path: Path to vault
            odoo_client: Initialized OdooClient instance
            check_interval: Seconds between syncs (default: 3600 = 1 hour)
        """
        super().__init__(vault_path, check_interval)
        self.odoo_client = odoo_client
        self.accounting_dir = self.vault_path / 'Accounting'
        self.accounting_dir.mkdir(parents=True, exist_ok=True)

        # Track last sync time
        self.last_sync_file = self.accounting_dir / '.last_sync'
        self.last_sync = self._load_last_sync()

    def _load_last_sync(self) -> datetime:
        """Load last sync timestamp"""
        if self.last_sync_file.exists():
            try:
                timestamp = self.last_sync_file.read_text().strip()
                return datetime.fromisoformat(timestamp)
            except Exception:
                pass
        return datetime.min

    def _save_last_sync(self):
        """Save current sync timestamp"""
        self.last_sync_file.write_text(datetime.now().isoformat())

    def check_for_updates(self) -> list:
        """
        Check if sync is needed (runs every hour)

        Returns:
            List with single 'sync' item if sync needed, empty list otherwise
        """
        now = datetime.now()
        time_since_sync = (now - self.last_sync).total_seconds()

        # Sync if more than check_interval has passed
        if time_since_sync >= self.check_interval:
            self.logger.info(f'Sync needed (last sync: {self.last_sync})')
            return ['sync']

        return []

    def create_action_file(self, item) -> Path:
        """
        Sync Odoo data to vault

        Args:
            item: 'sync' indicator

        Returns:
            Path to sync summary file
        """
        try:
            self.logger.info('Starting Odoo data sync...')

            # Sync financial summary
            summary = self._sync_financial_summary()

            # Sync unpaid invoices
            invoices = self._sync_unpaid_invoices()

            # Sync recent expenses
            expenses = self._sync_recent_expenses()

            # Create sync summary
            sync_summary = {
                'timestamp': datetime.now().isoformat(),
                'summary': summary,
                'unpaid_invoices_count': len(invoices),
                'recent_expenses_count': len(expenses),
            }

            # Save sync summary
            summary_file = self.accounting_dir / 'sync_summary.json'
            summary_file.write_text(json.dumps(sync_summary, indent=2))

            # Update last sync time
            self._save_last_sync()
            self.last_sync = datetime.now()

            self.logger.info('Odoo data sync completed successfully')

            # Return summary file path (not creating action file, just syncing)
            return summary_file

        except Exception as e:
            self.logger.error(f'Error syncing Odoo data: {e}', exc_info=True)
            raise

    def _sync_financial_summary(self) -> dict:
        """Sync financial summary for current year"""
        try:
            # Get year-to-date summary
            start_date = f'{datetime.now().year}-01-01'
            summary = self.odoo_client.get_financial_summary(start_date)

            # Save to file
            summary_file = self.accounting_dir / 'financial_summary.json'
            summary_file.write_text(json.dumps(summary, indent=2))

            self.logger.info(f'Synced financial summary: Revenue ${summary["revenue"]:.2f}')
            return summary

        except Exception as e:
            self.logger.error(f'Error syncing financial summary: {e}')
            return {}

    def _sync_unpaid_invoices(self) -> list:
        """Sync unpaid invoices"""
        try:
            invoices = self.odoo_client.list_unpaid_invoices()

            # Save to file
            invoices_file = self.accounting_dir / 'unpaid_invoices.json'
            invoices_file.write_text(json.dumps(invoices, indent=2))

            total_outstanding = sum(inv['outstanding'] for inv in invoices)
            self.logger.info(f'Synced {len(invoices)} unpaid invoices (${total_outstanding:.2f} outstanding)')

            return invoices

        except Exception as e:
            self.logger.error(f'Error syncing unpaid invoices: {e}')
            return []

    def _sync_recent_expenses(self) -> list:
        """Sync expenses from last 30 days"""
        try:
            # Get last 30 days of expenses
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            expenses = self.odoo_client.search(
                'account.move',
                [
                    ['move_type', '=', 'entry'],
                    ['date', '>=', start_date.strftime('%Y-%m-%d')],
                    ['date', '<=', end_date.strftime('%Y-%m-%d')],
                ],
                ['name', 'date', 'amount_total', 'ref']
            )

            # Save to file
            expenses_file = self.accounting_dir / 'recent_expenses.json'
            expenses_file.write_text(json.dumps(expenses, indent=2))

            total_expenses = sum(abs(exp.get('amount_total', 0)) for exp in expenses)
            self.logger.info(f'Synced {len(expenses)} recent expenses (${total_expenses:.2f})')

            return expenses

        except Exception as e:
            self.logger.error(f'Error syncing recent expenses: {e}')
            return []


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Import OdooClient
    sys.path.append(str(Path(__file__).parent.parent / 'mcp-servers' / 'odoo-mcp'))
    from odoo_client import OdooClient

    # Initialize Odoo client
    odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
    odoo_db = os.getenv('ODOO_DB', 'odoo')
    odoo_user = os.getenv('ODOO_USERNAME')
    odoo_pass = os.getenv('ODOO_PASSWORD')

    if not odoo_user or not odoo_pass:
        print('Error: ODOO_USERNAME and ODOO_PASSWORD must be set')
        sys.exit(1)

    # Create and authenticate client
    client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_pass)

    try:
        client.authenticate()
    except Exception as e:
        print(f'Error authenticating with Odoo: {e}')
        sys.exit(1)

    # Get vault path
    vault_path = Path(__file__).parent.parent / 'vault'

    # Create and run watcher
    watcher = OdooSyncWatcher(str(vault_path), client, check_interval=3600)
    watcher.run()
