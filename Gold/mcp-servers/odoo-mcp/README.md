# Odoo MCP Server

MCP server providing Odoo accounting integration for Claude Code.

## Features

- Create customer invoices
- Record business expenses
- Get financial summaries (revenue, expenses, profit)
- List unpaid invoices
- Generate comprehensive financial reports

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables in `.env`:
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
```

3. Ensure Odoo is running (see `../odoo-integration/setup_guide.md`)

## Usage with Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:/Personal_Ai_Employee/Gold/mcp-servers/odoo-mcp/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "your_username",
        "ODOO_PASSWORD": "your_password"
      }
    }
  }
}
```

## Available Tools

### create_invoice
Create a customer invoice in Odoo.

**Parameters:**
- `customer_name` (string): Customer name
- `invoice_lines` (array): Line items with description, quantity, price
- `due_date` (string, optional): Due date in YYYY-MM-DD format

**Example:**
```javascript
{
  "customer_name": "Acme Corp",
  "invoice_lines": [
    {
      "description": "Consulting services",
      "quantity": 10,
      "price": 150
    }
  ],
  "due_date": "2026-04-15"
}
```

### record_expense
Record a business expense.

**Parameters:**
- `description` (string): Expense description
- `amount` (number): Expense amount
- `category` (string, optional): Expense category
- `date` (string, optional): Date in YYYY-MM-DD format

### get_financial_summary
Get financial summary for a date range.

**Parameters:**
- `start_date` (string, optional): Start date
- `end_date` (string, optional): End date

**Returns:**
- Revenue, expenses, profit, receivables
- Invoice and expense counts

### list_unpaid_invoices
List all unpaid or partially paid invoices.

**Returns:**
- Array of unpaid invoices with customer, date, amount, outstanding balance

### generate_financial_report
Generate comprehensive financial report.

**Parameters:**
- `start_date` (string, optional): Start date
- `end_date` (string, optional): End date

**Returns:**
- Financial summary
- List of unpaid invoices
- Generated timestamp

## Testing

```bash
npm test
```

## Troubleshooting

### Authentication errors
- Verify Odoo is running: `docker-compose ps`
- Check credentials in `.env`
- Ensure user has accounting permissions

### Connection errors
- Check ODOO_URL is correct
- Verify port 8069 is accessible
- Check Odoo logs: `docker-compose logs odoo`

### API errors
- Check Odoo accounting module is installed
- Verify chart of accounts is configured
- Check user has proper access rights
