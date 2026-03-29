"""
Gmail Watcher - Monitors Gmail for new important emails and creates action files
Based on the implementation outlined in the Platinum tier document
"""

import time
import logging
import json
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Dict, Any


class GmailWatcher(BaseWatcher):
    """
    Gmail watcher implementation that monitors for new important emails
    and creates action files for the AI Employee to process.
    """

    def __init__(self, vault_path: str, credentials_path: str = None,
                 token_path: str = None, check_interval: int = 120):
        """
        Initialize the Gmail watcher

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to the OAuth2 credentials JSON file
            token_path: Path to the saved token file (defaults to token.pickle in vault)
            check_interval: How often to check for new emails (in seconds)
        """
        super().__init__(vault_path, check_interval)

        # Set default paths if not provided
        self.credentials_path = Path(credentials_path) if credentials_path else \
                               Path(vault_path) / "gmail_credentials.json"
        self.token_path = Path(token_path) if token_path else \
                         Path(vault_path) / "token.pickle"

        # Gmail API scopes - only read access for security
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']

        # Initialize Gmail service
        self.service = self._authenticate()

        # Track processed message IDs to avoid duplicates
        self.processed_ids = set()

        # Load previously processed IDs if available
        self._load_processed_ids()

    def _authenticate(self):
        """
        Authenticate with Gmail API using OAuth2

        Returns:
            Gmail API service object
        """
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    # If refresh fails, fall back to re-authentication
                    creds = None

            if not creds:
                if not self.credentials_path.exists():
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    self.logger.error("Please follow the Gmail API setup instructions to create credentials.")
                    return None

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    creds = flow.run_local_server(port=0)

                    # Save the credentials for next run
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(creds, token)
                except Exception as e:
                    self.logger.error(f"Authentication failed: {e}")
                    return None

        # Build the Gmail service
        try:
            service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Successfully authenticated with Gmail API")
            return service
        except Exception as e:
            self.logger.error(f"Failed to build Gmail service: {e}")
            return None

    def _load_processed_ids(self):
        """
        Load previously processed message IDs from a file to avoid reprocessing
        """
        processed_file = self.vault_path / "processed_emails.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('processed_ids', []))
            except Exception as e:
                self.logger.warning(f"Could not load processed email IDs: {e}")

    def _save_processed_ids(self):
        """
        Save processed message IDs to a file
        """
        processed_file = self.vault_path / "processed_emails.json"
        try:
            with open(processed_file, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_ids),
                    'last_updated': datetime.now().isoformat()
                }, f)
        except Exception as e:
            self.logger.error(f"Could not save processed email IDs: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new important/unread emails

        Returns:
            List of message objects that need processing
        """
        if not self.service:
            self.logger.error("Gmail service not available")
            return []

        try:
            # Query for unread important emails
            # You can customize this query based on your needs
            query = 'is:unread is:important newer_than:1d'  # Last 24 hours of important unread emails

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=20  # Limit to 20 emails per check to avoid overwhelming
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for msg in messages:
                msg_id = msg['id']

                # Skip if we've already processed this message
                if msg_id in self.processed_ids:
                    continue

                try:
                    # Get the full message details
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg_id
                    ).execute()

                    new_messages.append(full_msg)
                    self.processed_ids.add(msg_id)

                except Exception as e:
                    self.logger.error(f"Could not fetch message {msg_id}: {e}")

            # Save processed IDs to file
            self._save_processed_ids()

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking for Gmail updates: {e}")
            return []

    def create_action_file(self, message) -> Path:
        """
        Create an action file for a Gmail message

        Args:
            message: Gmail message object

        Returns:
            Path to the created action file
        """
        # Extract headers
        headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}

        # Extract email parts
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown Sender')
        recipient = headers.get('To', 'Unknown Recipient')
        date = headers.get('Date', 'Unknown Date')

        # Extract snippet and body
        snippet = message.get('snippet', '')

        # Try to extract the full body content
        body = self._extract_body(message)

        # Determine priority based on sender or subject
        priority = self._determine_priority(sender, subject)

        # Create markdown content
        content = f"""---
type: email
from: {sender}
to: {recipient}
subject: {subject}
received: {date}
gmail_id: {message['id']}
priority: {priority}
status: pending
category: {self._categorize_email(sender, subject)}
---

# Email Received

## Message Details
- **From:** {sender}
- **To:** {recipient}
- **Subject:** {subject}
- **Date:** {date}
- **Priority:** {priority}
- **Category:** {self._categorize_email(sender, subject)}

## Email Content
{body if body else f"> {snippet}"}

## Recommended Actions
- [ ] Review content thoroughly
- [ ] Respond appropriately ({'requires response' if self._requires_response(sender, subject) else 'informational'})
- [ ] File appropriately
- [ ] Update contact records if needed

## Classification
- **Urgent:** {'Yes' if priority == 'high' else 'No'}
- **Requires Response:** {'Yes' if self._requires_response(sender, subject) else 'No'}
- **May Contain Attachment:** {'Yes' if self._has_attachments(message) else 'No'}

## Context
Based on the sender and content, this email may require immediate attention.
"""

        # Create a unique filename based on the message ID and subject
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean subject for filename
        clean_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_subject = clean_subject[:50]  # Limit length
        action_filename = f"GMAIL_{timestamp}_{message['id']}_{clean_subject}.md"
        action_filepath = self.needs_action / action_filename

        # Write the content to the action file
        action_filepath.write_text(content, encoding='utf-8')

        return action_filepath

    def _extract_body(self, message) -> str:
        """
        Extract the body content from a Gmail message

        Args:
            message: Gmail message object

        Returns:
            Body content as string
        """
        try:
            payload = message.get('payload', {})
            parts = payload.get('parts', [])

            # If there are no parts, try to get the body from the payload directly
            if not parts:
                body_data = payload.get('body', {}).get('data')
                if body_data:
                    import base64
                    decoded_bytes = base64.urlsafe_b64decode(body_data)
                    return decoded_bytes.decode('utf-8')
                return ""

            # Look for text/plain or text/html parts
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data')
                    if body_data:
                        import base64
                        decoded_bytes = base64.urlsafe_b64decode(body_data)
                        return decoded_bytes.decode('utf-8')

                elif part.get('mimeType') == 'text/html':
                    # If no plain text found, return HTML content
                    body_data = part.get('body', {}).get('data')
                    if body_data:
                        import base64
                        decoded_bytes = base64.urlsafe_b64decode(body_data)
                        html_content = decoded_bytes.decode('utf-8')
                        # Simple HTML to text conversion (could be improved)
                        import re
                        clean_text = re.sub('<[^<]+?>', '', html_content)
                        return clean_text

            return ""
        except Exception as e:
            self.logger.error(f"Error extracting email body: {e}")
            return ""

    def _determine_priority(self, sender: str, subject: str) -> str:
        """
        Determine the priority of an email based on sender and subject

        Args:
            sender: Email sender
            subject: Email subject

        Returns:
            Priority level ('low', 'medium', 'high', 'critical')
        """
        subject_lower = subject.lower()
        sender_lower = sender.lower()

        # Critical keywords
        critical_keywords = [
            'urgent', 'asap', 'immediately', 'emergency', 'critical',
            'important', 'attention', 'deadline', 'payment', 'invoice'
        ]

        # High priority keywords
        high_keywords = [
            'meeting', 'schedule', 'proposal', 'contract', 'agreement',
            'billing', 'account', 'security', 'password', 'login'
        ]

        # Check for critical keywords
        for keyword in critical_keywords:
            if keyword in subject_lower or keyword in sender_lower:
                return 'critical'

        # Check for high priority keywords
        for keyword in high_keywords:
            if keyword in subject_lower or keyword in sender_lower:
                return 'high'

        # Medium priority for business-related emails
        business_keywords = [
            'business', 'client', 'customer', 'order', 'sale', 'project',
            'work', 'team', 'company', 'partner', 'vendor'
        ]

        for keyword in business_keywords:
            if keyword in subject_lower or keyword in sender_lower:
                return 'medium'

        # Default to low priority
        return 'low'

    def _categorize_email(self, sender: str, subject: str) -> str:
        """
        Categorize the email based on sender and subject

        Args:
            sender: Email sender
            subject: Email subject

        Returns:
            Category string
        """
        subject_lower = subject.lower()
        sender_lower = sender.lower()

        # Define categories
        categories = {
            'personal': ['friend', 'family', 'personal', 'home'],
            'business': ['client', 'customer', 'order', 'sale', 'project', 'work', 'business'],
            'financial': ['payment', 'invoice', 'billing', 'account', 'bank', 'finance', 'money'],
            'technical': ['support', 'bug', 'error', 'issue', 'technical', 'system'],
            'marketing': ['promotion', 'offer', 'discount', 'sale', 'advertising', 'marketing'],
            'notification': ['notification', 'alert', 'update', 'reminder', 'confirm']
        }

        # Check each category
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in subject_lower or keyword in sender_lower:
                    return category

        # Default category
        return 'general'

    def _requires_response(self, sender: str, subject: str) -> bool:
        """
        Determine if the email requires a response

        Args:
            sender: Email sender
            subject: Email subject

        Returns:
            Boolean indicating if response is required
        """
        subject_lower = subject.lower()

        # Keywords that suggest a response is needed
        response_keywords = [
            'question', '?', 'ask', 'please', 'help', 'need', 'want',
            'when', 'how', 'what', 'can you', 'would you', 'could you'
        ]

        for keyword in response_keywords:
            if keyword in subject_lower:
                return True

        # Check if it's from a known contact
        # This would typically check against a contacts list
        return False

    def _has_attachments(self, message) -> bool:
        """
        Check if the email has attachments

        Args:
            message: Gmail message object

        Returns:
            Boolean indicating if there are attachments
        """
        try:
            payload = message.get('payload', {})
            parts = payload.get('parts', [])

            for part in parts:
                if part.get('filename'):  # Has a filename, likely an attachment
                    return True
                # Also check if it's an attachment part
                headers = part.get('headers', [])
                for header in headers:
                    if header.get('name') == 'Content-Disposition':
                        if 'attachment' in header.get('value', ''):
                            return True
        except Exception:
            pass

        return False


def main():
    """
    Example usage of the Gmail watcher
    """
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to the vault directory')
    parser.add_argument('--credentials', type=str, help='Path to Gmail credentials JSON file')
    parser.add_argument('--token', type=str, help='Path to saved token file')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds (default: 120)')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create and run the Gmail watcher
    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token,
        check_interval=args.interval
    )

    # Run the watcher (this will run indefinitely)
    watcher.run()


if __name__ == "__main__":
    main()