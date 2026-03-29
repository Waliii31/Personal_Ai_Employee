# Odoo Integration Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Port 8069 available

## Installation Steps

### 1. Start Odoo

```bash
cd Gold/odoo-integration
docker-compose up -d
```

Wait 2-3 minutes for Odoo to initialize.

### 2. Access Odoo

Open browser: http://localhost:8069

**First-time setup:**
1. Create a new database:
   - Master Password: `admin`
   - Database Name: `odoo`
   - Email: your email
   - Password: choose a strong password
   - Language: English
   - Country: Your country
   - Demo data: Uncheck (for production) or Check (for testing)

2. Click "Create Database"

### 3. Install Accounting Modules

After database creation:

1. Go to Apps menu
2. Remove "Apps" filter to see all modules
3. Install these modules:
   - **Accounting** (account) - Core accounting
   - **Invoicing** (account_invoicing) - Invoice management
   - **Expenses** (hr_expense) - Expense tracking
   - **Contacts** (contacts) - Customer/vendor management

### 4. Configure Chart of Accounts

1. Go to Accounting → Configuration → Settings
2. Select your country's chart of accounts
3. Configure fiscal year
4. Save

### 5. Create API User

1. Go to Settings → Users & Companies → Users
2. Click "Create"
3. Fill in:
   - Name: `API User`
   - Email: `api@localhost`
   - Access Rights: Check "Accounting" and "Administration/Settings"
4. Save and set password

### 6. Get API Credentials

Add to your `.env` file:

```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=api@localhost
ODOO_PASSWORD=<your_api_user_password>
```

### 7. Test Connection

```bash
cd Gold/mcp-servers/odoo-mcp
npm install
npm test
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs odoo
docker-compose logs postgres
```

### Port 8069 already in use
Edit `docker-compose.yml` and change port mapping:
```yaml
ports:
  - "8070:8069"  # Use 8070 instead
```

### Database connection error
Check postgres is running:
```bash
docker-compose ps
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## Useful Commands

```bash
# View logs
docker-compose logs -f odoo

# Restart Odoo
docker-compose restart odoo

# Stop all services
docker-compose down

# Backup database
docker exec odoo_postgres pg_dump -U odoo odoo > backup.sql

# Restore database
docker exec -i odoo_postgres psql -U odoo odoo < backup.sql
```

## Next Steps

Once Odoo is running:
1. Configure the Odoo MCP server
2. Test creating invoices via Claude Code
3. Set up the odoo_sync_watcher to cache data locally
