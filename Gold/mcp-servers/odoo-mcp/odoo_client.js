/**
 * Odoo JSON-RPC Client
 * Handles authentication and API calls to Odoo
 */

import fetch from 'node-fetch';

export class OdooClient {
  constructor(url, db, username, password) {
    this.url = url;
    this.db = db;
    this.username = username;
    this.password = password;
    this.uid = null;
  }

  /**
   * Authenticate with Odoo and get user ID
   */
  async authenticate() {
    try {
      const response = await this.jsonRpcCall('/web/session/authenticate', {
        db: this.db,
        login: this.username,
        password: this.password,
      });

      if (response.error) {
        throw new Error(`Authentication failed: ${response.error.data.message}`);
      }

      this.uid = response.result.uid;
      if (!this.uid) {
        throw new Error('Authentication failed: No user ID returned');
      }

      console.error(`[Odoo Client] Authenticated as user ${this.uid}`);
      return this.uid;
    } catch (error) {
      console.error('[Odoo Client] Authentication error:', error.message);
      throw error;
    }
  }

  /**
   * Make a JSON-RPC call to Odoo
   */
  async jsonRpcCall(endpoint, params) {
    const url = `${this.url}${endpoint}`;
    const payload = {
      jsonrpc: '2.0',
      method: 'call',
      params: params,
      id: Math.floor(Math.random() * 1000000),
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Execute an Odoo model method
   */
  async execute(model, method, args = [], kwargs = {}) {
    if (!this.uid) {
      await this.authenticate();
    }

    const response = await this.jsonRpcCall('/web/dataset/call_kw', {
      model: model,
      method: method,
      args: args,
      kwargs: kwargs,
    });

    if (response.error) {
      throw new Error(`Odoo error: ${response.error.data.message}`);
    }

    return response.result;
  }

  /**
   * Search for records
   */
  async search(model, domain = [], fields = [], limit = null, offset = 0) {
    const kwargs = {
      fields: fields,
      limit: limit,
      offset: offset,
    };

    return await this.execute(model, 'search_read', [domain], kwargs);
  }

  /**
   * Create a new record
   */
  async create(model, values) {
    return await this.execute(model, 'create', [values]);
  }

  /**
   * Update existing record(s)
   */
  async write(model, ids, values) {
    return await this.execute(model, 'write', [ids, values]);
  }

  /**
   * Delete record(s)
   */
  async unlink(model, ids) {
    return await this.execute(model, 'unlink', [ids]);
  }

  /**
   * Read record(s)
   */
  async read(model, ids, fields = []) {
    return await this.execute(model, 'read', [ids], { fields: fields });
  }

  // ===== Accounting-specific methods =====

  /**
   * Create a customer invoice
   */
  async createInvoice(partnerName, invoiceLines, dueDate = null) {
    // First, find or create the partner (customer)
    let partnerId;
    const existingPartners = await this.search(
      'res.partner',
      [['name', '=', partnerName]],
      ['id'],
      1
    );

    if (existingPartners.length > 0) {
      partnerId = existingPartners[0].id;
    } else {
      // Create new partner
      partnerId = await this.create('res.partner', {
        name: partnerName,
        customer_rank: 1,
      });
    }

    // Prepare invoice data
    const invoiceData = {
      partner_id: partnerId,
      move_type: 'out_invoice', // Customer invoice
      invoice_date: new Date().toISOString().split('T')[0],
      invoice_line_ids: invoiceLines.map(line => [0, 0, {
        name: line.description,
        quantity: line.quantity || 1,
        price_unit: line.price,
        account_id: line.account_id || false, // Will use default
      }]),
    };

    if (dueDate) {
      invoiceData.invoice_date_due = dueDate;
    }

    const invoiceId = await this.create('account.move', invoiceData);
    return invoiceId;
  }

  /**
   * Record an expense
   */
  async recordExpense(description, amount, category = 'General', date = null) {
    const expenseDate = date || new Date().toISOString().split('T')[0];

    // Find expense account (typically 6xxxxx accounts)
    const expenseAccounts = await this.search(
      'account.account',
      [['account_type', '=', 'expense']],
      ['id', 'name'],
      1
    );

    if (expenseAccounts.length === 0) {
      throw new Error('No expense account found. Please configure chart of accounts.');
    }

    // Create journal entry for expense
    const journalEntry = {
      move_type: 'entry',
      date: expenseDate,
      journal_id: 1, // Miscellaneous journal (adjust as needed)
      line_ids: [
        [0, 0, {
          name: description,
          account_id: expenseAccounts[0].id,
          debit: amount,
          credit: 0,
        }],
        [0, 0, {
          name: description,
          account_id: expenseAccounts[0].id, // Should be cash/bank account
          debit: 0,
          credit: amount,
        }],
      ],
    };

    const moveId = await this.create('account.move', journalEntry);
    return moveId;
  }

  /**
   * Get financial summary
   */
  async getFinancialSummary(startDate = null, endDate = null) {
    const today = new Date().toISOString().split('T')[0];
    const start = startDate || `${new Date().getFullYear()}-01-01`;
    const end = endDate || today;

    // Get invoices (revenue)
    const invoices = await this.search(
      'account.move',
      [
        ['move_type', '=', 'out_invoice'],
        ['state', '=', 'posted'],
        ['invoice_date', '>=', start],
        ['invoice_date', '<=', end],
      ],
      ['amount_total', 'amount_residual']
    );

    const totalRevenue = invoices.reduce((sum, inv) => sum + inv.amount_total, 0);
    const totalReceivable = invoices.reduce((sum, inv) => sum + inv.amount_residual, 0);

    // Get expenses
    const expenses = await this.search(
      'account.move',
      [
        ['move_type', '=', 'entry'],
        ['date', '>=', start],
        ['date', '<=', end],
      ],
      ['amount_total']
    );

    const totalExpenses = expenses.reduce((sum, exp) => sum + Math.abs(exp.amount_total), 0);

    return {
      period: { start, end },
      revenue: totalRevenue,
      expenses: totalExpenses,
      profit: totalRevenue - totalExpenses,
      receivable: totalReceivable,
      invoice_count: invoices.length,
      expense_count: expenses.length,
    };
  }

  /**
   * List unpaid invoices
   */
  async listUnpaidInvoices() {
    const invoices = await this.search(
      'account.move',
      [
        ['move_type', '=', 'out_invoice'],
        ['state', '=', 'posted'],
        ['payment_state', 'in', ['not_paid', 'partial']],
      ],
      ['name', 'partner_id', 'invoice_date', 'invoice_date_due', 'amount_total', 'amount_residual']
    );

    return invoices.map(inv => ({
      invoice_number: inv.name,
      customer: inv.partner_id[1], // [id, name] tuple
      date: inv.invoice_date,
      due_date: inv.invoice_date_due,
      total: inv.amount_total,
      outstanding: inv.amount_residual,
    }));
  }

  /**
   * Generate financial report
   */
  async generateFinancialReport(startDate = null, endDate = null) {
    const summary = await this.getFinancialSummary(startDate, endDate);
    const unpaidInvoices = await this.listUnpaidInvoices();

    return {
      summary: summary,
      unpaid_invoices: unpaidInvoices,
      generated_at: new Date().toISOString(),
    };
  }
}
