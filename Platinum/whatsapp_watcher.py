"""
WhatsApp Watcher - Monitors WhatsApp for new messages and creates action files
Uses Playwright for WhatsApp Web automation as outlined in the Platinum tier document
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from playwright.sync_api import sync_playwright
import json
import re
from typing import List, Dict, Any


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp watcher implementation that monitors WhatsApp Web for new messages
    and creates action files for the AI Employee to process.

    NOTE: This implementation respects WhatsApp's Terms of Service and includes
    appropriate delays and user-agent settings.
    """

    def __init__(self, vault_path: str, session_path: str = None,
                 check_interval: int = 30, keywords: List[str] = None):
        """
        Initialize the WhatsApp watcher

        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store WhatsApp session data
            check_interval: How often to check for new messages (in seconds)
            keywords: List of keywords that indicate important messages
        """
        super().__init__(vault_path, check_interval)

        # Set up session path for WhatsApp
        self.session_path = Path(session_path) if session_path else \
                           Path(vault_path) / "whatsapp_session"

        # Create session directory
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Set of keywords to monitor for important messages
        self.keywords = keywords or [
            'urgent', 'asap', 'invoice', 'payment', 'help',
            'problem', 'issue', 'need', 'question', 'when',
            'meeting', 'project', 'contract', 'agreement'
        ]

        # Track processed message IDs to avoid duplicates
        self.processed_message_ids = set()

        # Load previously processed IDs if available
        self._load_processed_ids()

    def _load_processed_ids(self):
        """
        Load previously processed message IDs from a file to avoid reprocessing
        """
        processed_file = self.vault_path / "processed_whatsapp.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_message_ids = set(data.get('processed_ids', []))
            except Exception as e:
                self.logger.warning(f"Could not load processed WhatsApp message IDs: {e}")

    def _save_processed_ids(self):
        """
        Save processed message IDs to a file
        """
        processed_file = self.vault_path / "processed_whatsapp.json"
        try:
            with open(processed_file, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_message_ids),
                    'last_updated': datetime.now().isoformat()
                }, f)
        except Exception as e:
            self.logger.error(f"Could not save processed WhatsApp message IDs: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new important messages

        Returns:
            List of message dictionaries that need processing
        """
        try:
            with sync_playwright() as p:
                # Launch browser with WhatsApp Web
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True in production
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    viewport={'width': 1280, 'height': 800},
                    locale='en-US',
                    timezone_id='America/New_York'
                )

                page = browser.new_page()

                # Navigate to WhatsApp Web
                page.goto('https://web.whatsapp.com')

                # Wait for WhatsApp to load and QR code scan (manual step)
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                except:
                    # If QR code is still showing, wait for manual scan
                    qr_code = page.locator('canvas')
                    if qr_code.count() > 0:
                        print("Please scan the QR code to log in to WhatsApp Web")
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)

                # Wait a bit more to ensure everything is loaded
                page.wait_for_timeout(5000)

                # Find chats with unread messages
                unread_chats = page.query_selector_all('[data-testid="default-chat"] div[role="button"][aria-label*="unread"]')

                important_messages = []

                for chat in unread_chats:
                    try:
                        # Click on the chat to open it
                        chat.click()

                        # Wait for messages to load
                        page.wait_for_timeout(2000)

                        # Get all messages in the chat
                        message_elements = page.query_selector_all('div[data-testid="conversation-turn"] div[data-testid="msg-container"]')

                        for msg_element in message_elements:
                            # Extract message text
                            message_text = msg_element.inner_text()

                            # Check if message contains important keywords
                            if self._contains_important_keyword(message_text):
                                # Create a unique ID for this message
                                msg_id = hash(message_text + str(datetime.now().timestamp()))

                                # Skip if already processed
                                if str(msg_id) in self.processed_message_ids:
                                    continue

                                # Get sender info (try to extract from context)
                                sender_element = msg_element.query_selector('..')  # Go up one level
                                sender_info = self._extract_sender_info(page, msg_element)

                                important_messages.append({
                                    'id': str(msg_id),
                                    'text': message_text,
                                    'sender': sender_info,
                                    'timestamp': datetime.now().isoformat(),
                                    'chat_name': self._get_current_chat_name(page)
                                })

                                # Add to processed IDs
                                self.processed_message_ids.add(str(msg_id))

                    except Exception as e:
                        self.logger.error(f"Error processing chat: {e}")
                        continue

                # Close the browser
                browser.close()

                # Save processed IDs
                self._save_processed_ids()

                return important_messages

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp for updates: {e}")
            return []

    def _contains_important_keyword(self, text: str) -> bool:
        """
        Check if text contains any of the important keywords

        Args:
            text: Text to check

        Returns:
            Boolean indicating if important keyword is found
        """
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword in text_lower:
                return True
        return False

    def _extract_sender_info(self, page, message_element) -> str:
        """
        Attempt to extract sender information from the message element

        Args:
            page: Playwright page object
            message_element: Message element to analyze

        Returns:
            Sender information string
        """
        try:
            # Try to find sender name associated with the message
            # This may vary depending on WhatsApp Web structure
            sender_elements = message_element.query_selector_all('span[dir="auto"]')

            if sender_elements:
                for elem in sender_elements:
                    sender_name = elem.inner_text().strip()
                    if sender_name and len(sender_name) > 0 and not sender_name.isdigit():
                        return sender_name

            # Fallback to current chat name
            return self._get_current_chat_name(page)
        except:
            return "Unknown Contact"

    def _get_current_chat_name(self, page) -> str:
        """
        Get the name of the currently selected chat

        Args:
            page: Playwright page object

        Returns:
            Chat name string
        """
        try:
            # Look for the chat header with contact name
            chat_title_selector = '._3U32X ._19RFN'
            title_element = page.query_selector(chat_title_selector)
            if title_element:
                return title_element.inner_text().strip()

            # Alternative selectors (WhatsApp Web frequently changes)
            alt_selectors = [
                '[data-testid="conversation-info-title"]',
                '._3U32X span',
                '[title*="Chat with"]'
            ]

            for selector in alt_selectors:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text().strip()
                    if text:
                        return text

        except Exception as e:
            self.logger.debug(f"Could not extract chat name: {e}")

        return "Unknown Chat"

    def create_action_file(self, message) -> Path:
        """
        Create an action file for a WhatsApp message

        Args:
            message: Dictionary containing message details

        Returns:
            Path to the created action file
        """
        # Determine priority based on keywords in the message
        priority = self._determine_priority(message['text'])

        # Create markdown content
        content = f"""---
type: whatsapp_message
sender: {message['sender']}
timestamp: {message['timestamp']}
message_id: {message['id']}
priority: {priority}
status: pending
category: {self._categorize_message(message['text'])}
---

# WhatsApp Message Received

## Message Details
- **From:** {message['sender']}
- **Time:** {message['timestamp']}
- **Priority:** {priority}
- **Category:** {self._categorize_message(message['text'])}

## Message Content
{message['text']}

## Recommended Actions
- [ ] Review message content
- [ ] Respond appropriately ({'requires response' if self._requires_response(message['text']) else 'informational'})
- [ ] Take necessary action
- [ ] Update contact records if needed

## Analysis
- **Urgent:** {'Yes' if priority == 'high' or priority == 'critical' else 'No'}
- **Requires Response:** {'Yes' if self._requires_response(message['text']) else 'No'}
- **Contains Important Keyword:** {'Yes' if self._contains_important_keyword(message['text']) else 'No'}

## Context
This message contains keywords that indicate importance. Please review and respond accordingly.
"""

        # Create a unique filename based on the message ID and sender
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean sender name for filename
        clean_sender = "".join(c for c in message['sender'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_sender = clean_sender[:30]  # Limit length
        action_filename = f"WHATSAPP_{timestamp}_{message['id']}_{clean_sender}.md"
        action_filepath = self.needs_action / action_filename

        # Write the content to the action file
        action_filepath.write_text(content, encoding='utf-8')

        return action_filepath

    def _determine_priority(self, text: str) -> str:
        """
        Determine the priority of a message based on its content

        Args:
            text: Message text

        Returns:
            Priority level ('low', 'medium', 'high', 'critical')
        """
        text_lower = text.lower()

        # Critical keywords
        critical_keywords = [
            'urgent', 'asap', 'immediately', 'emergency', 'critical',
            'problem', 'issue', 'error', 'broken', 'failed'
        ]

        # High priority keywords
        high_keywords = [
            'payment', 'invoice', 'money', 'contract', 'agreement',
            'meeting', 'appointment', 'delivery', 'order', 'project'
        ]

        # Count occurrences of keywords
        critical_count = sum(1 for keyword in critical_keywords if keyword in text_lower)
        high_count = sum(1 for keyword in high_keywords if keyword in text_lower)

        if critical_count > 0:
            return 'critical'
        elif high_count > 0 or critical_count > 0:
            return 'high'
        elif len(text) > 100:  # Long messages might contain important details
            return 'medium'
        else:
            return 'low'

    def _categorize_message(self, text: str) -> str:
        """
        Categorize the message based on its content

        Args:
            text: Message text

        Returns:
            Category string
        """
        text_lower = text.lower()

        # Define categories
        categories = {
            'business': ['payment', 'invoice', 'contract', 'order', 'project', 'work', 'business'],
            'personal': ['family', 'friend', 'personal', 'home', 'dinner', 'party'],
            'technical': ['error', 'problem', 'issue', 'bug', 'fix', 'update', 'system'],
            'financial': ['money', 'payment', 'invoice', 'bill', 'cost', 'price', 'expensive'],
            'scheduling': ['meeting', 'appointment', 'when', 'time', 'schedule', 'date', 'event']
        }

        # Check each category
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category

        # Default category
        return 'general'

    def _requires_response(self, text: str) -> bool:
        """
        Determine if the message requires a response

        Args:
            text: Message text

        Returns:
            Boolean indicating if response is required
        """
        text_lower = text.lower()

        # Keywords that suggest a response is needed
        response_keywords = [
            'question', '?', 'ask', 'please', 'help', 'need', 'want',
            'when', 'how', 'what', 'can you', 'would you', 'could you',
            'are you', 'did you', 'do you', 'will you'
        ]

        for keyword in response_keywords:
            if keyword in text_lower:
                return True

        return False


def main():
    """
    Example usage of the WhatsApp watcher
    """
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to the vault directory')
    parser.add_argument('--session', type=str, help='Path to WhatsApp session data')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds (default: 30)')
    parser.add_argument('--keywords', nargs='+', help='Keywords to monitor for important messages')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create and run the WhatsApp watcher
    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        session_path=args.session,
        check_interval=args.interval,
        keywords=args.keywords
    )

    # Run the watcher (this will run indefinitely)
    watcher.run()


if __name__ == "__main__":
    main()