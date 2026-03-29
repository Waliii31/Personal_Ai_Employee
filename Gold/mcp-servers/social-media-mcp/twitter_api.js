/**
 * Twitter API v2 Client
 * Handles posting tweets and analytics
 */

import fetch from 'node-fetch';

export class TwitterAPI {
  constructor(apiKey, apiSecret, accessToken, accessSecret, bearerToken) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.accessToken = accessToken;
    this.accessSecret = accessSecret;
    this.bearerToken = bearerToken;
    this.baseUrl = 'https://api.twitter.com/2';
  }

  /**
   * Generate OAuth 1.0a signature for authenticated requests
   */
  async _getOAuth1Headers(method, url, params = {}) {
    // For simplicity, we'll use Bearer token for most operations
    // OAuth 1.0a is complex and requires crypto signing
    // In production, use a library like 'twitter-api-v2'
    return {
      'Authorization': `Bearer ${this.bearerToken}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Post a tweet
   */
  async postTweet(text) {
    if (text.length > 280) {
      throw new Error('Tweet exceeds 280 character limit');
    }

    const url = `${this.baseUrl}/tweets`;

    const body = {
      text: text,
    };

    // Note: Posting requires OAuth 1.0a User Context
    // For now, using bearer token (may need OAuth 1.0a in production)
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.bearerToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twitter API error: ${error.detail || error.title}`);
    }

    const result = await response.json();
    return {
      tweet_id: result.data.id,
      text: result.data.text,
      success: true,
    };
  }

  /**
   * Get tweet by ID
   */
  async getTweet(tweetId) {
    const url = `${this.baseUrl}/tweets/${tweetId}`;

    const params = new URLSearchParams({
      'tweet.fields': 'created_at,public_metrics,author_id',
    });

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.bearerToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twitter API error: ${error.detail || error.title}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Get tweet analytics (likes, retweets, replies)
   */
  async getTweetAnalytics(tweetId) {
    const tweet = await this.getTweet(tweetId);

    return {
      likes: tweet.public_metrics?.like_count || 0,
      retweets: tweet.public_metrics?.retweet_count || 0,
      replies: tweet.public_metrics?.reply_count || 0,
      impressions: tweet.public_metrics?.impression_count || 0,
    };
  }

  /**
   * Get user's mentions
   */
  async getMentions(userId, maxResults = 10) {
    const url = `${this.baseUrl}/users/${userId}/mentions`;

    const params = new URLSearchParams({
      'max_results': maxResults.toString(),
      'tweet.fields': 'created_at,author_id,text',
    });

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.bearerToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twitter API error: ${error.detail || error.title}`);
    }

    const result = await response.json();
    return result.data || [];
  }

  /**
   * Get authenticated user's ID
   */
  async getAuthenticatedUserId() {
    const url = `${this.baseUrl}/users/me`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${this.bearerToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twitter API error: ${error.detail || error.title}`);
    }

    const result = await response.json();
    return result.data.id;
  }

  /**
   * Search recent tweets
   */
  async searchTweets(query, maxResults = 10) {
    const url = `${this.baseUrl}/tweets/search/recent`;

    const params = new URLSearchParams({
      'query': query,
      'max_results': maxResults.toString(),
      'tweet.fields': 'created_at,author_id,public_metrics',
    });

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.bearerToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twitter API error: ${error.detail || error.title}`);
    }

    const result = await response.json();
    return result.data || [];
  }
}
