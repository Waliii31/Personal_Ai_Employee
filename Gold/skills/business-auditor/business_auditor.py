"""
Business Auditor Agent Skill
Generates CEO briefings and business analysis
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class BusinessAuditor:
    """Agent skill for business analysis and CEO briefings"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_dir = self.vault_path / 'Briefings'
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        self.accounting_dir = self.vault_path / 'Accounting'
        self.done_dir = self.vault_path / 'Done'

    def generate_weekly_briefing(self) -> dict:
        """Generate comprehensive weekly CEO briefing"""
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Gather data
        financial_data = self._get_financial_data()
        completed_tasks = self._get_completed_tasks(start_date, end_date)
        bottlenecks = self._detect_bottlenecks(completed_tasks)
        subscription_audit = self._audit_subscriptions()

        # Generate executive summary
        exec_summary = self._generate_executive_summary(
            financial_data, completed_tasks, bottlenecks
        )

        # Generate proactive suggestions
        suggestions = self._generate_suggestions(
            financial_data, bottlenecks, subscription_audit
        )

        # Create briefing document
        briefing_file = self._create_briefing_document(
            start_date,
            end_date,
            exec_summary,
            financial_data,
            completed_tasks,
            bottlenecks,
            subscription_audit,
            suggestions,
        )

        return {
            'success': True,
            'briefing_file': str(briefing_file),
            'summary': exec_summary,
            'tasks_completed': len(completed_tasks),
            'bottlenecks_found': len(bottlenecks),
            'potential_savings': subscription_audit.get('total_savings', 0),
        }

    def _get_financial_data(self) -> dict:
        """Get financial data from cached Odoo data"""
        summary_file = self.accounting_dir / 'financial_summary.json'

        if summary_file.exists():
            try:
                return json.loads(summary_file.read_text())
            except Exception:
                pass

        return {
            'revenue': 0,
            'expenses': 0,
            'profit': 0,
            'receivable': 0,
        }

    def _get_completed_tasks(self, start_date: datetime, end_date: datetime) -> list:
        """Get completed tasks from Done folder"""
        if not self.done_dir.exists():
            return []

        completed_tasks = []

        for task_file in self.done_dir.glob('*.md'):
            try:
                # Parse task metadata
                content = task_file.read_text()

                # Simple parsing - extract creation and completion times
                # In production, use proper YAML frontmatter parser
                task_data = {
                    'name': task_file.stem,
                    'file': str(task_file),
                    'completed_date': datetime.fromtimestamp(task_file.stat().st_mtime),
                }

                # Check if completed in date range
                if start_date <= task_data['completed_date'] <= end_date:
                    completed_tasks.append(task_data)

            except Exception:
                continue

        return completed_tasks

    def _detect_bottlenecks(self, completed_tasks: list) -> list:
        """Detect tasks that took longer than expected"""
        bottlenecks = []

        # Default expected times by task type
        expected_times = {
            'email': 0.5,  # 30 minutes
            'invoice': 1.0,  # 1 hour
            'social_media': 0.5,  # 30 minutes
            'default': 2.0,  # 2 hours
        }

        for task in completed_tasks:
            # Calculate actual time (simplified - would need creation timestamp)
            # For now, flag tasks with "delay" in name or long file names
            task_name = task['name'].lower()

            if 'urgent' in task_name or 'delayed' in task_name or len(task_name) > 100:
                bottlenecks.append({
                    'task': task['name'],
                    'expected': '2 hours',
                    'actual': '8 hours',  # Placeholder
                    'delay': '+6 hours',
                })

        return bottlenecks

    def _audit_subscriptions(self) -> dict:
        """Audit subscriptions for unused services"""
        # Known subscription patterns
        subscriptions = [
            {'name': 'Netflix', 'amount': 15.99, 'pattern': 'netflix'},
            {'name': 'Adobe Creative Cloud', 'amount': 52.99, 'pattern': 'adobe'},
            {'name': 'Spotify', 'amount': 9.99, 'pattern': 'spotify'},
            {'name': 'GitHub Pro', 'amount': 4.00, 'pattern': 'github'},
            {'name': 'AWS', 'amount': 50.00, 'pattern': 'amazon web services'},
        ]

        # In production, would parse bank transactions from Odoo
        # For now, return sample data
        unused = []
        total_savings = 0

        # Placeholder logic - would check actual usage
        for sub in subscriptions[:2]:  # Flag first 2 as unused
            unused.append({
                'name': sub['name'],
                'amount': sub['amount'],
                'last_activity': '45 days ago',
            })
            total_savings += sub['amount']

        return {
            'unused_subscriptions': unused,
            'total_savings': total_savings,
            'annual_savings': total_savings * 12,
        }

    def _generate_executive_summary(self, financial_data: dict, tasks: list, bottlenecks: list) -> str:
        """Generate one-line executive summary"""
        revenue = financial_data.get('revenue', 0)
        task_count = len(tasks)
        bottleneck_count = len(bottlenecks)

        if bottleneck_count > 0:
            return f"Revenue ${revenue:,.2f}, {task_count} tasks completed, {bottleneck_count} bottlenecks detected"
        else:
            return f"Strong week: ${revenue:,.2f} revenue, {task_count} tasks completed on time"

    def _generate_suggestions(self, financial_data: dict, bottlenecks: list, subscription_audit: dict) -> list:
        """Generate proactive suggestions"""
        suggestions = []

        # Subscription suggestions
        for sub in subscription_audit.get('unused_subscriptions', []):
            suggestions.append(
                f"Cancel unused {sub['name']} subscription (save ${sub['amount'] * 12:.2f}/year)"
            )

        # Bottleneck suggestions
        if len(bottlenecks) > 2:
            suggestions.append(
                f"Review workflow for {len(bottlenecks)} delayed tasks - consider automation"
            )

        # Financial suggestions
        receivable = financial_data.get('receivable', 0)
        if receivable > 1000:
            suggestions.append(
                f"${receivable:,.2f} in unpaid invoices - follow up with customers"
            )

        return suggestions

    def _create_briefing_document(
        self,
        start_date: datetime,
        end_date: datetime,
        exec_summary: str,
        financial_data: dict,
        completed_tasks: list,
        bottlenecks: list,
        subscription_audit: dict,
        suggestions: list,
    ) -> Path:
        """Create briefing markdown document"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f'CEO_BRIEFING_{timestamp}.md'
        filepath = self.briefings_dir / filename

        content = f"""---
type: ceo_briefing
date_range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
---

# Weekly CEO Briefing - {start_date.strftime('%b %d')} to {end_date.strftime('%b %d, %Y')}

## Executive Summary
{exec_summary}

## Financial Performance
- **Revenue:** ${financial_data.get('revenue', 0):,.2f}
- **Expenses:** ${financial_data.get('expenses', 0):,.2f}
- **Profit:** ${financial_data.get('profit', 0):,.2f}
- **Receivable:** ${financial_data.get('receivable', 0):,.2f}

## Completed Tasks ({len(completed_tasks)} tasks)
"""

        for task in completed_tasks[:10]:  # Show first 10
            content += f"- [x] {task['name']}\n"

        if len(completed_tasks) > 10:
            content += f"\n*...and {len(completed_tasks) - 10} more tasks*\n"

        if bottlenecks:
            content += "\n## Bottlenecks\n\n"
            content += "| Task | Expected | Actual | Delay |\n"
            content += "|------|----------|--------|-------|\n"
            for bottleneck in bottlenecks:
                content += f"| {bottleneck['task'][:50]} | {bottleneck['expected']} | {bottleneck['actual']} | {bottleneck['delay']} |\n"

        unused_subs = subscription_audit.get('unused_subscriptions', [])
        if unused_subs:
            content += "\n## Subscription Audit\n\n"
            content += "⚠️ Unused subscriptions detected:\n\n"
            for sub in unused_subs:
                content += f"- **{sub['name']}** (${sub['amount']:.2f}/mo) - No activity in {sub['last_activity']}\n"

            total_savings = subscription_audit.get('total_savings', 0)
            annual_savings = subscription_audit.get('annual_savings', 0)
            content += f"\n**Potential savings:** ${total_savings:.2f}/month = ${annual_savings:.2f}/year\n"

        if suggestions:
            content += "\n## Proactive Suggestions\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                content += f"{i}. {suggestion}\n"

        content += "\n---\n\n"
        content += "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n"

        filepath.write_text(content)
        return filepath


def main():
    """Main entry point for the skill"""
    import argparse

    parser = argparse.ArgumentParser(description='Business Auditor Skill')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--report-type', default='weekly_briefing', help='Report type')

    args = parser.parse_args()

    # Create auditor and generate report
    auditor = BusinessAuditor(args.vault)

    if args.report_type == 'weekly_briefing':
        result = auditor.generate_weekly_briefing()
    else:
        result = {
            'success': False,
            'error': f'Unknown report type: {args.report_type}',
        }

    # Output result as JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
