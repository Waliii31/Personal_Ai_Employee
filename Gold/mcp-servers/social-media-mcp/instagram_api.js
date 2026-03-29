/**
 * Instagram Graph API Client
 * Handles posting and analytics for Instagram Business accounts
 */

import fetch from 'node-fetch';

export class InstagramAPI {
  constructor(userId, accessToken) {
    this.userId = userId;
    this.accessToken = accessToken;
    this.baseUrl = 'https://graph.facebook.com/v18.0';
  }

  /**
   * Create media container (step 1 of posting)
   */
  async createMediaContainer(imageUrl, caption = '') {
    const url = `${this.baseUrl}/${this.userId}/media`;

    const body = {
      image_url: imageUrl,
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
      throw new Error(`Instagram API error: ${error.error.message}`);
    }

    const result = await response.json();
    return result.id; // Container ID
  }

  /**
   * Publish media container (step 2 of posting)
   */
  async publishMedia(containerId) {
    const url = `${this.baseUrl}/${this.userId}/media_publish`;

    const body = {
      creation_id: containerId,
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
      throw new Error(`Instagram API error: ${error.error.message}`);
    }

    const result = await response.json();
    return {
      post_id: result.id,
      success: true,
    };
  }

  /**
   * Post an image to Instagram (combines create + publish)
   */
  async postImage(imageUrl, caption = '') {
    // Step 1: Create container
    const containerId = await this.createMediaContainer(imageUrl, caption);

    // Wait a moment for processing
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Step 2: Publish
    return await this.publishMedia(containerId);
  }

  /**
   * Get media insights (reach, impressions, engagement)
   */
  async getMediaInsights(mediaId) {
    const url = `${this.baseUrl}/${mediaId}/insights`;

    const params = new URLSearchParams({
      metric: 'impressions,reach,engagement',
      access_token: this.accessToken,
    });

    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Instagram API error: ${error.error.message}`);
    }

    const result = await response.json();

    // Convert to simple object
    const insights = {};
    for (const item of result.data || []) {
      insights[item.name] = item.values[0]?.value || 0;
    }

    return insights;
  }

  /**
   * Get account insights
   */
  async getAccountInsights(metric = 'impressions', period = 'day') {
    const url = `${this.baseUrl}/${this.userId}/insights`;

    const params = new URLSearchParams({
      metric: metric,
      period: period,
      access_token: this.accessToken,
    });

    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Instagram API error: ${error.error.message}`);
    }

    const result = await response.json();
    return result.data;
  }

  /**
   * Get recent comments on posts
   */
  async getRecentComments(limit = 10) {
    // First get recent media
    const mediaUrl = `${this.baseUrl}/${this.userId}/media`;
    const mediaParams = new URLSearchParams({
      fields: 'id,caption,timestamp',
      limit: limit,
      access_token: this.accessToken,
    });

    const mediaResponse = await fetch(`${mediaUrl}?${mediaParams}`);
    if (!mediaResponse.ok) {
      const error = await mediaResponse.json();
      throw new Error(`Instagram API error: ${error.error.message}`);
    }

    const mediaResult = await mediaResponse.json();

    // Get comments for each media
    const allComments = [];
    for (const media of mediaResult.data || []) {
      const commentsUrl = `${this.baseUrl}/${media.id}/comments`;
      const commentsParams = new URLSearchParams({
        fields: 'from,text,timestamp',
        access_token: this.accessToken,
      });

      try {
        const commentsResponse = await fetch(`${commentsUrl}?${commentsParams}`);
        if (commentsResponse.ok) {
          const commentsResult = await commentsResponse.json();
          for (const comment of commentsResult.data || []) {
            allComments.push({
              media_id: media.id,
              media_caption: media.caption,
              comment_from: comment.from.username,
              comment_text: comment.text,
              timestamp: comment.timestamp,
            });
          }
        }
      } catch (e) {
        // Skip if comments not available
        continue;
      }
    }

    return allComments;
  }
}
