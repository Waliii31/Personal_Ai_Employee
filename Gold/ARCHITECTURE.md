# Gold Tier Architecture

## System Design

Gold Tier implements a fully autonomous business operations system with financial management, social media automation, and proactive business intelligence.

## Core Components

### 1. MCP Servers (External Integrations)

**Odoo MCP Server**
- Location: `mcp-servers/odoo-mcp/`
- Purpose: Accounting and financial management
- Protocol: JSON-RPC over HTTP
- Tools:
  - `create_invoice` - Create customer invoices
  - `record_expense` - Record business expenses
  - `get_financial_summary` - Retrieve financial metrics
  - `list_unpaid_invoices` - List outstanding invoices
  - `generate_financial_report` - Generate comprehensive reports

**Social Media MCP Server**
- Location: `mcp-servers/social-media-mcp/`
- Purpose: Multi-platform social media posting
- APIs: Facebook Graph API, Instagram Graph API, Twitter API v2
- Tools:
  - `post_to_facebook` - Post to Facebook page
  - `post_to_instagram` - Post image to Instagram
  - `post_to_twitter` - Post tweet
  - `get_facebook_insights` - Retrieve engagement metrics
  - `get_instagram_insights` - Retrieve reach/impressions
  - `get_twitter_analytics` - Retrieve tweet performance

### 2. Watchers (Event Monitors)

Watchers inherit from `BaseWatcher` and implement:
- `check_for_updates()` - Poll external systems
- `create_action_file()` - Create task files in vault

**Active Watchers:**
- `facebook_watcher.py` - Monitor Facebook comments (5 min interval)
- `instagram_watcher.py` - Monitor Instagram comments (5 min interval)
- `twitter_watcher.py` - Monitor Twitter mentions (5 min interval)
- `odoo_sync_watcher.py` - Sync Odoo data to vault (1 hour interval)
- `briefing_scheduler.py` - Trigger CEO briefing (Sunday 11 PM)
- `approval_workflow.py` - Process approval requests (1 min interval)

### 3. Agent Skills (Task Processors)

Skills are Python scripts invoked by Claude Code to process specific task types.

**Accounting Assistant**
- Location: `skills/accounting-assistant/`
- Purpose: Process financial tasks
- Capabilities:
  - Create invoice approval requests
  - Record expense approval requests
  - Retrieve cached financial data
  - List unpaid invoices

**Social Media Manager**
- Location: `skills/social-media-manager/`
- Purpose: Manage social media posting
- Capabilities:
  - Draft posts for multiple platforms
  - Validate content (character limits, required fields)
  - Create approval requests
  - Store drafts in vault

**Business Auditor**
- Location: `skills/business-auditor/`
- Purpose: Generate CEO briefings
- Capabilities:
  - Analyze Odoo financial data
  - Scan completed tasks
  - Detect bottlenecks
  - Audit subscriptions
  - Generate proactive suggestions

**Task Orchestrator**
- Location: `skills/task-orchestrator/`
- Purpose: Manage Ralph Wiggum loop
- Capabilities:
  - Start autonomous loops
  - Track iteration state
  - Detect task completion
  - Emergency stop

### 4. Ralph Wiggum Loop (Autonomous Engine)

**Purpose:** Enable Claude to work autonomously on multi-step tasks until completion.

**Completion Detection Strategies:**
1. **File Movement** - Task file moved to `/Done` folder
2. **Promise Tag** - Claude outputs `<promise>TASK_COMPLETE</promise>`
3. **Metadata Flag** - Task frontmatter contains `status: completed`

**Safety Limits:**
- Max iterations: 10 (configurable)
- Timeout per iteration: 5 minutes
- Emergency stop mechanism
- State persistence across iterations

**State Management:**
- State stored in `vault/Logs/loop_state/`
- JSON format with full history
- Resumable after interruption

### 5. Error Recovery System

**Error Categories:**
- **Transient** - Network timeouts, temporary unavailability → Retry with backoff
- **Auth** - Authentication failures → Alert human, pause operations
- **Logic** - Business logic errors → Move to human review queue
- **Data** - Validation errors → Quarantine data
- **System** - System-level errors → Watchdog restart

**Retry Strategy:**
- Exponential backoff (1s, 2s, 4s)
- Max 3 attempts for transient errors
- Operation queuing for service outages
- Graceful degradation

### 6. Audit Logging System

**Purpose:** Comprehensive audit trail for compliance and debugging.

**Logged Events:**
- All MCP server calls
- All approval decisions
- All external API calls
- All error occurrences

**Log Format:**
```json
{
  "timestamp": "2026-03-14T10:00:00",
  "action_type": "create_invoice",
  "actor": "claude",
  "target": "invoice_123",
  "parameters": {...},
  "result": "success",
  "details": {...}
}
```

**Retention:** 90 days, automatic cleanup

## Data Flow

### Invoice Creation Flow

```
1. Email arrives → Gmail Watcher
2. Creates task in Needs_Action/
3. Claude processes task → Accounting Assistant skill
4. Skill creates approval request in Pending_Approval/
5. Human moves to Approved/
6. Approval Workflow watcher detects approval
7. Executes via Odoo MCP server
8. Logs to audit trail
9. Moves task to Done/
```

### Social Media Posting Flow

```
1. User creates post task in Needs_Action/
2. Claude processes → Social Media Manager skill
3. Skill validates content, creates draft
4. Creates approval request in Pending_Approval/
5. Human reviews and approves
6. Approval Workflow executes via Social Media MCP
7. Posts to Facebook, Instagram, Twitter
8. Logs to audit trail
9. Moves task to Done/
```

### CEO Briefing Flow

```
1. Sunday 11 PM → Briefing Scheduler watcher
2. Creates briefing task in Needs_Action/
3. Claude processes → Business Auditor skill
4. Skill analyzes:
   - Odoo financial data (cached)
   - Completed tasks (Done/ folder)
   - Subscription usage (bank transactions)
5. Generates briefing in Briefings/
6. Moves task to Done/
```

### Ralph Wiggum Loop Flow

```
1. Complex task created in Needs_Action/
2. Ralph Wiggum loop started
3. Loop iteration:
   a. Check if task complete (file movement, promise, metadata)
   b. If complete → Exit with success
   c. If waiting approval → Pause loop
   d. If incomplete → Invoke Claude Code
   e. Update state, increment iteration
   f. Wait 5 seconds
4. Repeat until complete or max iterations
5. Save final state
```

## Vault Structure

```
vault/
├── Needs_Action/          # Tasks awaiting processing
├── Pending_Approval/      # Actions awaiting human approval
├── Approved/              # Approved actions (processed by workflow)
├── Rejected/              # Rejected actions (archived)
├── Done/                  # Completed tasks
├── Accounting/            # Cached Odoo data
│   ├── financial_summary.json
│   ├── unpaid_invoices.json
│   └── recent_expenses.json
├── Social_Media/          # Social media data
│   ├── Drafts/           # Post drafts
│   ├── .facebook_processed
│   ├── .instagram_processed
│   └── .twitter_processed
├── Briefings/             # CEO briefings
│   └── CEO_BRIEFING_YYYYMMDD.md
└── Logs/                  # System logs
    ├── audit/            # Audit logs (90-day retention)
    ├── errors/           # Error logs
    ├── loop_state/       # Ralph Wiggum state
    └── orchestrator.log  # Orchestrator log
```

## Security Model

### Human-in-the-Loop (HITL)

All sensitive actions require approval:
- Creating invoices
- Recording expenses
- Posting to social media
- Canceling subscriptions

### Approval Workflow

1. Skill creates approval request in `Pending_Approval/`
2. Request includes full details and MCP command
3. Human reviews and moves to `Approved/` or `Rejected/`
4. Approval workflow watcher executes approved actions
5. All decisions logged to audit trail

### Credential Management

- All credentials in environment variables
- Never committed to git
- MCP servers run with minimal permissions
- Separate credentials per service

## Performance Considerations

### Watcher Intervals

- Social media watchers: 5 minutes (balance responsiveness vs. rate limits)
- Odoo sync: 1 hour (financial data changes slowly)
- Briefing scheduler: 1 hour (only triggers on Sunday 11 PM)
- Approval workflow: 1 minute (fast response to approvals)

### Caching Strategy

- Odoo data cached locally for offline access
- Social media processed IDs tracked to avoid duplicates
- Briefing data aggregated from cache (fast generation)

### Scalability

- Each watcher runs in separate thread
- MCP servers are stateless (can scale horizontally)
- Audit logs partitioned by day (fast queries)
- Ralph Wiggum loops isolated per task

## Error Handling

### Graceful Degradation

- If Odoo unavailable → Use cached data, queue operations
- If social media API fails → Retry with backoff, alert human
- If watcher crashes → Watchdog restarts, log error
- If max iterations reached → Alert human, save state

### Recovery Procedures

1. **Transient errors** - Automatic retry with exponential backoff
2. **Auth errors** - Alert human, pause operations, wait for fix
3. **Logic errors** - Move to human review queue
4. **Data errors** - Quarantine data, alert human
5. **System errors** - Watchdog restart, log for investigation

## Monitoring

### Health Checks

- Orchestrator status endpoint
- Watcher thread monitoring
- MCP server connectivity checks
- Audit log completeness verification

### Metrics

- Actions per day (by type)
- Approval rate (approved vs. rejected)
- Error rate (by category)
- Task completion time
- Ralph Wiggum iteration counts

## Future Enhancements (Platinum Tier)

- 24/7 cloud deployment
- Work-zone specialization (Cloud drafts, Local approves)
- Vault synchronization via Git
- Agent-to-agent communication
- Advanced security with secrets isolation
- Multi-user support
