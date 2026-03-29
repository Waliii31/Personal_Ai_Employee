# Business Auditor Skill

Agent skill for generating CEO briefings and business analysis.

## Purpose

Analyzes business operations and generates comprehensive reports including:
- Weekly CEO briefings
- Financial performance analysis
- Task completion tracking
- Bottleneck detection
- Subscription usage auditing
- Proactive cost optimization suggestions

## Usage

### Command Line

```bash
python business_auditor.py --vault /path/to/vault --report-type weekly_briefing
```

### From Claude Code

Automatically invoked by the briefing scheduler watcher every Sunday at 11 PM.

## Report Types

### weekly_briefing

Comprehensive weekly business audit including:
- Executive summary (one-line overview)
- Financial performance (revenue, MTD, YTD, trends)
- Completed tasks (from Done folder)
- Bottlenecks (tasks taking longer than expected)
- Subscription audit (unused subscriptions)
- Proactive suggestions (cost optimization, upcoming deadlines)

**Output:** Markdown report in `vault/Briefings/`

### financial_analysis

Detailed financial analysis using Odoo data:
- Revenue breakdown by customer
- Expense breakdown by category
- Profit margins
- Cash flow analysis
- Unpaid invoices aging

### task_analysis

Task completion analysis:
- Tasks completed this week
- Average completion time
- Tasks by category
- Bottlenecks (tasks taking >expected time)

### subscription_audit

Audit business subscriptions for unused services:
- Parse bank transactions from Odoo
- Match against subscription patterns
- Flag subscriptions with no activity in 30+ days
- Calculate potential savings

## Data Sources

### Odoo Financial Data
- Revenue from invoices
- Expenses from journal entries
- Unpaid invoices
- Bank transactions

### Vault Task Data
- Completed tasks in `Done/` folder
- Task metadata (created, completed, duration)
- Task categories and tags

### External Data
- Subscription patterns (Netflix, Adobe, etc.)
- Industry benchmarks (optional)

## Output Format

### Weekly Briefing Structure

```markdown
# Weekly CEO Briefing - [Date Range]

## Executive Summary
[One-line overview of the week]

## Financial Performance
- Revenue: $X,XXX (↑/↓ X% vs last week)
- Expenses: $X,XXX
- Profit: $X,XXX
- MTD Revenue: $X,XXX
- YTD Revenue: $X,XXX

## Completed Tasks (X tasks)
- [x] Task 1 (completed in X hours)
- [x] Task 2 (completed in X hours)
...

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Task A | 2 hours | 8 hours | +6 hours |

## Subscription Audit
⚠️ Unused subscriptions detected:
- Netflix ($15.99/mo) - No activity in 45 days
- Adobe Creative Cloud ($52.99/mo) - No activity in 60 days

**Potential savings:** $68.98/month = $827.76/year

## Proactive Suggestions
1. Cancel unused Netflix subscription (save $191.88/year)
2. Invoice #INV-123 overdue by 15 days - follow up with customer
3. Q1 tax deadline in 14 days - prepare documents
```

## Bottleneck Detection

Identifies tasks taking longer than expected:

1. Parse task metadata from Done folder
2. Calculate actual completion time
3. Compare against expected time (from task metadata or defaults)
4. Flag tasks with >50% delay
5. Categorize by reason (if available)

## Subscription Audit Logic

1. Retrieve bank transactions from Odoo (last 90 days)
2. Match against subscription patterns:
   - Recurring charges (same amount, same merchant)
   - Known subscription merchants (Netflix, Adobe, etc.)
3. Check for activity indicators:
   - Related project files modified
   - Mentions in completed tasks
   - Usage logs (if available)
4. Flag subscriptions with no activity in 30+ days
5. Calculate potential savings

## Integration

### With Odoo MCP Server
- Retrieves financial data
- Accesses bank transactions

### With Vault
- Reads completed tasks from `Done/`
- Writes briefings to `Briefings/`
- Accesses cached Odoo data from `Accounting/`

## Dependencies

- Python 3.8+
- Access to vault filesystem
- Odoo MCP server (for live financial data)
- Cached Odoo data (from odoo_sync_watcher)
