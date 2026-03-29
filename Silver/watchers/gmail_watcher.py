"""
Gmail Watcher
Monitors Gmail inbox for important emails and creates action items
"""
import os
import pickle
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for new emails"""

    def __init__(self, vault_path: str, credentials_path: str = None):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes

        # Default credentials path to parent directory (Silver directory)
        if credentials_path is None:
            script_dir = Path(__file__).parent
            self.credentials_path = script_dir.parent / 'credentials.json'
        else:
            self.credentials_path = Path(credentials_path)

        # Token path also in parent directory
        self.token_path = self.credentials_path.parent / 'token.pickle'

        self.service = None
        self.last_history_id = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    self.logger.error(f'Credentials file not found: {self.credentials_path}')
                    self.logger.info('Please download credentials.json from Google Cloud Console')
                    self.logger.info(f'Expected location: {self.credentials_path.absolute()}')
                    raise FileNotFoundError(f'Missing {self.credentials_path}')

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info('Gmail authentication successful')

    def check_for_updates(self) -> list:
        """
        Check for new emails in Gmail inbox

        Returns:
            List of new email messages
        """
        try:
            # Get unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            # Fetch full message details
            emails = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                emails.append(message)

            return emails

        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, email) -> Path:
        """
        Create an action file for a new email

        Args:
            email: Gmail message object

        Returns:
            Path to the created action file
        """
        # Extract email details
        headers = {h['name']: h['value'] for h in email['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown')
        date = headers.get('Date', '')
        message_id = email['id']

        # Get email snippet
        snippet = email.get('snippet', '')

        # Determine priority based on sender or keywords
        priority = self._determine_priority(sender, subject, snippet)

        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = ''.join(c for c in subject[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        action_filename = f'EMAIL_{timestamp}_{safe_subject}.md'
        action_filepath = self.needs_action / action_filename

        # Create markdown content
        content = f"""---
type: email
message_id: {message_id}
from: {sender}
subject: {subject}
date: {date}
detected: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# New Email: {subject}

## Email Details
- **From**: {sender}
- **Date**: {date}
- **Priority**: {priority}

## Preview
{snippet}

## Suggested Actions
- [ ] Read full email content
- [ ] Determine if response is needed
- [ ] Draft response if required
- [ ] Move to /Done when complete

## Response Template
```
Hi [Name],

[Your response here]

Best regards
```

## Notes
Email automatically detected by Gmail Watcher.
Awaiting Claude Code processing.

---
*Generated by GmailWatcher at {datetime.now().isoformat()}*
"""

        # Write the action file
        action_filepath.write_text(content, encoding='utf-8')

        self.logger.info(f'Created action file: {action_filepath.name}')

        # Log to vault logs
        self._log_action(email, action_filepath)

        return action_filepath

    def _determine_priority(self, sender: str, subject: str, snippet: str) -> str:
        """Determine email priority based on content"""
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'important']

        text = f'{sender} {subject} {snippet}'.lower()

        if any(keyword in text for keyword in urgent_keywords):
            return 'high'

        # Check if from known important domains
        important_domains = ['client.com', 'partner.com']  # Customize this
        if any(domain in sender.lower() for domain in important_domains):
            return 'high'

        return 'normal'

    def _log_action(self, email, action_file: Path):
        """Log the action to the vault logs"""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'{today}.log'

        headers = {h['name']: h['value'] for h in email['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')

        log_entry = f"[{datetime.now().isoformat()}] EMAIL_DETECTED: {subject} -> {action_file.name}\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'vault'

    watcher = GmailWatcher(str(vault_path))
    watcher.run()
