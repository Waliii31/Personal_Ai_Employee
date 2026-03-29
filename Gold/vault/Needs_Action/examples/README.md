# Example Task Files

This directory contains example task files to help you get started with Gold Tier.

## Available Examples

### 1. EXAMPLE_INVOICE.md
Create a customer invoice in Odoo.

**Use case:** Billing clients for services or products

**What it does:**
- Creates invoice with line items
- Sets payment terms and due date
- Requires approval before creating in Odoo

**To use:**
```bash
cp EXAMPLE_INVOICE.md ../INVOICE_001.md
# Edit with your customer details
# Process with Claude Code
```

### 2. EXAMPLE_EXPENSE.md
Record a business expense.

**Use case:** Tracking business expenses for accounting

**What it does:**
- Records expense with category
- Includes receipt reference
- Requires approval before recording in Odoo

**To use:**
```bash
cp EXAMPLE_EXPENSE.md ../EXPENSE_001.md
# Edit with your expense details
# Process with Claude Code
```

### 3. EXAMPLE_SOCIAL_POST.md
Post to social media platforms.

**Use case:** Multi-platform social media posting

**What it does:**
- Drafts post for Facebook and Twitter
- Validates content and character limits
- Creates approval request
- Posts to platforms after approval

**To use:**
```bash
cp EXAMPLE_SOCIAL_POST.md ../POST_001.md
# Edit with your content
# Process with Claude Code
```

### 4. EXAMPLE_BRIEFING.md
Generate weekly CEO briefing.

**Use case:** Business intelligence and reporting

**What it does:**
- Analyzes financial performance
- Reviews completed tasks
- Detects bottlenecks
- Audits subscriptions
- Provides proactive suggestions

**To use:**
```bash
cp EXAMPLE_BRIEFING.md ../BRIEFING_001.md
# Process with Claude Code
# Or wait for automatic Sunday 11 PM generation
```

## Task File Structure

All task files follow this structure:

```markdown
---
type: task_category
task_type: specific_task
priority: normal
created: YYYY-MM-DD
---

# Task Title

## Task Details
[Description of what needs to be done]

## Instructions for Claude
[Specific instructions for processing]

## Expected Outcome
[What should happen when complete]
```

## Task Types

### Accounting Tasks
- `type: accounting`
- `task_type: create_invoice` or `record_expense`
- Processed by: accounting-assistant skill
- Requires: Odoo MCP server

### Social Media Tasks
- `type: social_media`
- `task_type: draft_post` or `post_to_platform`
- Processed by: social-media-manager skill
- Requires: Social Media MCP server

### Business Audit Tasks
- `type: business_audit`
- `task_type: weekly_briefing`
- Processed by: business-auditor skill
- Requires: Cached Odoo data

## Processing Workflow

1. **Create Task**
   - Copy example or create new file
   - Edit with your details
   - Save in `vault/Needs_Action/`

2. **Claude Processes**
   - Reads task file
   - Invokes appropriate skill
   - Creates approval request

3. **Human Approves**
   - Review in `vault/Pending_Approval/`
   - Move to `Approved/` to execute
   - Move to `Rejected/` to cancel

4. **System Executes**
   - Approval workflow detects approval
   - Executes via MCP server
   - Logs to audit trail
   - Moves task to `Done/`

## Tips

- **Be Specific:** Include all necessary details in the task file
- **Use Frontmatter:** Always include type and task_type
- **Add Context:** Explain why the task is needed
- **Set Priority:** Use priority field for urgent tasks
- **Review Approvals:** Always review approval requests carefully

## Creating Custom Tasks

You can create custom task types by:
1. Creating a new agent skill
2. Adding task type to skill documentation
3. Creating example task file
4. Processing with Claude Code

## Getting Help

- See skill documentation in `../../skills/*/SKILL.md`
- Check MCP server docs in `../../mcp-servers/*/README.md`
- Review ARCHITECTURE.md for system design
- Check audit logs for errors

---

**Ready to start?** Copy an example and process it with Claude Code!
