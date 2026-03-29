"""
Audit Logger
Comprehensive JSON logging for all system actions
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict
import logging


class AuditLogger:
    """Structured audit logging with 90-day retention"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.audit_dir = self.vault_path / 'Logs' / 'audit'
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = 90

        # Setup standard logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup standard logger"""
        logger = logging.getLogger('AuditLogger')
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict[str, Any] = None,
        result: str = 'success',
        details: Dict[str, Any] = None
    ):
        """
        Log an action to audit trail

        Args:
            action_type: Type of action (e.g., 'create_invoice', 'post_to_facebook')
            actor: Who performed the action (e.g., 'claude', 'user', 'system')
            target: What was acted upon (e.g., 'invoice_123', 'facebook_post')
            parameters: Action parameters
            result: Result status ('success', 'failure', 'pending')
            details: Additional details
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'parameters': parameters or {},
            'result': result,
            'details': details or {},
        }

        # Log to daily audit file
        self._append_to_daily_log(audit_entry)

        # Also log to standard logger
        self.logger.info(
            f'[AUDIT] {action_type} by {actor} on {target}: {result}'
        )

    def log_mcp_call(
        self,
        server: str,
        tool: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        actor: str = 'claude'
    ):
        """
        Log MCP server tool call

        Args:
            server: MCP server name (e.g., 'odoo', 'social-media')
            tool: Tool name (e.g., 'create_invoice', 'post_to_facebook')
            parameters: Tool parameters
            result: Tool result
            actor: Who invoked the tool
        """
        self.log_action(
            action_type=f'mcp_call_{server}_{tool}',
            actor=actor,
            target=f'{server}/{tool}',
            parameters=parameters,
            result='success' if result.get('success') else 'failure',
            details={'result': result}
        )

    def log_approval_decision(
        self,
        approval_file: str,
        decision: str,
        actor: str = 'user',
        details: Dict[str, Any] = None
    ):
        """
        Log approval decision

        Args:
            approval_file: Approval file name
            decision: 'approved' or 'rejected'
            actor: Who made the decision
            details: Additional details
        """
        self.log_action(
            action_type='approval_decision',
            actor=actor,
            target=approval_file,
            parameters={'decision': decision},
            result=decision,
            details=details or {}
        )

    def log_external_api_call(
        self,
        service: str,
        endpoint: str,
        method: str,
        status_code: int,
        parameters: Dict[str, Any] = None,
        response: Dict[str, Any] = None
    ):
        """
        Log external API call

        Args:
            service: Service name (e.g., 'facebook', 'odoo', 'twitter')
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            parameters: Request parameters
            response: Response data (sanitized)
        """
        result = 'success' if 200 <= status_code < 300 else 'failure'

        self.log_action(
            action_type='external_api_call',
            actor='system',
            target=f'{service}/{endpoint}',
            parameters={
                'method': method,
                'parameters': parameters or {},
            },
            result=result,
            details={
                'status_code': status_code,
                'response': response or {},
            }
        )

    def query_logs(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        action_type: str = None,
        actor: str = None,
        result: str = None
    ) -> list:
        """
        Query audit logs

        Args:
            start_date: Start date filter
            end_date: End date filter
            action_type: Action type filter
            actor: Actor filter
            result: Result filter

        Returns:
            List of matching audit entries
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        matching_entries = []

        # Iterate through daily log files in date range
        current_date = start_date.date()
        while current_date <= end_date.date():
            log_file = self.audit_dir / f'{current_date.isoformat()}.json'

            if log_file.exists():
                try:
                    entries = json.loads(log_file.read_text())

                    for entry in entries:
                        # Apply filters
                        if action_type and entry.get('action_type') != action_type:
                            continue
                        if actor and entry.get('actor') != actor:
                            continue
                        if result and entry.get('result') != result:
                            continue

                        matching_entries.append(entry)

                except Exception as e:
                    self.logger.error(f'Error reading log file {log_file}: {e}')

            current_date += timedelta(days=1)

        return matching_entries

    def cleanup_old_logs(self):
        """Remove logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed_count = 0

        for log_file in self.audit_dir.glob('*.json'):
            try:
                # Parse date from filename (YYYY-MM-DD.json)
                date_str = log_file.stem
                file_date = datetime.fromisoformat(date_str)

                if file_date < cutoff_date:
                    log_file.unlink()
                    removed_count += 1
                    self.logger.info(f'Removed old log file: {log_file.name}')

            except Exception as e:
                self.logger.error(f'Error processing log file {log_file}: {e}')

        if removed_count > 0:
            self.logger.info(f'Cleaned up {removed_count} old log files')

    def _append_to_daily_log(self, entry: Dict[str, Any]):
        """Append entry to daily log file"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = self.audit_dir / f'{date_str}.json'

        # Read existing entries
        entries = []
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text())
            except Exception:
                pass

        # Append new entry
        entries.append(entry)

        # Write back
        log_file.write_text(json.dumps(entries, indent=2))

    def generate_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate audit summary for last N days

        Args:
            days: Number of days to summarize

        Returns:
            Summary statistics
        """
        start_date = datetime.now() - timedelta(days=days)
        entries = self.query_logs(start_date=start_date)

        summary = {
            'period': f'Last {days} days',
            'total_actions': len(entries),
            'by_action_type': {},
            'by_actor': {},
            'by_result': {},
            'failures': [],
        }

        for entry in entries:
            # Count by action type
            action_type = entry.get('action_type', 'unknown')
            summary['by_action_type'][action_type] = \
                summary['by_action_type'].get(action_type, 0) + 1

            # Count by actor
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1

            # Count by result
            result = entry.get('result', 'unknown')
            summary['by_result'][result] = summary['by_result'].get(result, 0) + 1

            # Collect failures
            if result == 'failure':
                summary['failures'].append({
                    'timestamp': entry.get('timestamp'),
                    'action_type': action_type,
                    'target': entry.get('target'),
                })

        return summary


# Global audit logger instance
_audit_logger = None


def get_audit_logger(vault_path: str = None) -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None and vault_path:
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger
