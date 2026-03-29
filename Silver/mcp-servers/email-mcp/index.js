#!/usr/bin/env node

/**
 * Email MCP Server
 * Provides email sending capabilities via Gmail API to Claude Code
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class EmailMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'email-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.gmail = null;
    this.setupToolHandlers();

    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async authenticate() {
    try {
      const credentialsPath = process.env.GMAIL_CREDENTIALS_PATH ||
                             path.join(__dirname, '../../credentials.json');
      const tokenPath = process.env.GMAIL_TOKEN_PATH ||
                       path.join(__dirname, '../../token.json');

      if (!fs.existsSync(credentialsPath)) {
        throw new Error(`Credentials file not found: ${credentialsPath}`);
      }

      const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
      const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;

      const oAuth2Client = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );

      // Load token if exists
      if (fs.existsSync(tokenPath)) {
        const token = JSON.parse(fs.readFileSync(tokenPath, 'utf8'));
        oAuth2Client.setCredentials(token);
      } else {
        throw new Error('Token file not found. Please run Gmail authentication first.');
      }

      this.gmail = google.gmail({ version: 'v1', auth: oAuth2Client });
      console.error('[Email MCP] Gmail authentication successful');
    } catch (error) {
      console.error('[Email MCP] Authentication error:', error.message);
      throw error;
    }
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'send_email',
          description: 'Send an email via Gmail',
          inputSchema: {
            type: 'object',
            properties: {
              to: {
                type: 'string',
                description: 'Recipient email address',
              },
              subject: {
                type: 'string',
                description: 'Email subject line',
              },
              body: {
                type: 'string',
                description: 'Email body content (plain text or HTML)',
              },
              cc: {
                type: 'string',
                description: 'CC recipients (comma-separated)',
              },
              bcc: {
                type: 'string',
                description: 'BCC recipients (comma-separated)',
              },
            },
            required: ['to', 'subject', 'body'],
          },
        },
        {
          name: 'send_reply',
          description: 'Reply to an existing email thread',
          inputSchema: {
            type: 'object',
            properties: {
              thread_id: {
                type: 'string',
                description: 'Gmail thread ID to reply to',
              },
              message_id: {
                type: 'string',
                description: 'Gmail message ID to reply to',
              },
              body: {
                type: 'string',
                description: 'Reply body content',
              },
            },
            required: ['thread_id', 'message_id', 'body'],
          },
        },
        {
          name: 'get_email',
          description: 'Retrieve a specific email by ID',
          inputSchema: {
            type: 'object',
            properties: {
              message_id: {
                type: 'string',
                description: 'Gmail message ID',
              },
            },
            required: ['message_id'],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'send_email':
            return await this.sendEmail(args);
          case 'send_reply':
            return await this.sendReply(args);
          case 'get_email':
            return await this.getEmail(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async sendEmail(args) {
    const { to, subject, body, cc, bcc } = args;

    // Create email message
    const message = [
      `To: ${to}`,
      cc ? `Cc: ${cc}` : '',
      bcc ? `Bcc: ${bcc}` : '',
      `Subject: ${subject}`,
      '',
      body,
    ].filter(line => line).join('\n');

    // Encode message
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    // Send via Gmail API
    const result = await this.gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage,
      },
    });

    return {
      content: [
        {
          type: 'text',
          text: `Email sent successfully!\nMessage ID: ${result.data.id}\nTo: ${to}\nSubject: ${subject}`,
        },
      ],
    };
  }

  async sendReply(args) {
    const { thread_id, message_id, body } = args;

    // Get original message to extract headers
    const original = await this.gmail.users.messages.get({
      userId: 'me',
      id: message_id,
    });

    const headers = original.data.payload.headers;
    const to = headers.find(h => h.name === 'From')?.value;
    const subject = headers.find(h => h.name === 'Subject')?.value;

    // Create reply message
    const message = [
      `To: ${to}`,
      `Subject: Re: ${subject}`,
      `In-Reply-To: ${message_id}`,
      `References: ${message_id}`,
      '',
      body,
    ].join('\n');

    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    const result = await this.gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage,
        threadId: thread_id,
      },
    });

    return {
      content: [
        {
          type: 'text',
          text: `Reply sent successfully!\nMessage ID: ${result.data.id}\nThread ID: ${thread_id}`,
        },
      ],
    };
  }

  async getEmail(args) {
    const { message_id } = args;

    const message = await this.gmail.users.messages.get({
      userId: 'me',
      id: message_id,
      format: 'full',
    });

    const headers = message.data.payload.headers;
    const from = headers.find(h => h.name === 'From')?.value;
    const to = headers.find(h => h.name === 'To')?.value;
    const subject = headers.find(h => h.name === 'Subject')?.value;
    const date = headers.find(h => h.name === 'Date')?.value;

    return {
      content: [
        {
          type: 'text',
          text: `Email Details:\n\nFrom: ${from}\nTo: ${to}\nSubject: ${subject}\nDate: ${date}\n\nSnippet: ${message.data.snippet}`,
        },
      ],
    };
  }

  async run() {
    await this.authenticate();
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('[Email MCP] Server running on stdio');
  }
}

// Start server
const server = new EmailMCPServer();
server.run().catch(console.error);
