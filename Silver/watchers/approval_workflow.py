"""
Approval Workflow Manager
Monitors Pending_Approval folder and executes approved actions
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import shutil


class ApprovalWorkflow:
    """Manages human-in-the-loop approval workflow"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.rejected_dir = self.vault_path / 'Rejected'
        self.logs_dir = self.vault_path / 'Logs'

        # Ensure directories exist
        for dir in [self.pending_dir, self.approved_dir, self.rejected_dir, self.logs_dir]:
            dir.mkdir(parents=True, exist_ok=True)

        self.processed_files = set()
        self.approval_log = self.logs_dir / 'approvals.log'

    def monitor(self, check_interval: int = 10):
        """
        Monitor approval folders for user decisions

        Args:
            check_interval: Seconds between checks
        """
        print(f"[Approval Workflow] Monitoring started")
        print(f"[Approval Workflow] Pending: {self.pending_dir}")
        print(f"[Approval Workflow] Approved: {self.approved_dir}")
        print(f"[Approval Workflow] Rejected: {self.rejected_dir}")

        while True:
            try:
                # Check for approved items
                approved_items = list(self.approved_dir.glob('*.md'))
                for item in approved_items:
                    if item not in self.processed_files:
                        self.process_approved(item)
                        self.processed_files.add(item)

                # Check for rejected items
                rejected_items = list(self.rejected_dir.glob('*.md'))
                for item in rejected_items:
                    if item not in self.processed_files:
                        self.process_rejected(item)
                        self.processed_files.add(item)

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("\n[Approval Workflow] Stopped by user")
                break
            except Exception as e:
                print(f"[Approval Workflow] Error: {e}")
                time.sleep(check_interval)

    def process_approved(self, item: Path):
        """
        Process an approved action

        Args:
            item: Path to approved item
        """
        print(f"\n[Approval Workflow] Processing approved: {item.name}")

        try:
            # Read the file to determine action type
            content = item.read_text(encoding='utf-8')
            action_type = self._extract_type(content)

            # Execute based on type
            if action_type == 'linkedin_post':
                self._execute_linkedin_post(item, content)
            elif action_type == 'email':
                self._execute_email(item, content)
            elif action_type == 'whatsapp':
                self._execute_whatsapp_response(item, content)
            else:
                print(f"[Approval Workflow] Unknown action type: {action_type}")

            # Log approval
            self._log_approval(item, 'approved', action_type)

            # Move to Done
            done_dir = self.vault_path / 'Done'
            done_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(done_dir / item.name))

            print(f"[Approval Workflow] ✓ Approved action executed: {item.name}")

        except Exception as e:
            print(f"[Approval Workflow] Error processing approved item: {e}")
            self._log_approval(item, 'error', str(e))

    def process_rejected(self, item: Path):
        """
        Process a rejected action

        Args:
            item: Path to rejected item
        """
        print(f"\n[Approval Workflow] Processing rejected: {item.name}")

        try:
            content = item.read_text(encoding='utf-8')
            action_type = self._extract_type(content)

            # Log rejection
            self._log_approval(item, 'rejected', action_type)

            print(f"[Approval Workflow] ✗ Action rejected: {item.name}")

        except Exception as e:
            print(f"[Approval Workflow] Error processing rejected item: {e}")

    def _extract_type(self, content: str) -> str:
        """Extract action type from frontmatter"""
        for line in content.split('\n'):
            if line.startswith('type:'):
                return line.split('type:')[1].strip()
        return 'unknown'

    def _execute_linkedin_post(self, item: Path, content: str):
        """
        Execute LinkedIn post

        In production, this would use LinkedIn API or browser automation.
        For this hackathon, we'll create a placeholder.
        """
        print(f"[LinkedIn] Publishing post from {item.name}")

        # Extract post content
        post_content = self._extract_content_section(content)

        # In production: Use LinkedIn API or Playwright
        # For now, log the action
        publish_log = self.logs_dir / 'linkedin_posts.log'
        log_entry = f"""
[{datetime.now().isoformat()}]
File: {item.name}
Content Preview: {post_content[:100]}...
Status: Published (simulated)
---
"""
        with open(publish_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(f"[LinkedIn] ✓ Post published (logged to {publish_log.name})")

    def _execute_email(self, item: Path, content: str):
        """
        Execute email sending via MCP server

        In production, this would call the Email MCP server.
        For this hackathon, we'll create a placeholder.
        """
        print(f"[Email] Sending email from {item.name}")

        # Extract email details from frontmatter
        to = self._extract_field(content, 'to')
        subject = self._extract_field(content, 'subject')
        body = self._extract_content_section(content)

        # In production: Call Email MCP server
        # For now, log the action
        email_log = self.logs_dir / 'emails_sent.log'
        log_entry = f"""
[{datetime.now().isoformat()}]
File: {item.name}
To: {to}
Subject: {subject}
Status: Sent (simulated)
---
"""
        with open(email_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(f"[Email] ✓ Email sent (logged to {email_log.name})")

    def _execute_whatsapp_response(self, item: Path, content: str):
        """
        Execute WhatsApp response

        In production, this would use WhatsApp API or browser automation.
        For this hackathon, we'll create a placeholder.
        """
        print(f"[WhatsApp] Sending response from {item.name}")

        # Extract response details
        to = self._extract_field(content, 'from')
        message = self._extract_content_section(content)

        # In production: Use WhatsApp API or Playwright
        # For now, log the action
        whatsapp_log = self.logs_dir / 'whatsapp_sent.log'
        log_entry = f"""
[{datetime.now().isoformat()}]
File: {item.name}
To: {to}
Message Preview: {message[:100]}...
Status: Sent (simulated)
---
"""
        with open(whatsapp_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(f"[WhatsApp] ✓ Response sent (logged to {whatsapp_log.name})")

    def _extract_field(self, content: str, field: str) -> str:
        """Extract a field from frontmatter"""
        for line in content.split('\n'):
            if line.startswith(f'{field}:'):
                return line.split(f'{field}:')[1].strip()
        return 'unknown'

    def _extract_content_section(self, content: str) -> str:
        """Extract main content section from markdown"""
        # Find content after frontmatter
        parts = content.split('---')
        if len(parts) >= 3:
            return parts[2].strip()
        return content

    def _log_approval(self, item: Path, decision: str, action_type: str):
        """Log approval decision"""
        log_entry = f"[{datetime.now().isoformat()}] {decision.upper()}: {action_type} - {item.name}\n"

        with open(self.approval_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def create_approval_request(self, action_type: str, data: Dict) -> Path:
        """
        Create a new approval request

        Args:
            action_type: Type of action (email, linkedin_post, etc.)
            data: Action data

        Returns:
            Path to created approval request
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'APPROVAL_{action_type}_{timestamp}.md'
        filepath = self.pending_dir / filename

        # Create approval request content
        content = f"""---
type: {action_type}
created: {datetime.now().isoformat()}
status: pending_approval
priority: {data.get('priority', 'normal')}
---

# Approval Required: {action_type.replace('_', ' ').title()}

## Action Details
{self._format_data(data)}

## Instructions
**To approve:** Move this file to `/Approved` folder
**To reject:** Move this file to `/Rejected` folder

## Notes
This action requires your approval before execution.
Review the details above and make your decision.

---
*Generated by Approval Workflow at {datetime.now().isoformat()}*
"""

        filepath.write_text(content, encoding='utf-8')
        print(f"[Approval Workflow] Created approval request: {filename}")

        return filepath

    def _format_data(self, data: Dict) -> str:
        """Format data dictionary as markdown"""
        lines = []
        for key, value in data.items():
            if key != 'priority':
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        return '\n'.join(lines)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'vault'

    workflow = ApprovalWorkflow(str(vault_path))

    # Example: Create a test approval request
    if '--test' in sys.argv:
        workflow.create_approval_request('email', {
            'to': 'test@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email requiring approval.',
            'priority': 'normal'
        })
        print("\nTest approval request created. Move it to /Approved or /Rejected to test.")
    else:
        # Start monitoring
        workflow.monitor()
