---
type: accounting
task_type: create_invoice
customer_name: Acme Corporation
priority: normal
created: 2026-03-14
---

# Create Invoice for Acme Corporation

## Customer Details
- **Name:** Acme Corporation
- **Contact:** John Smith
- **Email:** john@acme.com

## Invoice Items

| Description | Quantity | Unit Price |
|-------------|----------|------------|
| Consulting Services - Project Alpha | 40 hours | $150.00 |
| Software License - Annual | 1 | $500.00 |
| Technical Support - March | 1 | $200.00 |

**Total:** $6,700.00

## Payment Terms
- **Due Date:** 2026-04-30 (Net 30)
- **Payment Method:** Bank transfer or check

## Notes
- Project Alpha completed on schedule
- Software license includes 1 year of updates
- Technical support covers email and phone support

## Instructions for Claude

Please use the **accounting-assistant** skill to:
1. Create an approval request for this invoice
2. Include all line items with correct quantities and prices
3. Set the due date to 30 days from today
4. Wait for human approval before creating in Odoo

## Expected Outcome

- Approval request created in `Pending_Approval/`
- After approval, invoice created in Odoo
- Invoice number assigned
- Customer notified (optional)
- Task moved to `Done/`
