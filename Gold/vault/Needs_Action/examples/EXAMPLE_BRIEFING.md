---
type: business_audit
task_type: weekly_briefing
priority: high
created: 2026-03-14
---

# Generate Weekly CEO Briefing

## Task

Generate comprehensive weekly CEO briefing for the period:
**March 7 - March 14, 2026**

## Required Sections

### 1. Executive Summary
One-line overview of the week's performance

### 2. Financial Performance
- Revenue (this week)
- Expenses (this week)
- Profit (this week)
- Month-to-date totals
- Year-to-date totals
- Comparison to targets

### 3. Completed Tasks
List of tasks completed this week from `Done/` folder

### 4. Bottlenecks
Tasks that took longer than expected with analysis

### 5. Subscription Audit
- Active subscriptions
- Usage analysis
- Unused subscriptions (30+ days)
- Potential cost savings

### 6. Proactive Suggestions
- Cost optimization opportunities
- Upcoming deadlines
- Process improvements
- Revenue opportunities

## Data Sources

- **Odoo Financial Data:** `vault/Accounting/financial_summary.json`
- **Completed Tasks:** `vault/Done/*.md`
- **Bank Transactions:** Odoo bank statements
- **Previous Briefings:** `vault/Briefings/`

## Instructions for Claude

Please use the **business-auditor** skill to:
1. Analyze all data sources
2. Generate comprehensive briefing
3. Include actionable insights
4. Save to `vault/Briefings/CEO_BRIEFING_YYYYMMDD.md`
5. Move this task to `Done/`

## Expected Outcome

- Briefing file created in `Briefings/`
- All sections complete with accurate data
- Proactive suggestions included
- Task moved to `Done/`

## Success Criteria

- Financial data matches Odoo
- All completed tasks listed
- Bottlenecks identified with root cause
- At least 3 proactive suggestions
- Actionable recommendations

## Notes

- This briefing is typically generated automatically every Sunday at 11 PM
- Manual generation can be triggered anytime
- Review previous briefings for format consistency
