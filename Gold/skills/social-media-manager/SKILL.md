# Social Media Manager Skill

Agent skill for managing multi-platform social media posting.

## Purpose

Handles social media operations including:
- Drafting posts for multiple platforms
- Creating approval requests for posts
- Posting to Facebook, Instagram, Twitter
- Analyzing post performance

## Usage

### Command Line

```bash
python social_media_manager.py --vault /path/to/vault --task-file /path/to/task.md
```

### From Claude Code

Automatically invoked when processing social media tasks from the vault.

## Task Types

### draft_post

Draft a social media post for one or more platforms.

**Required fields:**
- `platforms`: Array of platforms (facebook, instagram, twitter)
- `content`: Post content/caption

**Optional fields:**
- `image_url`: Image URL (required for Instagram)
- `link`: Link to share (Facebook)
- `schedule_time`: When to post (future feature)

**Example task file:**

```markdown
---
type: social_media
task_type: draft_post
platforms: [facebook, twitter]
---

# Draft Social Media Post

Content: Excited to announce our new product launch! 🚀

Link: https://example.com/product
```

### post_to_platform

Post content to a specific platform (after approval).

**Required fields:**
- `platform`: Platform name (facebook, instagram, twitter)
- `content`: Post content

### analyze_performance

Analyze performance of recent posts.

Uses cached analytics data from social media watchers.

## Approval Workflow

All posts require human approval:

1. Skill creates approval request in `Pending_Approval/`
2. Human reviews and moves to `Approved/` or `Rejected/`
3. Approval workflow watcher executes approved posts via Social Media MCP

## Platform-Specific Rules

### Facebook
- Max 63,206 characters
- Supports text, links, images
- Link preview automatically generated

### Instagram
- Requires image URL
- Max 2,200 characters for caption
- Image must be publicly accessible

### Twitter
- Max 280 characters
- Text only (images require media upload API)
- Hashtags and mentions supported

## Output Format

```json
{
  "success": true,
  "status": "pending_approval",
  "approval_file": "/path/to/approval.md",
  "platforms": ["facebook", "twitter"],
  "message": "Post requires approval"
}
```

## Integration

### With Social Media MCP Server

Creates approval requests with MCP commands for posting.

### With Vault

- Reads tasks from `Needs_Action/`
- Creates approval requests in `Pending_Approval/`
- Stores drafts in `Social_Media/Drafts/`

## Dependencies

- Python 3.8+
- Access to vault filesystem
- Social Media MCP server
- Approval workflow watcher
