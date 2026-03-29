# LinkedIn Poster Skill

This skill enables Claude Code to generate and schedule LinkedIn posts.

## Description

Automates LinkedIn content creation and posting:
- Generates business-focused content
- Schedules posts for optimal times
- Creates approval requests for immediate posts
- Tracks post performance

## Usage

Invoke this skill when you need to:
- Create LinkedIn content
- Schedule posts for the week
- Generate business insights to share

## Examples

```
/linkedin-poster --generate-weekly
```

Or in conversation:
```
Please generate this week's LinkedIn posts
```

```
Create a LinkedIn post about AI automation
```

## What It Does

1. Generates professional content based on topics
2. Schedules posts according to optimal times
3. Creates posts in Pending_Approval for review
4. Logs all posting activity

## Configuration

Edit `linkedin_config.json` to customize:
- Posting schedule (days and times)
- Content topics
- Hashtags
- Target audience
- Tone and style

## Requirements

- Vault must exist at configured path
- LinkedIn_Posts folder structure
- Write permissions to vault directory
