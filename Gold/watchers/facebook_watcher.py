"""
Facebook Watcher
Monitors Facebook page for comments, mentions, and engagement
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'Silver' / 'watchers'))
from base_watcher import BaseWatcher


class FacebookWatcher(BaseWatcher):
    """Monitors Facebook page for engagement requiring action"""

    def __init__(self, vault_path: str, facebook_client, check_interval: int = 300):
        """
        Initialize Facebook watcher

        Args:
            vault_path: Path to vault
            facebook_client: Initialized FacebookAPI instance
            check_interval: Seconds between checks (default: 300 = 5 minutes)
        """
        super().__init__(vault_path, check_interval)
        self.facebook = facebook_client
        self.social_media_dir = self.vault_path / 'Social_Media'
        self.social_media_dir.mkdir(parents=True, exist_ok=True)

        # Track processed comments
        self.processed_file = self.social_media_dir / '.facebook_processed'
        self.processed_ids = self._load_processed_ids()

    def _load_processed_ids(self) -> set:
        """Load IDs of already processed comments"""
        if self.processed_file.exists():
            try:
                data = json.loads(self.processed_file.read_text())
                return set(data.get('processed_ids', []))
            except Exception:
                pass
        return set()

    def _save_processed_ids(self):
        """Save processed comment IDs"""
        data = {
            'processed_ids': list(self.processed_ids),
            'last_updated': datetime.now().isoformat(),
        }
        self.processed_file.write_text(json.dumps(data, indent=2))

    def check_for_updates(self) -> list:
        """
        Check for new comments on Facebook posts

        Returns:
            List of new comments requiring action
        """
        try:
            comments = self.facebook.getRecentComments(limit=20)
            new_comments = []

            for comment in comments:
                # Create unique ID for comment
                comment_id = f"{comment['post_id']}_{comment['created_time']}"

                if comment_id not in self.processed_ids:
                    new_comments.append(comment)
                    self.processed_ids.add(comment_id)

            if new_comments:
                self._save_processed_ids()

            return new_comments

        except Exception as e:
            self.logger.error(f'Error checking Facebook: {e}', exc_info=True)
            return []

    def create_action_file(self, comment) -> Path:
        """
        Create action file for Facebook comment

        Args:
            comment: Comment data from Facebook API

        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'FACEBOOK_{timestamp}_{comment["comment_from"][:20]}.md'
        filepath = self.needs_action / filename

        content = f"""---
type: social_media_engagement
platform: facebook
source: {comment['comment_from']}
created: {datetime.now().isoformat()}
---

# Facebook Comment Requires Response

**From:** {comment['comment_from']}
**Post:** {comment.get('post_message', 'N/A')[:100]}...
**Comment:** {comment['comment_message']}
**Time:** {comment['created_time']}

## Action Required

Review this comment and determine if a response is needed.

## Response Options

1. Reply to comment
2. Like comment
3. Mark as spam
4. No action needed

## Instructions for Claude

Please analyze this comment and suggest an appropriate response if needed.
"""

        filepath.write_text(content)
        return filepath


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Import FacebookAPI
    sys.path.append(str(Path(__file__).parent.parent / 'mcp-servers' / 'social-media-mcp'))
    from facebook_api import FacebookAPI

    page_id = os.getenv('FACEBOOK_PAGE_ID')
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')

    if not page_id or not access_token:
        print('Error: FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN must be set')
        sys.exit(1)

    client = FacebookAPI(page_id, access_token)
    vault_path = Path(__file__).parent.parent / 'vault'

    watcher = FacebookWatcher(str(vault_path), client, check_interval=300)
    watcher.run()
