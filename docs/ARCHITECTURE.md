# Architecture Documentation

## System Overview

My Personal AI Employee is built on a layered architecture that separates concerns and enables incremental development through tiers.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL WORLD                           │
│  Gmail │ WhatsApp │ LinkedIn │ Bank │ Facebook │ Twitter   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 PERCEPTION LAYER                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Watchers (Python Scripts)                           │  │
│  │  - Gmail Watcher                                     │  │
│  │  - WhatsApp Watcher                                  │  │
│  │  - LinkedIn Watcher                                  │  │
│  │  - Filesystem Watcher                                │  │
│  │  - Finance Watcher                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              KNOWLEDGE BASE (Obsidian Vault)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  State Management                                    │  │
│  │  - Dashboard.md (Current state)                      │  │
│  │  - Company_Handbook.md (Rules & policies)            │  │
│  │  - Business_Goals.md (Objectives & metrics)          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Workflow Folders                                    │  │
│  │  - /Inbox (New items)                                │  │
│  │  - /Needs_Action (Pending tasks)                     │  │
│  │  - /Plans (Generated plans)                          │  │
│  │  - /Pending_Approval (Awaiting my approval)          │  │
│  │  - /Approved (Ready for execution)                   │  │
│  │  - /Done (Completed tasks)                           │  │
│  │  - /Logs (Audit trail)                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 REASONING LAYER                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Claude Code (AI Agent)                              │  │
│  │  1. Read: Scan vault for tasks                       │  │
│  │  2. Think: Analyze context and requirements          │  │
│  │  3. Plan: Create structured action plan              │  │
│  │  4. Write: Update vault with plans/results           │  │
│  │  5. Request: Create approval requests if needed      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Skills (Reusable Capabilities)               │  │
│  │  - Email Handler                                     │  │
│  │  - Social Media Manager                              │  │
│  │  - Task Planner                                      │  │
│  │  - Business Auditor                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              HUMAN-IN-THE-LOOP GATE                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Approval Workflow                                   │  │
│  │  - Review pending actions                            │  │
│  │  - Approve or reject                                 │  │
│  │  - Provide feedback                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  ACTION LAYER                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Servers (Model Context Protocol)               │  │
│  │  - Email MCP (Send emails)                           │  │
│  │  - Social Media MCP (Post content)                   │  │
│  │  - Browser MCP (Web automation)                      │  │
│  │  - Calendar MCP (Schedule events)                    │  │
│  │  - Odoo MCP (Accounting operations)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Orchestrator (Master Process)                       │  │
│  │  - Schedule periodic tasks                           │  │
│  │  - Monitor folder changes                            │  │
│  │  - Trigger Claude Code                               │  │
│  │  - Coordinate watchers                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Watchdog (Health Monitor)                           │  │
│  │  - Monitor process health                            │  │
│  │  - Restart failed processes                          │  │
│  │  - Alert on critical failures                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Example: Email Processing Flow

```
1. Gmail Watcher detects new email
   └─> Creates EMAIL_xxx.md in /Needs_Action

2. Orchestrator detects new file
   └─> Triggers Claude Code

3. Claude Code processes
   ├─> Reads email content
   ├─> Reads Company_Handbook.md for rules
   ├─> Analyzes context
   └─> Creates PLAN_xxx.md in /Plans

4. Claude evaluates action
   ├─> If safe: Draft reply
   └─> If sensitive: Create approval request in /Pending_Approval

5. Human reviews (if needed)
   └─> Moves file to /Approved or /Rejected

6. Orchestrator detects approval
   └─> Triggers Email MCP

7. Email MCP sends email
   └─> Logs action to /Logs

8. Claude updates status
   └─> Moves task to /Done
```

## Component Details

### 1. Watchers (Perception Layer)

**Purpose**: Monitor external sources and create actionable items

**Technology**: Python with event-based monitoring

**Key Features**:
- Continuous operation (24/7)
- Error recovery with exponential backoff
- Configurable check intervals
- Structured output (Markdown files)

**Base Pattern**:
```python
class BaseWatcher(ABC):
    def check_for_updates() -> list
    def create_action_file(item) -> Path
    def run()
```

### 2. Obsidian Vault (Knowledge Base)

**Purpose**: Central repository for state, rules, and workflow

**Technology**: Local Markdown files

**Key Features**:
- Human-readable format
- Version control friendly
- Easy to backup
- No external dependencies

**Folder Structure**:
```
vault/
├── Dashboard.md          # Current state snapshot
├── Company_Handbook.md   # Rules and policies
├── Business_Goals.md     # Objectives and metrics
├── Inbox/                # New items
├── Needs_Action/         # Pending tasks
├── Plans/                # Generated plans
├── Pending_Approval/     # Awaiting approval
├── Approved/             # Ready for execution
├── Rejected/             # Rejected actions
├── Done/                 # Completed tasks
└── Logs/                 # Audit trail
```

### 3. Claude Code (Reasoning Layer)

**Purpose**: AI-powered decision making and planning

**Technology**: Claude API via Claude Code CLI

**Key Features**:
- File system access to vault
- Agent Skills for reusable capabilities
- Ralph Wiggum loop for persistence
- Context-aware reasoning

**Workflow**:
1. Read vault state
2. Analyze tasks and context
3. Generate structured plans
4. Create approval requests for sensitive actions
5. Update vault with results

### 4. MCP Servers (Action Layer)

**Purpose**: Execute actions in external systems

**Technology**: Node.js/Python servers implementing MCP protocol

**Key Features**:
- Standardized interface
- Tool-based architecture
- Error handling and retries
- Audit logging

**Common Servers**:
- Email MCP: Send/receive emails
- Social Media MCP: Post content
- Browser MCP: Web automation
- Calendar MCP: Schedule events
- Odoo MCP: Accounting operations

### 5. Orchestrator (Coordination)

**Purpose**: Coordinate all components and manage workflow

**Technology**: Python master process

**Key Features**:
- Folder monitoring
- Scheduled task execution
- Process management
- Error recovery

**Responsibilities**:
- Start/stop watchers
- Trigger Claude Code
- Monitor approvals
- Execute MCP actions
- Generate reports

## Security Architecture

### Defense in Depth

```
Layer 1: Local-First
└─> All sensitive data stays on my machine

Layer 2: Secrets Management
└─> Environment variables, never in code

Layer 3: Human-in-the-Loop
└─> Critical actions require my approval

Layer 4: Audit Logging
└─> All actions logged with timestamps

Layer 5: Permission Boundaries
└─> Clear thresholds for auto-approval
```

### Approval Thresholds

| Action Type | Auto-Approve | Requires Approval |
|-------------|--------------|-------------------|
| Email reply | Known contacts | New contacts, bulk |
| Social post | Scheduled drafts | Immediate posts |
| Payment | < $50 recurring | All new, > $100 |
| File delete | Temp files | Vault files |

## Tier Progression

### Bronze: Foundation
- Single watcher (filesystem)
- Basic vault structure
- Claude Code integration
- Manual workflow

### Silver: Functional Assistant
- Multiple watchers (Gmail, WhatsApp, LinkedIn)
- MCP servers (Email)
- Approval workflow
- Scheduled operations

### Gold: Autonomous Employee
- Full integration (Personal + Business)
- Odoo accounting
- Multi-platform social media
- Weekly business audits
- Error recovery

### Platinum: Always-On Cloud
- 24/7 cloud deployment
- Work-zone specialization
- Vault synchronization
- Production-grade reliability

## Technology Stack

### Core Technologies
- **Python 3.13+**: Watchers, orchestration
- **Node.js v24+**: MCP servers
- **Claude Code**: AI reasoning
- **Obsidian**: Knowledge base
- **Git**: Version control

### Libraries & Frameworks
- **watchdog**: File system monitoring
- **playwright**: Browser automation
- **google-api-python-client**: Gmail integration
- **python-dotenv**: Environment management
- **requests**: HTTP client

### Infrastructure (Platinum)
- **Docker**: Containerization
- **Terraform**: Infrastructure as Code
- **Prometheus**: Monitoring
- **Grafana**: Dashboards
- **Let's Encrypt**: SSL certificates

## Scalability Considerations

### Current Design (Bronze-Gold)
- Single machine
- Local processing
- Manual scaling

### Future Design (Platinum+)
- Cloud + Local hybrid
- Distributed processing
- Automatic scaling
- Multi-agent coordination

## Monitoring & Observability

### Metrics to Track
- Watcher uptime
- Task processing time
- API call counts
- Error rates
- Approval response time

### Logging Strategy
- Structured JSON logs
- Daily log rotation
- 90-day retention
- Centralized collection (Platinum)

## Disaster Recovery

### Backup Strategy
- Daily vault backups
- Weekly full system backups
- Monthly snapshots
- Off-site storage

### Recovery Procedures
1. Restore vault from backup
2. Reinstall dependencies
3. Restore environment variables
4. Restart watchers
5. Verify functionality

---

**Last Updated**: 2026-02-22
