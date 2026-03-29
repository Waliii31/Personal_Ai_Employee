---
type: accounting
task_type: record_expense
category: Office Supplies
priority: normal
created: 2026-03-14
---

# Record Business Expense - Office Supplies

## Expense Details

- **Vendor:** Office Depot
- **Date:** 2026-03-14
- **Amount:** $247.89
- **Category:** Office Supplies
- **Payment Method:** Company Credit Card

## Items Purchased

- Printer paper (5 reams) - $45.00
- Ink cartridges (2 sets) - $120.00
- Notebooks and pens - $35.50
- Desk organizers - $27.39
- Shipping - $20.00

**Total:** $247.89

## Receipt

Receipt #: OD-2026-03-14-1234
Attached: receipt_office_depot_20260314.pdf

## Tax Information

- Deductible: Yes
- Category: Office Expenses
- Tax Year: 2026

## Instructions for Claude

Please use the **accounting-assistant** skill to:
1. Create an approval request for this expense
2. Categorize as "Office Supplies"
3. Include receipt reference
4. Wait for human approval before recording in Odoo

## Expected Outcome

- Approval request created in `Pending_Approval/`
- After approval, expense recorded in Odoo
- Journal entry created
- Task moved to `Done/`

## Notes

- Regular monthly office supply order
- All items for business use
- Keep receipt for tax records
