# Platinum Tier: Always-On Cloud + Local Executive

**Estimated Time**: 60+ hours
**Status**: ⏳ Planned

## Overview

The Platinum Tier represents the ultimate evolution of my Personal AI Employee - a production-grade, always-on system with cloud and local agents working in harmony. This tier implements 24/7 autonomous operation with work-zone specialization, where the cloud agent drafts and monitors, while my local agent approves and executes sensitive actions.

## Prerequisites

✅ Complete all Gold Tier requirements first:
- Full cross-domain integration
- Odoo accounting system
- Multi-platform social media
- Weekly business audits
- Error recovery and logging
- Ralph Wiggum loop

## Platinum Tier Requirements

### 1. 24/7 Cloud Deployment

- [ ] Deploy cloud VM (Oracle Cloud Free Tier or AWS/Azure)
- [ ] Set up always-on watchers in cloud
- [ ] Implement orchestrator for continuous operation
- [ ] Configure health monitoring and alerts
- [ ] Set up automatic restart on failures
- [ ] Implement resource monitoring (CPU, memory, disk)

**Cloud Provider Options**:
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/) (recommended for cost)
- AWS EC2 (t2.micro free tier)
- Azure VM (B1s free tier)

### 2. Work-Zone Specialization

**Cloud Agent Responsibilities** (Draft-only):
- Email triage and draft replies
- Social media post drafts and scheduling
- Initial data processing and analysis
- Monitoring and alerting
- Non-sensitive task execution

**Local Agent Responsibilities** (Approval & Execution):
- Approve all cloud-drafted actions
- WhatsApp session management (never synced to cloud)
- Banking and payment execution
- Final "send/post" actions
- Sensitive credential management

**Security Rule**: Cloud never stores or uses WhatsApp sessions, banking credentials, or payment tokens.

### 3. Vault Synchronization Architecture

- [ ] Choose sync method: Git (recommended) or Syncthing
- [ ] Configure bidirectional sync
- [ ] Implement conflict resolution
- [ ] Set up sync exclusions for secrets
- [ ] Create sync monitoring and alerts

**Sync Strategy**:
```
Cloud Agent writes to:
  /Needs_Action/<domain>/
  /Plans/<domain>/
  /Pending_Approval/<domain>/
  /Updates/

Local Agent writes to:
  /Approved/
  /Done/
  /Dashboard.md (single-writer rule)
```

**Claim-by-Move Rule**: First agent to move an item from `/Needs_Action` to `/In_Progress/<agent>/` owns it; other agents must ignore it.

### 4. Delegation via Synced Vault

**Phase 1: File-Based Communication**
- [ ] Agents communicate by writing files
- [ ] Implement claim-by-move for task ownership
- [ ] Single-writer rule for Dashboard.md (Local only)
- [ ] Cloud writes updates to /Updates/, Local merges to Dashboard

**Phase 2: Agent-to-Agent (A2A) Communication** (Optional)
- [ ] Replace some file handoffs with direct A2A messages
- [ ] Keep vault as audit record
- [ ] Implement message queuing
- [ ] Add A2A protocol documentation

### 5. Cloud Odoo Deployment

- [ ] Deploy Odoo Community on cloud VM
- [ ] Configure HTTPS with SSL certificate (Let's Encrypt)
- [ ] Set up automated database backups
- [ ] Implement health monitoring
- [ ] Configure firewall rules
- [ ] Integrate Cloud Agent with Odoo via MCP
- [ ] Draft-only accounting actions (Local approval required)

### 6. Security Architecture

**Secrets Isolation**:
- [ ] Cloud: Only non-sensitive API tokens
- [ ] Local: All sensitive credentials
- [ ] Never sync: .env, tokens, WhatsApp sessions, banking creds
- [ ] Implement secrets manager (HashiCorp Vault or AWS Secrets Manager)

**Network Security**:
- [ ] Configure VPN for cloud-local communication (optional)
- [ ] Implement IP whitelisting
- [ ] Use SSH key authentication only
- [ ] Enable fail2ban on cloud VM
- [ ] Regular security audits

### 7. Platinum Demo (Minimum Passing Gate)

**Required Demo Scenario**:
1. Email arrives while Local is offline
2. Cloud Agent detects email and drafts reply
3. Cloud writes approval file to `/Pending_Approval/`
4. Vault syncs to Local
5. When Local returns, I review and approve
6. Local executes send via MCP
7. Local logs action and moves task to `/Done/`
8. Vault syncs back to Cloud

## Folder Structure

```
Platinum/
├── README.md                    # This file
├── cloud-deployment/            # Cloud infrastructure
│   ├── terraform/               # Infrastructure as Code
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── docker/                  # Containerization
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── scripts/                 # Deployment scripts
│   │   ├── setup.sh
│   │   ├── deploy.sh
│   │   └── backup.sh
│   ├── monitoring/              # Health checks
│   │   ├── prometheus.yml
│   │   └── grafana-dashboard.json
│   └── odoo/                    # Cloud Odoo setup
│       ├── docker-compose.yml
│       ├── nginx.conf
│       └── ssl/
├── local-agent/                 # Local agent configuration
│   ├── config/
│   │   ├── agent.yml
│   │   └── mcp-servers.json
│   ├── watchers/                # Local-only watchers
│   │   ├── whatsapp_watcher.py
│   │   └── approval_watcher.py
│   ├── skills/                  # Local agent skills
│   │   ├── approval-handler/
│   │   ├── payment-executor/
│   │   └── sensitive-action-handler/
│   └── secrets/                 # Local secrets (gitignored)
│       └── .env.local
├── sync-architecture/           # Vault synchronization
│   ├── git-sync/                # Git-based sync
│   │   ├── sync.sh
│   │   ├── .gitignore
│   │   └── hooks/
│   ├── syncthing/               # Alternative: Syncthing
│   │   └── config.xml
│   ├── conflict-resolution/     # Conflict handling
│   │   └── resolver.py
│   └── monitoring/              # Sync monitoring
│       └── sync_monitor.py
├── shared-vault/                # Synced vault structure
│   ├── Needs_Action/
│   │   ├── cloud/
│   │   └── local/
│   ├── In_Progress/
│   │   ├── cloud-agent/
│   │   └── local-agent/
│   ├── Pending_Approval/
│   ├── Updates/                 # Cloud writes here
│   └── Done/
└── docs/                        # Documentation
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT.md
    ├── SECURITY.md
    └── TROUBLESHOOTING.md
```

## Implementation Guide

### Step 1: Set Up Cloud VM

```bash
# Using Oracle Cloud Free Tier
# 1. Create account at oracle.com/cloud/free
# 2. Launch VM (Ubuntu 22.04 LTS)
# 3. Configure security list (ports 22, 80, 443, 8069)

# SSH into VM
ssh -i ~/.ssh/oracle_key ubuntu@<VM_IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.13 nodejs npm docker.io docker-compose git
```

### Step 2: Deploy Cloud Agent

```bash
# Clone repository to cloud
git clone <your-repo-url> ~/ai-employee
cd ~/ai-employee/Platinum/cloud-deployment

# Set up environment
cp .env.example .env.cloud
# Edit .env.cloud with non-sensitive tokens only

# Deploy with Docker
docker-compose up -d

# Set up process manager
npm install -g pm2
pm2 start orchestrator.py --interpreter python3
pm2 save
pm2 startup
```

### Step 3: Configure Vault Sync (Git Method)

**On Cloud**:
```bash
cd ~/ai-employee/shared-vault
git init
git remote add origin <your-private-repo>

# Set up auto-sync
crontab -e
# Add: */5 * * * * cd ~/ai-employee/shared-vault && git pull && git add -A && git commit -m "Auto-sync" && git push
```

**On Local**:
```bash
cd ~/ai-employee/shared-vault
git remote add origin <your-private-repo>

# Set up auto-sync
# Windows: Use Task Scheduler
# Mac/Linux: Use cron
*/5 * * * * cd ~/ai-employee/shared-vault && git pull && git add -A && git commit -m "Auto-sync" && git push
```

### Step 4: Deploy Cloud Odoo

```bash
cd ~/ai-employee/Platinum/cloud-deployment/odoo

# Configure Odoo with HTTPS
docker-compose up -d

# Set up Let's Encrypt SSL
sudo certbot --nginx -d odoo.yourdomain.com

# Configure automated backups
./scripts/backup.sh
# Add to crontab: 0 2 * * * ~/ai-employee/Platinum/cloud-deployment/odoo/scripts/backup.sh
```

### Step 5: Implement Work-Zone Specialization

**Cloud Agent Configuration**:
```yaml
# cloud-deployment/config/agent.yml
agent:
  name: cloud-agent
  mode: draft-only
  capabilities:
    - email_triage
    - social_media_drafts
    - data_processing
    - monitoring
  restrictions:
    - no_send_actions
    - no_payment_execution
    - no_whatsapp_access
```

**Local Agent Configuration**:
```yaml
# local-agent/config/agent.yml
agent:
  name: local-agent
  mode: approval-and-execution
  capabilities:
    - approve_actions
    - execute_payments
    - whatsapp_management
    - sensitive_operations
  authority: final
```

### Step 6: Set Up Monitoring

```bash
# Install Prometheus and Grafana
cd ~/ai-employee/Platinum/cloud-deployment/monitoring
docker-compose up -d

# Access Grafana at http://<VM_IP>:3000
# Import dashboard from grafana-dashboard.json
```

### Step 7: Implement Health Checks

```python
# cloud-deployment/monitoring/health_check.py
import requests
import time

def check_services():
    services = {
        'orchestrator': 'http://localhost:8000/health',
        'odoo': 'http://localhost:8069/web/health',
        'watchers': 'http://localhost:8001/health'
    }

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                alert_admin(f'{name} is unhealthy')
        except Exception as e:
            alert_admin(f'{name} is down: {e}')

# Run every 5 minutes
while True:
    check_services()
    time.sleep(300)
```

## Platinum Demo Walkthrough

### Scenario: Email Arrives While I'm Offline

**1. Cloud Agent Detects Email** (00:00)
```
Cloud Gmail Watcher detects important email from client
Creates: /Needs_Action/cloud/EMAIL_client_request_20260224.md
```

**2. Cloud Agent Processes** (00:01)
```
Cloud orchestrator triggers Claude Code
Claude reads email, understands context
Drafts professional reply
Creates: /Pending_Approval/EMAIL_REPLY_client_20260224.md
```

**3. Vault Syncs** (00:05)
```
Git auto-sync pushes to remote
Local git auto-sync pulls changes
Approval file now available locally
```

**4. I Return and Review** (08:00 next day)
```
I open Obsidian vault
See pending approval in /Pending_Approval/
Review drafted email reply
Move to /Approved/ folder
```

**5. Local Agent Executes** (08:01)
```
Local approval watcher detects file in /Approved/
Triggers Email MCP server
Sends email via my Gmail
Logs action to /Logs/2026-02-24.json
Moves task to /Done/
```

**6. Sync Completes** (08:05)
```
Local git auto-sync pushes completion
Cloud pulls and sees task is done
Updates cloud dashboard
```

## Testing Checklist

- [ ] Cloud VM is accessible and stable
- [ ] All cloud watchers run continuously
- [ ] Vault sync works bidirectionally
- [ ] No secrets are synced to cloud
- [ ] Cloud agent drafts but doesn't execute
- [ ] Local agent receives and approves drafts
- [ ] Claim-by-move prevents double-work
- [ ] Odoo is accessible via HTTPS
- [ ] Automated backups are working
- [ ] Health monitoring alerts on failures
- [ ] Platinum demo scenario works end-to-end
- [ ] System recovers from cloud VM restart
- [ ] System handles local offline periods

## Security Checklist

- [ ] Cloud VM has firewall configured
- [ ] SSH key authentication only (no passwords)
- [ ] fail2ban is active
- [ ] SSL certificates are valid
- [ ] Secrets are never synced
- [ ] Audit logs capture all actions
- [ ] Regular security updates applied
- [ ] Backup encryption enabled
- [ ] Access logs reviewed weekly

## Cost Estimation

### Oracle Cloud Free Tier
- VM: Free (2 VMs, 1GB RAM each)
- Storage: Free (200GB)
- Bandwidth: Free (10TB/month)
- **Total: $0/month**

### Paid Options
- AWS t3.small: ~$15/month
- DigitalOcean Droplet: ~$12/month
- Azure B2s: ~$30/month

### Additional Costs
- Domain name: ~$12/year
- Claude API: ~$500-2000/month (usage-based)
- **Estimated Total: $500-2000/month**

## Performance Optimization

### Cloud VM
- Use SSD storage
- Enable swap for memory management
- Implement caching for API responses
- Use CDN for static assets (if applicable)

### Sync Efficiency
- Sync only changed files
- Compress large files
- Use .gitignore for temporary files
- Implement incremental backups

## Common Issues

### Sync Conflicts
**Problem**: Both agents modify same file
**Solution**: Implement conflict resolution strategy, use single-writer rules

### Cloud VM Out of Memory
**Problem**: Processes killed by OOM
**Solution**: Add swap space, optimize watcher memory usage, upgrade VM

### Network Latency
**Problem**: Slow sync between cloud and local
**Solution**: Optimize sync frequency, compress data, use faster network

### SSL Certificate Expiry
**Problem**: HTTPS stops working
**Solution**: Set up auto-renewal with certbot, monitor expiry dates

## Maintenance Schedule

**Daily**:
- Check health monitoring dashboard
- Review error logs

**Weekly**:
- Verify backups are successful
- Review security logs
- Update system packages

**Monthly**:
- Rotate credentials
- Review and optimize costs
- Performance audit

**Quarterly**:
- Full security audit
- Disaster recovery test
- Architecture review

## Disaster Recovery

### Backup Strategy
- Daily automated Odoo database backups
- Weekly full vault backups
- Monthly system snapshots
- Store backups in multiple locations

### Recovery Procedures
1. **Cloud VM Failure**: Restore from snapshot, redeploy
2. **Data Corruption**: Restore from latest backup
3. **Security Breach**: Rotate all credentials, audit logs, rebuild VM

## Next Steps

After completing Platinum Tier:
- **Custom Cloud FTEs**: Build specialized agents for different roles
- **Multi-Agent Coordination**: Orchestrate multiple AI employees
- **Advanced A2A Communication**: Implement sophisticated agent protocols
- **Production Hardening**: Enterprise-grade reliability and security

## Resources

- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Let's Encrypt SSL](https://letsencrypt.org/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Git Sync Strategies](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)

---

**My Progress**: This is the ultimate tier - a production-grade AI Employee running 24/7. Expect 60+ hours of focused work and ongoing maintenance.
