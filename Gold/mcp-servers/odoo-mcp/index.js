#!/usr/bin/env node

/**
 * Odoo MCP Server
 * Provides Odoo accounting capabilities to Claude Code
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { OdooClient } from './odoo_client.js';
import dotenv from 'dotenv';

dotenv.config();

class OdooMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'odoo-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.odooClient = null;
    this.setupToolHandlers();

    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async initializeOdoo() {
    if (this.odooClient) {
      return this.odooClient;
    }

    const url = process.env.ODOO_URL || 'http://localhost:8069';
    const db = process.env.ODOO_DB || 'odoo';
    const username = process.env.ODOO_USERNAME;
    const password = process.env.ODOO_PASSWORD;

    if (!username || !password) {
      throw new Error('ODOO_USERNAME and ODOO_PASSWORD must be set in environment variables');
    }

    this.odooClient = new OdooClient(url, db, username, password);
    await this.odooClient.authenticate();
    console.error('[Odoo MCP] Odoo client initialized');

    return this.odooClient;
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'create_invoice',
          description: 'Create a customer invoice in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              customer_name: {
                type: 'string',
                description: 'Customer name (will be created if does not exist)',
              },
              invoice_lines: {
                type: 'array',
                description: 'Array of invoice line items',
                items: {
                  type: 'object',
                  properties: {
                    description: {
                      type: 'string',
                      description: 'Line item description',
                    },
                    quantity: {
                      type: 'number',
                      description: 'Quantity (default: 1)',
                    },
                    price: {
                      type: 'number',
                      description: 'Unit price',
                    },
                  },
                  required: ['description', 'price'],
                },
              },
              due_date: {
                type: 'string',
                description: 'Due date in YYYY-MM-DD format (optional)',
              },
            },
            required: ['customer_name', 'invoice_lines'],
          },
        },
        {
          name: 'record_expense',
          description: 'Record a business expense in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              description: {
                type: 'string',
                description: 'Expense description',
              },
              amount: {
                type: 'number',
                description: 'Expense amount',
              },
              category: {
                type: 'string',
                description: 'Expense category (optional)',
              },
              date: {
                type: 'string',
                description: 'Expense date in YYYY-MM-DD format (optional, defaults to today)',
              },
            },
            required: ['description', 'amount'],
          },
        },
        {
          name: 'get_financial_summary',
          description: 'Get financial summary (revenue, expenses, profit) for a date range',
          inputSchema: {
            type: 'object',
            properties: {
              start_date: {
                type: 'string',
                description: 'Start date in YYYY-MM-DD format (optional, defaults to start of year)',
              },
              end_date: {
                type: 'string',
                description: 'End date in YYYY-MM-DD format (optional, defaults to today)',
              },
            },
          },
        },
        {
          name: 'list_unpaid_invoices',
          description: 'List all unpaid or partially paid customer invoices',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'generate_financial_report',
          description: 'Generate comprehensive financial report with summary and unpaid invoices',
          inputSchema: {
            type: 'object',
            properties: {
              start_date: {
                type: 'string',
                description: 'Start date in YYYY-MM-DD format (optional)',
              },
              end_date: {
                type: 'string',
                description: 'End date in YYYY-MM-DD format (optional)',
              },
            },
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        const client = await this.initializeOdoo();

        switch (request.params.name) {
          case 'create_invoice': {
            const { customer_name, invoice_lines, due_date } = request.params.arguments;
            const invoiceId = await client.createInvoice(
              customer_name,
              invoice_lines,
              due_date
            );
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    invoice_id: invoiceId,
                    message: `Invoice created successfully for ${customer_name}`,
                  }, null, 2),
                },
              ],
            };
          }

          case 'record_expense': {
            const { description, amount, category, date } = request.params.arguments;
            const expenseId = await client.recordExpense(
              description,
              amount,
              category,
              date
            );
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    expense_id: expenseId,
                    message: `Expense recorded: ${description} - $${amount}`,
                  }, null, 2),
                },
              ],
            };
          }

          case 'get_financial_summary': {
            const { start_date, end_date } = request.params.arguments || {};
            const summary = await client.getFinancialSummary(start_date, end_date);
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(summary, null, 2),
                },
              ],
            };
          }

          case 'list_unpaid_invoices': {
            const invoices = await client.listUnpaidInvoices();
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    count: invoices.length,
                    invoices: invoices,
                  }, null, 2),
                },
              ],
            };
          }

          case 'generate_financial_report': {
            const { start_date, end_date } = request.params.arguments || {};
            const report = await client.generateFinancialReport(start_date, end_date);
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(report, null, 2),
                },
              ],
            };
          }

          default:
            throw new Error(`Unknown tool: ${request.params.name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: false,
                error: error.message,
              }, null, 2),
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('[Odoo MCP] Server running on stdio');
  }
}

// Start the server
const server = new OdooMCPServer();
server.run().catch(console.error);
