"""
WhatsApp Watcher
Monitors WhatsApp messages for urgent communications
Uses whatsapp-web.js via Node.js subprocess or browser automation
"""
import json
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp for urgent messages"""

    def __init__(self, vault_path: str, session_path: str = './whatsapp_session'):
        super().__init__(vault_path, check_interval=60)  # Check every minute
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.messages_file = self.session_path / 'messages.json'
        self.processed_ids = self._load_processed_ids()

        # Urgent keywords to monitor
        self.urgent_keywords = ['urgent', 'asap', 'emergency', 'help', 'critical', 'important']

        # Important contacts (customize this)
        self.important_contacts = ['Family', 'Boss', 'Client']

    def _load_processed_ids(self) -> set:
        """Load already processed message IDs"""
        processed_file = self.session_path / 'processed.json'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                return set(json.load(f))
        return set()

    def _save_processed_id(self, message_id: str):
        """Save processed message ID"""
        self.processed_ids.add(message_id)
        processed_file = self.session_path / 'processed.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def check_for_updates(self) -> list:
        """
        Check for new WhatsApp messages

        Note: This is a simplified implementation. In production, you would:
        1. Use whatsapp-web.js with Node.js
        2. Use Playwright/Selenium for browser automation
        3. Use WhatsApp Business API (if available)

        For this hackathon, we'll monitor a messages.json file that would be
        populated by a separate WhatsApp monitoring script.

        Returns:
            List of new urgent messages
        """
        try:
            if not self.messages_file.exists():
                # Create sample file structure
                self.messages_file.write_text('[]', encoding='utf-8')
                return []

            with open(self.messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)

            # Filter for new urgent messages
            new_urgent = []
            for msg in messages:
                msg_id = msg.get('id', '')

                # Skip if already processed
                if msg_id in self.processed_ids:
                    continue

                # Check if urgent
                if self._is_urgent(msg):
                    new_urgent.append(msg)
                    self._save_processed_id(msg_id)

            return new_urgent

        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}')
            return []

    def _is_urgent(self, message: dict) -> bool:
        """Determine if a message is urgent"""
        text = message.get('text', '').lower()
        sender = message.get('sender', '')

        # Check for urgent keywords
        if any(keyword in text for keyword in self.urgent_keywords):
            return True

        # Check if from important contact
        if any(contact.lower() in sender.lower() for contact in self.important_contacts):
            return True

        return False

    def create_action_file(self, message: dict) -> Path:
        """
        Create an action file for an urgent WhatsApp message

        Args:
            message: WhatsApp message dict with keys: id, sender, text, timestamp

        Returns:
            Path to the created action file
        """
        message_id = message.get('id', 'unknown')
        sender = message.get('sender', 'Unknown')
        text = message.get('text', '')
        timestamp = message.get('timestamp', datetime.now().isoformat())

        # Determine priority
        priority = 'high' if self._is_urgent(message) else 'normal'

        # Create filename
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_sender = ''.join(c for c in sender[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        action_filename = f'WHATSAPP_{now}_{safe_sender}.md'
        action_filepath = self.needs_action / action_filename

        # Create markdown content
        content = f"""---
type: whatsapp
message_id: {message_id}
from: {sender}
timestamp: {timestamp}
detected: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# Urgent WhatsApp Message from {sender}

## Message Details
- **From**: {sender}
- **Time**: {timestamp}
- **Priority**: {priority}

## Message Content
```
{text}
```

## Suggested Actions
- [ ] Read and understand the message
- [ ] Determine urgency level
- [ ] Draft response if needed
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Response Template
```
Hi {sender},

[Your response here]

Thanks
```

## Notes
Message automatically detected by WhatsApp Watcher.
Flagged as urgent based on keywords or sender importance.

---
*Generated by WhatsAppWatcher at {datetime.now().isoformat()}*
"""

        # Write the action file
        action_filepath.write_text(content, encoding='utf-8')

        self.logger.info(f'Created action file: {action_filepath.name}')

        # Log to vault logs
        self._log_action(message, action_filepath)

        return action_filepath

    def _log_action(self, message: dict, action_file: Path):
        """Log the action to the vault logs"""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'{today}.log'

        sender = message.get('sender', 'Unknown')
        log_entry = f"[{datetime.now().isoformat()}] WHATSAPP_URGENT: {sender} -> {action_file.name}\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'vault'

    watcher = WhatsAppWatcher(str(vault_path))
    watcher.run()
