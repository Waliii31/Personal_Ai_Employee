"""
Accounting Assistant Agent Skill
Processes financial tasks using Odoo MCP server
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class AccountingAssistant:
    """Agent skill for handling accounting operations via Odoo"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.accounting_dir = self.vault_path / 'Accounting'
        self.accounting_dir.mkdir(parents=True, exist_ok=True)

    def process_task(self, task_data: dict) -> dict:
        """
        Process an accounting task

        Args:
            task_data: Task information from action file

        Returns:
            Result dictionary with status and details
        """
        task_type = task_data.get('task_type', 'unknown')

        if task_type == 'create_invoice':
            return self._handle_create_invoice(task_data)
        elif task_type == 'record_expense':
            return self._handle_record_expense(task_data)
        elif task_type == 'financial_summary':
            return self._handle_financial_summary(task_data)
        elif task_type == 'unpaid_invoices':
            return self._handle_unpaid_invoices(task_data)
        else:
            return {
                'success': False,
                'error': f'Unknown task type: {task_type}',
            }

    def _handle_create_invoice(self, task_data: dict) -> dict:
        """Handle invoice creation request"""
        # Extract invoice details
        customer = task_data.get('customer_name')
        items = task_data.get('invoice_lines', [])
        due_date = task_data.get('due_date')

        if not customer or not items:
            return {
                'success': False,
                'error': 'Missing required fields: customer_name and invoice_lines',
            }

        # Create approval request
        approval_file = self._create_approval_request(
            'create_invoice',
            {
                'customer': customer,
                'items': items,
                'due_date': due_date,
                'total': sum(item.get('price', 0) * item.get('quantity', 1) for item in items),
            }
        )

        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': str(approval_file),
            'message': f'Invoice creation for {customer} requires approval',
        }

    def _handle_record_expense(self, task_data: dict) -> dict:
        """Handle expense recording request"""
        description = task_data.get('description')
        amount = task_data.get('amount')
        category = task_data.get('category', 'General')
        date = task_data.get('date')

        if not description or not amount:
            return {
                'success': False,
                'error': 'Missing required fields: description and amount',
            }

        # Create approval request
        approval_file = self._create_approval_request(
            'record_expense',
            {
                'description': description,
                'amount': amount,
                'category': category,
                'date': date or datetime.now().strftime('%Y-%m-%d'),
            }
        )

        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': str(approval_file),
            'message': f'Expense recording (${amount}) requires approval',
        }

    def _handle_financial_summary(self, task_data: dict) -> dict:
        """Handle financial summary request"""
        # Check if we have cached data
        summary_file = self.accounting_dir / 'financial_summary.json'

        if summary_file.exists():
            try:
                summary = json.loads(summary_file.read_text())
                return {
                    'success': True,
                    'summary': summary,
                    'source': 'cached',
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error reading cached summary: {e}',
                }
        else:
            return {
                'success': False,
                'error': 'No cached financial data. Run Odoo sync first.',
                'suggestion': 'Use Odoo MCP server to fetch live data',
            }

    def _handle_unpaid_invoices(self, task_data: dict) -> dict:
        """Handle unpaid invoices request"""
        # Check if we have cached data
        invoices_file = self.accounting_dir / 'unpaid_invoices.json'

        if invoices_file.exists():
            try:
                invoices = json.loads(invoices_file.read_text())
                return {
                    'success': True,
                    'count': len(invoices),
                    'invoices': invoices,
                    'source': 'cached',
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error reading cached invoices: {e}',
                }
        else:
            return {
                'success': False,
                'error': 'No cached invoice data. Run Odoo sync first.',
                'suggestion': 'Use Odoo MCP server to fetch live data',
            }

    def _create_approval_request(self, action_type: str, data: dict) -> Path:
        """Create an approval request file"""
        pending_approval = self.vault_path / 'Pending_Approval'
        pending_approval.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'APPROVAL_{action_type}_{timestamp}.md'
        filepath = pending_approval / filename

        content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Required: {action_type.replace('_', ' ').title()}

## Details

```json
{json.dumps(data, indent=2)}
```

## Instructions

To approve: Move this file to `Approved/` folder
To reject: Move this file to `Rejected/` folder

## MCP Command (for approval)

```
Use Odoo MCP server tool: {action_type}
Parameters: {json.dumps(data)}
```
"""

        filepath.write_text(content)
        return filepath


def main():
    """Main entry point for the skill"""
    import argparse

    parser = argparse.ArgumentParser(description='Accounting Assistant Skill')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--task-file', required=True, help='Path to task file')

    args = parser.parse_args()

    # Read task file
    task_file = Path(args.task_file)
    if not task_file.exists():
        print(json.dumps({
            'success': False,
            'error': f'Task file not found: {task_file}',
        }))
        sys.exit(1)

    # Parse task data from markdown frontmatter and content
    content = task_file.read_text()
    # Simple parsing - in production, use proper YAML parser
    task_data = {
        'task_type': 'financial_summary',  # Default
    }

    # Create assistant and process
    assistant = AccountingAssistant(args.vault)
    result = assistant.process_task(task_data)

    # Output result as JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
