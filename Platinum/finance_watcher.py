"""
Finance Watcher - Monitors financial transactions and creates action files
Can integrate with banking APIs or monitor CSV files as outlined in the Platinum tier document
"""

import time
import logging
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher
from typing import List, Dict, Any
import os
import requests
from decimal import Decimal


class FinanceWatcher(BaseWatcher):
    """
    Finance watcher implementation that monitors financial transactions
    and creates action files for the AI Employee to process.
    Supports both API-based banking integrations and CSV file monitoring.
    """

    def __init__(self, vault_path: str, bank_api_config: dict = None,
                 csv_monitor_dirs: List[str] = None, check_interval: int = 300):
        """
        Initialize the finance watcher

        Args:
            vault_path: Path to the Obsidian vault
            bank_api_config: Configuration for bank API integration
            csv_monitor_dirs: List of directories to monitor for CSV files
            check_interval: How often to check for new transactions (in seconds)
        """
        super().__init__(vault_path, check_interval)

        # Configuration for bank API
        self.bank_api_config = bank_api_config or {}

        # Directories to monitor for CSV files
        self.csv_monitor_dirs = [Path(d) for d in csv_monitor_dirs or []]

        # Track processed transaction IDs to avoid duplicates
        self.processed_transaction_ids = set()

        # Subscription patterns for identifying recurring payments
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'amazon.com': 'Amazon Prime',
            'google.com': 'Google One',
            'apple.com': 'Apple Services',
            'microsoft.com': 'Microsoft 365',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'zoom.us': 'Zoom'
        }

        # Load previously processed IDs if available
        self._load_processed_ids()

    def _load_processed_ids(self):
        """
        Load previously processed transaction IDs from a file to avoid reprocessing
        """
        processed_file = self.vault_path / "processed_transactions.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_transaction_ids = set(data.get('processed_ids', []))
            except Exception as e:
                self.logger.warning(f"Could not load processed transaction IDs: {e}")

    def _save_processed_ids(self):
        """
        Save processed transaction IDs to a file
        """
        processed_file = self.vault_path / "processed_transactions.json"
        try:
            with open(processed_file, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_transaction_ids),
                    'last_updated': datetime.now().isoformat()
                }, f)
        except Exception as e:
            self.logger.error(f"Could not save processed transaction IDs: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new financial transactions from APIs and CSV files

        Returns:
            List of transaction dictionaries that need processing
        """
        new_transactions = []

        # Check bank API if configured
        if self.bank_api_config:
            api_transactions = self._check_bank_api()
            new_transactions.extend(api_transactions)

        # Check CSV files in monitored directories
        csv_transactions = self._check_csv_files()
        new_transactions.extend(csv_transactions)

        # Filter out already processed transactions
        filtered_transactions = []
        for transaction in new_transactions:
            trans_id = transaction.get('id', str(hash(json.dumps(transaction, sort_keys=True))))
            if trans_id not in self.processed_transaction_ids:
                transaction['id'] = trans_id
                filtered_transactions.append(transaction)
                self.processed_transaction_ids.add(trans_id)

        # Save processed IDs
        self._save_processed_ids()

        return filtered_transactions

    def _check_bank_api(self) -> List[Dict[str, Any]]:
        """
        Check bank API for new transactions

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Example implementation for a generic banking API
        # This would need to be customized for specific banks/APIs
        if 'api_base_url' in self.bank_api_config:
            try:
                # Prepare headers with authentication
                headers = {
                    'Authorization': f"Bearer {self.bank_api_config.get('access_token', '')}",
                    'Content-Type': 'application/json'
                }

                # Define date range for recent transactions
                end_date = datetime.now()
                start_date = end_date - timedelta(days=1)  # Last 24 hours

                # Example API call (this is a generic example)
                params = {
                    'from_date': start_date.strftime('%Y-%m-%d'),
                    'to_date': end_date.strftime('%Y-%m-%d'),
                    'limit': 50
                }

                response = requests.get(
                    f"{self.bank_api_config['api_base_url']}/transactions",
                    headers=headers,
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    raw_transactions = data.get('transactions', [])

                    for raw_trans in raw_transactions:
                        transaction = self._parse_api_transaction(raw_trans)
                        if transaction:
                            transactions.append(transaction)
                else:
                    self.logger.error(f"Bank API request failed: {response.status_code} - {response.text}")

            except Exception as e:
                self.logger.error(f"Error checking bank API: {e}")

        return transactions

    def _parse_api_transaction(self, raw_transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a raw transaction from the bank API into a standardized format

        Args:
            raw_transaction: Raw transaction data from API

        Returns:
            Standardized transaction dictionary
        """
        try:
            # Standardize the transaction format
            transaction = {
                'date': raw_transaction.get('date', raw_transaction.get('transactionDate', '')),
                'description': raw_transaction.get('description', raw_transaction.get('merchantName', '')),
                'amount': float(raw_transaction.get('amount', raw_transaction.get('transactionAmount', 0))),
                'currency': raw_transaction.get('currency', 'USD'),
                'category': raw_transaction.get('category', ''),
                'type': raw_transaction.get('type', 'debit' if raw_transaction.get('amount', 0) < 0 else 'credit'),
                'account_mask': raw_transaction.get('account', {}).get('mask', ''),
                'status': raw_transaction.get('status', 'posted')
            }

            # Additional parsing based on available fields
            if 'merchant' in raw_transaction:
                transaction['merchant'] = raw_transaction['merchant']

            return transaction

        except Exception as e:
            self.logger.error(f"Error parsing API transaction: {e}")
            return None

    def _check_csv_files(self) -> List[Dict[str, Any]]:
        """
        Check monitored directories for new CSV transaction files

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        for csv_dir in self.csv_monitor_dirs:
            if not csv_dir.exists():
                continue

            # Look for CSV files modified in the last check interval
            cutoff_time = time.time() - self.check_interval
            csv_files = [f for f in csv_dir.glob("*.csv") if f.stat().st_mtime > cutoff_time]

            for csv_file in csv_files:
                file_transactions = self._parse_csv_file(csv_file)
                transactions.extend(file_transactions)

        return transactions

    def _parse_csv_file(self, csv_file: Path) -> List[Dict[str, Any]]:
        """
        Parse a CSV file containing transaction data

        Args:
            csv_file: Path to the CSV file

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                # Try to detect the delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(file, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=1):
                    try:
                        transaction = self._parse_csv_row(row, csv_file.name, row_num)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        self.logger.warning(f"Error parsing row {row_num} in {csv_file.name}: {e}")
                        continue

        except Exception as e:
            self.logger.error(f"Error reading CSV file {csv_file}: {e}")

        return transactions

    def _parse_csv_row(self, row: Dict[str, str], filename: str, row_num: int) -> Dict[str, Any]:
        """
        Parse a single row from a CSV file into a transaction dictionary

        Args:
            row: Dictionary representing a CSV row
            filename: Name of the CSV file
            row_num: Row number in the file

        Returns:
            Transaction dictionary
        """
        # Common column name mappings
        date_fields = ['date', 'transaction_date', 'trans_date', 'posting_date', 'dt']
        description_fields = ['description', 'memo', 'payee', 'merchant', 'name', 'transaction']
        amount_fields = ['amount', 'transaction_amount', 'trans_amount', 'amt', 'value']

        # Find the actual column names in the row
        date_col = next((col for col in date_fields if col.lower() in [c.lower() for c in row.keys()]), None)
        desc_col = next((col for col in description_fields if col.lower() in [c.lower() for c in row.keys()]), None)
        amt_col = next((col for col in amount_fields if col.lower() in [c.lower() for c in row.keys()]), None)

        if not all([date_col, desc_col, amt_col]):
            self.logger.warning(f"Could not map columns in row {row_num} of {filename}")
            return None

        try:
            # Extract values
            date_str = row[date_col].strip() if row[date_col] else ''
            description = row[desc_col].strip() if row[desc_col] else ''
            amount_str = row[amt_col].strip() if row[amt_col] else ''

            # Clean and parse amount
            amount_str = ''.join(c for c in amount_str if c.isdigit() or c in '.-')
            amount = float(amount_str) if amount_str else 0.0

            # Create transaction
            transaction = {
                'date': date_str,
                'description': description,
                'amount': amount,
                'currency': 'USD',  # Default, could be inferred from other fields
                'type': 'debit' if amount < 0 else 'credit',
                'source_file': filename,
                'source_row': row_num,
                'status': 'imported'
            }

            return transaction

        except ValueError as e:
            self.logger.warning(f"Invalid numeric value in row {row_num} of {filename}: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Error parsing row {row_num} of {filename}: {e}")
            return None

    def create_action_file(self, transaction) -> Path:
        """
        Create an action file for a financial transaction

        Args:
            transaction: Dictionary containing transaction details

        Returns:
            Path to the created action file
        """
        # Analyze the transaction
        analysis = self._analyze_transaction(transaction)

        # Create markdown content
        content = f"""---
type: financial_transaction
transaction_id: {transaction['id']}
date: {transaction.get('date', datetime.now().isoformat())}
amount: {transaction.get('amount', 0):.2f}
currency: {transaction.get('currency', 'USD')}
description: "{transaction.get('description', 'N/A')}"
category: {analysis['category']}
status: pending
priority: {analysis['priority']}
---

# Financial Transaction Detected

## Transaction Details
- **Date:** {transaction.get('date', 'Unknown')}
- **Description:** {transaction.get('description', 'N/A')}
- **Amount:** {transaction.get('currency', 'USD')} {abs(transaction.get('amount', 0)):.2f} ({'Debit' if transaction.get('amount', 0) < 0 else 'Credit'})
- **Category:** {analysis['category']}
- **Priority:** {analysis['priority']}

## Analysis
- **Type:** {analysis['type']}
- **Merchant:** {analysis['merchant']}
- **Subscription:** {analysis['is_subscription']}
- **Unusual Amount:** {analysis['unusual_amount']}
- **New Merchant:** {analysis['new_merchant']}

## Recommended Actions
- [ ] Review transaction for validity
- [ ] Verify with business records
- [ ] Approve or flag as fraudulent
- [ ] Update accounting records

## Context
{analysis['context']}

## Potential Issues
{chr(10).join(f"- {issue}" for issue in analysis['issues']) if analysis['issues'] else '- No issues detected'}

## Related Transactions
{chr(10).join(f"- {related}" for related in analysis['related']) if analysis['related'] else '- No related transactions found'}
"""

        # Create a unique filename based on the transaction ID and details
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean description for filename
        clean_description = "".join(c for c in transaction.get('description', 'unknown') if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_description = clean_description[:50]  # Limit length
        action_filename = f"FINANCE_{timestamp}_{transaction['id']}_{clean_description}.md"
        action_filepath = self.needs_action / action_filename

        # Write the content to the action file
        action_filepath.write_text(content, encoding='utf-8')

        return action_filepath

    def _analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a transaction to determine category, priority, and potential issues

        Args:
            transaction: Transaction dictionary

        Returns:
            Analysis results dictionary
        """
        description = transaction.get('description', '').lower()
        amount = abs(transaction.get('amount', 0))

        # Determine transaction type
        if amount > 1000:
            trans_type = 'large'
        elif amount > 100:
            trans_type = 'medium'
        else:
            trans_type = 'small'

        # Check for subscription patterns
        is_subscription = False
        merchant_name = 'Unknown'
        for pattern, name in self.subscription_patterns.items():
            if pattern in description:
                is_subscription = True
                merchant_name = name
                break

        # Determine priority
        priority = 'low'
        if is_subscription:
            priority = 'medium'  # Regular subscriptions are important to track
        elif amount > 500:
            priority = 'high'  # Large transactions need review
        elif any(word in description for word in ['fraud', 'dispute', 'chargeback']):
            priority = 'critical'  # Fraud indicators are critical
        elif amount < 1:  # Very small charges might be suspicious
            priority = 'medium'

        # Check if amount is unusual compared to typical spending
        unusual_amount = self._is_unusual_amount(amount, description)

        # Check if this is a new merchant
        new_merchant = self._is_new_merchant(description)

        # Identify potential issues
        issues = []
        if amount > 1000:
            issues.append("Large transaction - requires review")
        if any(word in description for word in ['fraud', 'dispute', 'chargeback']):
            issues.append("Potential fraud indicator detected")
        if amount < 1 and amount > 0:
            issues.append("Very small charge - possible authorization hold or fraud")
        if 'foreign' in description or 'intl' in description:
            issues.append("International transaction - check for authorization")

        # Identify related transactions
        related = self._find_related_transactions(transaction)

        # Generate context
        context_parts = []
        if is_subscription:
            context_parts.append(f"This appears to be a recurring subscription payment for {merchant_name}.")
        if unusual_amount:
            context_parts.append("The amount is unusual compared to typical spending in this category.")
        if new_merchant:
            context_parts.append("This is a new merchant that hasn't been seen before.")

        if not context_parts:
            context_parts.append("Transaction appears to be routine.")

        return {
            'category': self._categorize_transaction(description),
            'type': trans_type,
            'merchant': merchant_name,
            'is_subscription': is_subscription,
            'unusual_amount': unusual_amount,
            'new_merchant': new_merchant,
            'priority': priority,
            'issues': issues,
            'related': related,
            'context': ' '.join(context_parts)
        }

    def _categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description

        Args:
            description: Transaction description

        Returns:
            Category string
        """
        categories = {
            'food': ['restaurant', 'cafe', 'food', 'grocery', 'market', 'deli', 'pizza', 'burger'],
            'transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus', 'train'],
            'shopping': ['amazon', 'walmart', 'target', 'store', 'retail', 'shop'],
            'services': ['service', 'fee', 'charge', 'payment', 'bill', 'utility'],
            'healthcare': ['hospital', 'clinic', 'doctor', 'pharmacy', 'medical'],
            'entertainment': ['movie', 'theater', 'concert', 'streaming', 'game', 'app'],
            'travel': ['hotel', 'airline', 'flight', 'airbnb', 'resort', 'rental'],
            'charity': ['donation', 'charity', 'nonprofit', 'fundraiser']
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in description:
                    return category

        return 'other'

    def _is_unusual_amount(self, amount: float, description: str) -> bool:
        """
        Check if the transaction amount is unusual for this category/merchant

        Args:
            amount: Transaction amount
            description: Transaction description

        Returns:
            Boolean indicating if amount is unusual
        """
        # This would normally check historical data
        # For now, we'll use simple heuristics
        category = self._categorize_transaction(description)

        # Typical thresholds by category (these would come from historical data in practice)
        thresholds = {
            'food': 100,  # More than $100 for food is unusual
            'transportation': 100,  # More than $100 for transport is unusual
            'shopping': 200,  # More than $200 for shopping is unusual
            'services': 500,  # More than $500 for services is unusual
            'healthcare': 300,  # More than $300 for healthcare is unusual
            'entertainment': 100,  # More than $100 for entertainment is unusual
            'travel': 500,  # More than $500 for travel is unusual
            'charity': 200,  # More than $200 for charity is unusual
        }

        typical_max = thresholds.get(category, 200)
        return amount > typical_max

    def _is_new_merchant(self, description: str) -> bool:
        """
        Check if this is a new merchant that hasn't been seen before

        Args:
            description: Transaction description

        Returns:
            Boolean indicating if merchant is new
        """
        # This would normally check historical data
        # For now, we'll return False as we don't have historical data
        return False

    def _find_related_transactions(self, transaction: Dict[str, Any]) -> List[str]:
        """
        Find potentially related transactions

        Args:
            transaction: Transaction dictionary

        Returns:
            List of related transaction descriptions
        """
        # This would normally check for related transactions in historical data
        # For now, we'll return an empty list
        return []


def main():
    """
    Example usage of the finance watcher
    """
    import argparse

    parser = argparse.ArgumentParser(description='Finance Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to the vault directory')
    parser.add_argument('--csv-dirs', nargs='+', help='Directories to monitor for CSV files')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create and run the finance watcher
    watcher = FinanceWatcher(
        vault_path=args.vault,
        csv_monitor_dirs=args.csv_dirs,
        check_interval=args.interval
    )

    # Run the watcher (this will run indefinitely)
    watcher.run()


if __name__ == "__main__":
    main()