"""
Twitter Watcher
Monitors Twitter account for mentions and engagement
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'Silver' / 'watchers'))
from base_watcher import BaseWatcher


class TwitterWatcher(BaseWatcher):
    """Monitors Twitter account for mentions requiring action"""

    def __init__(self, vault_path: str, twitter_client, user_id: str, check_interval: int = 300):
        """
        Initialize Twitter watcher

        Args:
            vault_path: Path to vault
            twitter_client: Initialized TwitterAPI instance
            user_id: Twitter user ID to monitor
            check_interval: Seconds between checks (default: 300 = 5 minutes)
        """
        super().__init__(vault_path, check_interval)
        self.twitter = twitter_client
        self.user_id = user_id
        self.social_media_dir = self.vault_path / 'Social_Media'
        self.social_media_dir.mkdir(parents=True, exist_ok=True)

        # Track processed mentions
        self.processed_file = self.social_media_dir / '.twitter_processed'
        self.processed_ids = self._load_processed_ids()

    def _load_processed_ids(self) -> set:
        """Load IDs of already processed mentions"""
        if self.processed_file.exists():
            try:
                data = json.loads(self.processed_file.read_text())
                return set(data.get('processed_ids', []))
            except Exception:
                pass
        return set()

    def _save_processed_ids(self):
        """Save processed mention IDs"""
        data = {
            'processed_ids': list(self.processed_ids),
            'last_updated': datetime.now().isoformat(),
        }
        self.processed_file.write_text(json.dumps(data, indent=2))

    def check_for_updates(self) -> list:
        """
        Check for new mentions on Twitter

        Returns:
            List of new mentions requiring action
        """
        try:
            mentions = self.twitter.getMentions(self.user_id, maxResults=20)
            new_mentions = []

            for mention in mentions:
                mention_id = mention['id']

                if mention_id not in self.processed_ids:
                    new_mentions.append(mention)
                    self.processed_ids.add(mention_id)

            if new_mentions:
                self._save_processed_ids()

            return new_mentions

        except Exception as e:
            self.logger.error(f'Error checking Twitter: {e}', exc_info=True)
            return []

    def create_action_file(self, mention) -> Path:
        """
        Create action file for Twitter mention

        Args:
            mention: Mention data from Twitter API

        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        author_id = mention.get('author_id', 'unknown')
        filename = f'TWITTER_{timestamp}_{author_id}.md'
        filepath = self.needs_action / filename

        content = f"""---
type: social_media_engagement
platform: twitter
source: {author_id}
created: {datetime.now().isoformat()}
---

# Twitter Mention Requires Response

**From:** User ID {author_id}
**Tweet:** {mention['text']}
**Time:** {mention.get('created_at', 'N/A')}
**Tweet ID:** {mention['id']}

## Action Required

Review this mention and determine if a response is needed.

## Response Options

1. Reply to tweet
2. Like tweet
3. Retweet
4. Quote tweet
5. No action needed

## Instructions for Claude

Please analyze this mention and suggest an appropriate response if needed.
"""

        filepath.write_text(content)
        return filepath


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Import TwitterAPI
    sys.path.append(str(Path(__file__).parent.parent / 'mcp-servers' / 'social-media-mcp'))
    from twitter_api import TwitterAPI

    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_secret = os.getenv('TWITTER_ACCESS_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print('Error: TWITTER_BEARER_TOKEN must be set')
        sys.exit(1)

    client = TwitterAPI(api_key, api_secret, access_token, access_secret, bearer_token)

    # Get authenticated user ID
    try:
        user_id = client.getAuthenticatedUserId()
        print(f'Monitoring Twitter user ID: {user_id}')
    except Exception as e:
        print(f'Error getting user ID: {e}')
        sys.exit(1)

    vault_path = Path(__file__).parent.parent / 'vault'

    watcher = TwitterWatcher(str(vault_path), client, user_id, check_interval=300)
    watcher.run()
