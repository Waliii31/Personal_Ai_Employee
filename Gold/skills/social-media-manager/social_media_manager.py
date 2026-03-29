"""
Social Media Manager Agent Skill
Manages multi-platform social media posting
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class SocialMediaManager:
    """Agent skill for handling social media operations"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.social_media_dir = self.vault_path / 'Social_Media'
        self.drafts_dir = self.social_media_dir / 'Drafts'
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

        # Platform character limits
        self.limits = {
            'twitter': 280,
            'facebook': 63206,
            'instagram': 2200,
        }

    def process_task(self, task_data: dict) -> dict:
        """
        Process a social media task

        Args:
            task_data: Task information from action file

        Returns:
            Result dictionary with status and details
        """
        task_type = task_data.get('task_type', 'unknown')

        if task_type == 'draft_post':
            return self._handle_draft_post(task_data)
        elif task_type == 'post_to_platform':
            return self._handle_post_to_platform(task_data)
        elif task_type == 'analyze_performance':
            return self._handle_analyze_performance(task_data)
        else:
            return {
                'success': False,
                'error': f'Unknown task type: {task_type}',
            }

    def _handle_draft_post(self, task_data: dict) -> dict:
        """Handle post drafting request"""
        platforms = task_data.get('platforms', [])
        content = task_data.get('content', '')
        image_url = task_data.get('image_url')
        link = task_data.get('link')

        if not platforms or not content:
            return {
                'success': False,
                'error': 'Missing required fields: platforms and content',
            }

        # Validate content for each platform
        validation_errors = []
        for platform in platforms:
            if platform not in self.limits:
                validation_errors.append(f'Unknown platform: {platform}')
                continue

            if len(content) > self.limits[platform]:
                validation_errors.append(
                    f'{platform}: Content exceeds {self.limits[platform]} character limit'
                )

            if platform == 'instagram' and not image_url:
                validation_errors.append('Instagram requires an image_url')

        if validation_errors:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': validation_errors,
            }

        # Save draft
        draft_file = self._save_draft(platforms, content, image_url, link)

        # Create approval request
        approval_file = self._create_approval_request(
            'post_to_social_media',
            {
                'platforms': platforms,
                'content': content,
                'image_url': image_url,
                'link': link,
                'draft_file': str(draft_file),
            }
        )

        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': str(approval_file),
            'draft_file': str(draft_file),
            'platforms': platforms,
            'message': f'Post to {", ".join(platforms)} requires approval',
        }

    def _handle_post_to_platform(self, task_data: dict) -> dict:
        """Handle direct posting (after approval)"""
        platform = task_data.get('platform')
        content = task_data.get('content')

        if not platform or not content:
            return {
                'success': False,
                'error': 'Missing required fields: platform and content',
            }

        # This would be called by approval workflow
        # Return instructions for MCP server
        return {
            'success': True,
            'status': 'ready_to_post',
            'platform': platform,
            'mcp_command': f'post_to_{platform}',
            'message': 'Ready to post via MCP server',
        }

    def _handle_analyze_performance(self, task_data: dict) -> dict:
        """Handle performance analysis request"""
        # Check for cached analytics data
        analytics_file = self.social_media_dir / 'analytics.json'

        if analytics_file.exists():
            try:
                analytics = json.loads(analytics_file.read_text())
                return {
                    'success': True,
                    'analytics': analytics,
                    'source': 'cached',
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error reading analytics: {e}',
                }
        else:
            return {
                'success': False,
                'error': 'No cached analytics data',
                'suggestion': 'Use Social Media MCP server to fetch live data',
            }

    def _save_draft(self, platforms: list, content: str, image_url: str = None, link: str = None) -> Path:
        """Save post draft to vault"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'DRAFT_{timestamp}.md'
        filepath = self.drafts_dir / filename

        draft_content = f"""---
platforms: {json.dumps(platforms)}
created: {datetime.now().isoformat()}
status: draft
---

# Social Media Post Draft

## Platforms
{', '.join(platforms)}

## Content
{content}

"""

        if image_url:
            draft_content += f"\n## Image\n{image_url}\n"

        if link:
            draft_content += f"\n## Link\n{link}\n"

        filepath.write_text(draft_content)
        return filepath

    def _create_approval_request(self, action_type: str, data: dict) -> Path:
        """Create an approval request file"""
        pending_approval = self.vault_path / 'Pending_Approval'
        pending_approval.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        platforms_str = '_'.join(data['platforms'])
        filename = f'APPROVAL_{action_type}_{platforms_str}_{timestamp}.md'
        filepath = pending_approval / filename

        content = f"""---
type: approval_request
action: {action_type}
platforms: {json.dumps(data['platforms'])}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Required: Social Media Post

## Platforms
{', '.join(data['platforms'])}

## Content
{data['content']}

"""

        if data.get('image_url'):
            content += f"\n## Image\n{data['image_url']}\n"

        if data.get('link'):
            content += f"\n## Link\n{data['link']}\n"

        content += f"""
## Instructions

To approve: Move this file to `Approved/` folder
To reject: Move this file to `Rejected/` folder

## MCP Commands (for approval)

"""

        for platform in data['platforms']:
            mcp_params = {'content': data['content']} if platform == 'twitter' else {'message': data['content']}

            if platform == 'instagram' and data.get('image_url'):
                mcp_params = {
                    'image_url': data['image_url'],
                    'caption': data['content']
                }
            elif platform == 'facebook' and data.get('link'):
                mcp_params['link'] = data['link']

            content += f"""
### {platform.title()}
```
Use Social Media MCP server tool: post_to_{platform}
Parameters: {json.dumps(mcp_params, indent=2)}
```
"""

        filepath.write_text(content)
        return filepath


def main():
    """Main entry point for the skill"""
    import argparse

    parser = argparse.ArgumentParser(description='Social Media Manager Skill')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--task-file', required=True, help='Path to task file')

    args = parser.parse_args()

    # Read task file
    task_file = Path(args.task_file)
    if not task_file.exists():
        print(json.dumps({
            'success': False,
            'error': f'Task file not found: {task_file}',
        }))
        sys.exit(1)

    # Parse task data (simplified)
    task_data = {
        'task_type': 'draft_post',
        'platforms': ['facebook', 'twitter'],
        'content': 'Sample post content',
    }

    # Create manager and process
    manager = SocialMediaManager(args.vault)
    result = manager.process_task(task_data)

    # Output result as JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
