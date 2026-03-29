# Accounting Assistant Skill

Agent skill for processing financial tasks using Odoo integration.

## Purpose

Handles accounting operations including:
- Creating customer invoices
- Recording business expenses
- Retrieving financial summaries
- Listing unpaid invoices

## Usage

This skill is invoked by Claude Code when processing accounting-related tasks from the vault.

### Command Line

```bash
python accounting_assistant.py --vault /path/to/vault --task-file /path/to/task.md
```

### From Claude Code

The skill is automatically available when configured in the orchestrator. Claude can invoke it when processing tasks in the `Needs_Action` folder that are tagged with accounting-related metadata.

## Task Types

### create_invoice

Create a customer invoice in Odoo.

**Required fields:**
- `customer_name`: Customer name
- `invoice_lines`: Array of line items with `description`, `quantity`, `price`

**Optional fields:**
- `due_date`: Invoice due date (YYYY-MM-DD)

**Example task file:**

```markdown
---
type: accounting
task_type: create_invoice
customer_name: Acme Corp
---

# Create Invoice for Acme Corp

Invoice lines:
- Consulting services: 10 hours @ $150/hr
- Software license: 1 @ $500

Due date: 2026-04-15
```

### record_expense

Record a business expense.

**Required fields:**
- `description`: Expense description
- `amount`: Expense amount

**Optional fields:**
- `category`: Expense category
- `date`: Expense date (YYYY-MM-DD)

### financial_summary

Get financial summary (revenue, expenses, profit).

Uses cached data from Odoo sync. For live data, use Odoo MCP server directly.

### unpaid_invoices

List all unpaid or partially paid invoices.

Uses cached data from Odoo sync. For live data, use Odoo MCP server directly.

## Approval Workflow

Financial operations (create_invoice, record_expense) require human approval:

1. Skill creates approval request in `Pending_Approval/`
2. Human reviews and moves to `Approved/` or `Rejected/`
3. Approval workflow watcher executes approved actions via Odoo MCP

## Integration

### With Odoo MCP Server

The skill creates approval requests that include MCP commands. When approved, the approval workflow watcher executes these commands using the Odoo MCP server.

### With Vault

- Reads tasks from `Needs_Action/`
- Creates approval requests in `Pending_Approval/`
- Uses cached data from `Accounting/` folder

## Output Format

Returns JSON with:

```json
{
  "success": true,
  "status": "pending_approval",
  "approval_file": "/path/to/approval.md",
  "message": "Invoice creation requires approval"
}
```

## Error Handling

- Missing required fields: Returns error with field names
- No cached data: Suggests using Odoo MCP directly
- Invalid task type: Returns error with supported types

## Dependencies

- Python 3.8+
- Access to vault filesystem
- Odoo MCP server (for live data)
- Approval workflow watcher (for executing approved actions)
