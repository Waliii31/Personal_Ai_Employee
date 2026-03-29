#!/usr/bin/env node

/**
 * Social Media MCP Server
 * Unified interface for Facebook, Instagram, and Twitter posting
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { FacebookAPI } from './facebook_api.js';
import { InstagramAPI } from './instagram_api.js';
import { TwitterAPI } from './twitter_api.js';
import dotenv from 'dotenv';

dotenv.config();

class SocialMediaMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'social-media-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.facebook = null;
    this.instagram = null;
    this.twitter = null;

    this.setupToolHandlers();

    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  initializeClients() {
    // Initialize Facebook
    if (process.env.FACEBOOK_PAGE_ID && process.env.FACEBOOK_ACCESS_TOKEN) {
      this.facebook = new FacebookAPI(
        process.env.FACEBOOK_PAGE_ID,
        process.env.FACEBOOK_ACCESS_TOKEN
      );
      console.error('[Social Media MCP] Facebook client initialized');
    }

    // Initialize Instagram
    if (process.env.INSTAGRAM_USER_ID && process.env.INSTAGRAM_ACCESS_TOKEN) {
      this.instagram = new InstagramAPI(
        process.env.INSTAGRAM_USER_ID,
        process.env.INSTAGRAM_ACCESS_TOKEN
      );
      console.error('[Social Media MCP] Instagram client initialized');
    }

    // Initialize Twitter
    if (process.env.TWITTER_BEARER_TOKEN) {
      this.twitter = new TwitterAPI(
        process.env.TWITTER_API_KEY,
        process.env.TWITTER_API_SECRET,
        process.env.TWITTER_ACCESS_TOKEN,
        process.env.TWITTER_ACCESS_SECRET,
        process.env.TWITTER_BEARER_TOKEN
      );
      console.error('[Social Media MCP] Twitter client initialized');
    }
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'post_to_facebook',
          description: 'Post a message or link to Facebook page',
          inputSchema: {
            type: 'object',
            properties: {
              message: {
                type: 'string',
                description: 'Post message/caption',
              },
              link: {
                type: 'string',
                description: 'Optional link to share',
              },
            },
            required: ['message'],
          },
        },
        {
          name: 'post_to_instagram',
          description: 'Post an image to Instagram with caption',
          inputSchema: {
            type: 'object',
            properties: {
              image_url: {
                type: 'string',
                description: 'Public URL of image to post',
              },
              caption: {
                type: 'string',
                description: 'Image caption',
              },
            },
            required: ['image_url'],
          },
        },
        {
          name: 'post_to_twitter',
          description: 'Post a tweet (max 280 characters)',
          inputSchema: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: 'Tweet text (max 280 chars)',
              },
            },
            required: ['text'],
          },
        },
        {
          name: 'get_facebook_insights',
          description: 'Get Facebook page engagement metrics',
          inputSchema: {
            type: 'object',
            properties: {
              metric: {
                type: 'string',
                description: 'Metric to retrieve (default: page_impressions)',
              },
            },
          },
        },
        {
          name: 'get_instagram_insights',
          description: 'Get Instagram account insights',
          inputSchema: {
            type: 'object',
            properties: {
              metric: {
                type: 'string',
                description: 'Metric to retrieve (default: impressions)',
              },
            },
          },
        },
        {
          name: 'get_twitter_analytics',
          description: 'Get analytics for a specific tweet',
          inputSchema: {
            type: 'object',
            properties: {
              tweet_id: {
                type: 'string',
                description: 'Tweet ID to get analytics for',
              },
            },
            required: ['tweet_id'],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        this.initializeClients();

        switch (request.params.name) {
          case 'post_to_facebook': {
            if (!this.facebook) {
              throw new Error('Facebook not configured. Set FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN');
            }

            const { message, link } = request.params.arguments;
            const result = await this.facebook.postMessage(message, link);

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    platform: 'facebook',
                    post_id: result.post_id,
                    message: 'Posted to Facebook successfully',
                  }, null, 2),
                },
              ],
            };
          }

          case 'post_to_instagram': {
            if (!this.instagram) {
              throw new Error('Instagram not configured. Set INSTAGRAM_USER_ID and INSTAGRAM_ACCESS_TOKEN');
            }

            const { image_url, caption } = request.params.arguments;
            const result = await this.instagram.postImage(image_url, caption || '');

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    platform: 'instagram',
                    post_id: result.post_id,
                    message: 'Posted to Instagram successfully',
                  }, null, 2),
                },
              ],
            };
          }

          case 'post_to_twitter': {
            if (!this.twitter) {
              throw new Error('Twitter not configured. Set TWITTER_BEARER_TOKEN');
            }

            const { text } = request.params.arguments;
            const result = await this.twitter.postTweet(text);

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    platform: 'twitter',
                    tweet_id: result.tweet_id,
                    message: 'Posted to Twitter successfully',
                  }, null, 2),
                },
              ],
            };
          }

          case 'get_facebook_insights': {
            if (!this.facebook) {
              throw new Error('Facebook not configured');
            }

            const { metric } = request.params.arguments || {};
            const insights = await this.facebook.getInsights(metric || 'page_impressions');

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(insights, null, 2),
                },
              ],
            };
          }

          case 'get_instagram_insights': {
            if (!this.instagram) {
              throw new Error('Instagram not configured');
            }

            const { metric } = request.params.arguments || {};
            const insights = await this.instagram.getAccountInsights(metric || 'impressions');

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(insights, null, 2),
                },
              ],
            };
          }

          case 'get_twitter_analytics': {
            if (!this.twitter) {
              throw new Error('Twitter not configured');
            }

            const { tweet_id } = request.params.arguments;
            const analytics = await this.twitter.getTweetAnalytics(tweet_id);

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(analytics, null, 2),
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
    console.error('[Social Media MCP] Server running on stdio');
  }
}

// Start the server
const server = new SocialMediaMCPServer();
server.run().catch(console.error);
