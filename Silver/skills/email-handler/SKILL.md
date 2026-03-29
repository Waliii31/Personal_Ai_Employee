# Email Handler Skill

This skill enables Claude Code to process and respond to emails.

## Description

Handles email processing tasks:
- Analyzes incoming emails
- Determines priority and action needed
- Drafts appropriate replies
- Creates approval requests for sending

## Usage

Invoke this skill when you need to:
- Process pending emails
- Draft replies to messages
- Analyze email priority

## Examples

```
/email-handler --analyze
```

```
/email-handler --draft-reply
```

Or in conversation:
```
Please process my pending emails
```

```
Draft replies to the emails in my inbox
```

## What It Does

1. Scans Needs_Action folder for email tasks
2. Analyzes each email for priority and content
3. Determines appropriate action (reply, acknowledge, review)
4. Drafts intelligent replies using templates
5. Creates approval requests in Pending_Approval folder

## Requirements

- Vault must exist at configured path
- Email tasks in Needs_Action folder
- Write permissions to vault directory
