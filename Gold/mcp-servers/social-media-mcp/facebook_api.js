/**
 * Facebook Graph API Client
 * Handles posting and analytics for Facebook Pages
 */

import fetch from 'node-fetch';

export class FacebookAPI {
  constructor(pageId, accessToken) {
    this.pageId = pageId;
    this.accessToken = accessToken;
    this.baseUrl = 'https://graph.facebook.com/v18.0';
  }

  /**
   * Post a message to Facebook page
   */
  async postMessage(message, link = null) {
    const url = `${this.baseUrl}/${this.pageId}/feed`;

    const body = {
      message: message,
      access_token: this.accessToken,
    };

    if (link) {
      body.link = link;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Facebook API error: ${error.error.message}`);
    }

    const result = await response.json();
    return {
      post_id: result.id,
      success: true,
    };
  }

  /**
   * Post a photo to Facebook page
   */
  async postPhoto(imageUrl, caption = '') {
    const url = `${this.baseUrl}/${this.pageId}/photos`;

    const body = {
      url: imageUrl,
      caption: caption,
      access_token: this.accessToken,
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Facebook API error: ${error.error.message}`);
    }

    const result = await response.json();
    return {
      post_id: result.id,
      success: true,
    };
  }

  /**
   * Get page insights (engagement metrics)
   */
  async getInsights(metric = 'page_impressions', period = 'day') {
    const url = `${this.baseUrl}/${this.pageId}/insights`;

    const params = new URLSearchParams({
      metric: metric,
      period: period,
      access_token: this.accessToken,
    });

    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Facebook API error: ${error.error.message}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Get post engagement (likes, comments, shares)
   */
  async getPostEngagement(postId) {
    const url = `${this.baseUrl}/${postId}`;

    const params = new URLSearchParams({
      fields: 'likes.summary(true),comments.summary(true),shares',
      access_token: this.accessToken,
    });

    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Facebook API error: ${error.error.message}`);
    }

    const result = await response.json();
    return {
      likes: result.likes?.summary?.total_count || 0,
      comments: result.comments?.summary?.total_count || 0,
      shares: result.shares?.count || 0,
    };
  }

  /**
   * Get recent comments on page posts
   */
  async getRecentComments(limit = 10) {
    const url = `${this.baseUrl}/${this.pageId}/feed`;

    const params = new URLSearchParams({
      fields: 'id,message,comments{from,message,created_time}',
      limit: limit,
      access_token: this.accessToken,
    });

    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Facebook API error: ${error.error.message}`);
    }

    const result = await response.json();

    // Flatten comments from all posts
    const allComments = [];
    for (const post of result.data || []) {
      if (post.comments?.data) {
        for (const comment of post.comments.data) {
          allComments.push({
            post_id: post.id,
            post_message: post.message,
            comment_from: comment.from.name,
            comment_message: comment.message,
            created_time: comment.created_time,
          });
        }
      }
    }

    return allComments;
  }
}
