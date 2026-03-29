"""
Silver Tier Testing Suite
Comprehensive tests for all Silver tier components
"""
import sys
import json
from pathlib import Path
from datetime import datetime


class SilverTierTester:
    """Test all Silver tier requirements"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("Silver Tier Testing Suite")
        print("=" * 60)
        print(f"Vault: {self.vault_path}")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 60)
        print()

        # Test 1: Folder structure
        self.test_folder_structure()

        # Test 2: Vault files
        self.test_vault_files()

        # Test 3: Watcher scripts
        self.test_watcher_scripts()

        # Test 4: MCP server
        self.test_mcp_server()

        # Test 5: Skills
        self.test_skills()

        # Test 6: Orchestrator
        self.test_orchestrator()

        # Test 7: Approval workflow
        self.test_approval_workflow()

        # Print results
        self.print_results()

    def test_folder_structure(self):
        """Test that all required folders exist"""
        print("[TEST] Checking folder structure...")

        required_folders = [
            'vault/Inbox',
            'vault/Needs_Action',
            'vault/Done',
            'vault/Plans',
            'vault/Pending_Approval',
            'vault/Approved',
            'vault/Rejected',
            'vault/Logs',
            'watchers',
            'mcp-servers',
            'skills'
        ]

        for folder in required_folders:
            folder_path = Path(folder)
            if folder_path.exists():
                self.results['passed'].append(f"Folder exists: {folder}")
            else:
                self.results['failed'].append(f"Missing folder: {folder}")

        print("  [OK] Folder structure test complete\n")

    def test_vault_files(self):
        """Test that required vault files exist"""
        print("[TEST] Checking vault files...")

        required_files = [
            'vault/Dashboard.md',
            'vault/Company_Handbook.md',
            'vault/Business_Goals.md'
        ]

        for file in required_files:
            file_path = Path(file)
            if file_path.exists():
                self.results['passed'].append(f"File exists: {file}")
            else:
                self.results['failed'].append(f"Missing file: {file}")

        print("  [OK] Vault files test complete\n")

    def test_watcher_scripts(self):
        """Test that watcher scripts exist"""
        print("[TEST] Checking watcher scripts...")

        required_scripts = [
            'watchers/base_watcher.py',
            'watchers/gmail_watcher.py',
            'watchers/whatsapp_watcher.py',
            'watchers/linkedin_automation.py',
            'watchers/approval_workflow.py'
        ]

        for script in required_scripts:
            script_path = Path(script)
            if script_path.exists():
                self.results['passed'].append(f"Script exists: {script}")
            else:
                self.results['failed'].append(f"Missing script: {script}")

        print("  [OK] Watcher scripts test complete\n")

    def test_mcp_server(self):
        """Test that MCP server exists"""
        print("[TEST] Checking MCP server...")

        required_files = [
            'mcp-servers/email-mcp/index.js',
            'mcp-servers/email-mcp/package.json',
            'mcp-servers/email-mcp/README.md'
        ]

        for file in required_files:
            file_path = Path(file)
            if file_path.exists():
                self.results['passed'].append(f"MCP file exists: {file}")
            else:
                self.results['failed'].append(f"Missing MCP file: {file}")

        # Check if Node.js is installed
        import subprocess
        try:
            result = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.results['passed'].append(f"Node.js installed: {result.stdout.strip()}")
            else:
                self.results['warnings'].append("Node.js not found - MCP server won't work")
        except FileNotFoundError:
            self.results['warnings'].append("Node.js not installed - MCP server won't work")

        print("  [OK] MCP server test complete\n")

    def test_skills(self):
        """Test that Agent Skills exist"""
        print("[TEST] Checking Agent Skills...")

        required_skills = [
            'skills/process-vault-tasks/process_vault_tasks.py',
            'skills/process-vault-tasks/SKILL.md',
            'skills/email-handler/email_handler.py',
            'skills/email-handler/SKILL.md',
            'skills/linkedin-poster/linkedin_poster.py',
            'skills/linkedin-poster/SKILL.md'
        ]

        for skill in required_skills:
            skill_path = Path(skill)
            if skill_path.exists():
                self.results['passed'].append(f"Skill exists: {skill}")
            else:
                self.results['failed'].append(f"Missing skill: {skill}")

        # Check skills-lock.json
        if Path('skills-lock.json').exists():
            self.results['passed'].append("skills-lock.json exists")
        else:
            self.results['failed'].append("Missing skills-lock.json")

        print("  [OK] Agent Skills test complete\n")

    def test_orchestrator(self):
        """Test that orchestrator exists"""
        print("[TEST] Checking orchestrator...")

        if Path('orchestrator.py').exists():
            self.results['passed'].append("orchestrator.py exists")
        else:
            self.results['failed'].append("Missing orchestrator.py")

        print("  [OK] Orchestrator test complete\n")

    def test_approval_workflow(self):
        """Test approval workflow functionality"""
        print("[TEST] Checking approval workflow...")

        # Check if approval directories exist
        approval_dirs = [
            self.vault_path / 'Pending_Approval',
            self.vault_path / 'Approved',
            self.vault_path / 'Rejected'
        ]

        for dir in approval_dirs:
            if dir.exists():
                self.results['passed'].append(f"Approval dir exists: {dir.name}")
            else:
                self.results['failed'].append(f"Missing approval dir: {dir.name}")

        print("  [OK] Approval workflow test complete\n")

    def print_results(self):
        """Print test results"""
        print("=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print()

        print(f"[PASS] PASSED: {len(self.results['passed'])}")
        print(f"[FAIL] FAILED: {len(self.results['failed'])}")
        print(f"[WARN] WARNINGS: {len(self.results['warnings'])}")
        print()

        if self.results['failed']:
            print("FAILURES:")
            for failure in self.results['failed']:
                print(f"  [X] {failure}")
            print()

        if self.results['warnings']:
            print("WARNINGS:")
            for warning in self.results['warnings']:
                print(f"  [!] {warning}")
            print()

        # Silver Tier Requirements Check
        print("=" * 60)
        print("SILVER TIER REQUIREMENTS")
        print("=" * 60)
        print()

        requirements = {
            "Multiple Watcher Scripts (2+)": self._check_watchers(),
            "LinkedIn Posting Automation": self._check_linkedin(),
            "Claude Reasoning Loop (Plan.md)": self._check_plans(),
            "MCP Server Implementation": self._check_mcp(),
            "Human-in-the-Loop Workflow": self._check_approval(),
            "Scheduling System": self._check_scheduler(),
            "Agent Skills": self._check_skills_requirement()
        }

        for req, status in requirements.items():
            symbol = "[OK]" if status else "[X]"
            print(f"  {symbol} {req}")

        print()

        # Overall status
        all_passed = all(requirements.values()) and len(self.results['failed']) == 0

        if all_passed:
            print("=" * 60)
            print("*** SILVER TIER COMPLETE! ***")
            print("=" * 60)
            print()
            print("All requirements met. You can now:")
            print("1. Run the orchestrator: python orchestrator.py ./vault")
            print("2. Set up scheduling: ./setup_scheduler.bat (Windows)")
            print("3. Configure MCP server in Claude Code settings")
            print("4. Start using your AI Employee!")
        else:
            print("=" * 60)
            print("*** SILVER TIER INCOMPLETE ***")
            print("=" * 60)
            print()
            print("Please address the failures above to complete Silver Tier.")

    def _check_watchers(self) -> bool:
        """Check if multiple watchers exist"""
        watchers = ['gmail_watcher.py', 'whatsapp_watcher.py']
        return all((Path('watchers') / w).exists() for w in watchers)

    def _check_linkedin(self) -> bool:
        """Check if LinkedIn automation exists"""
        return Path('watchers/linkedin_automation.py').exists()

    def _check_plans(self) -> bool:
        """Check if Plans directory exists"""
        return (self.vault_path / 'Plans').exists()

    def _check_mcp(self) -> bool:
        """Check if MCP server exists"""
        return Path('mcp-servers/email-mcp/index.js').exists()

    def _check_approval(self) -> bool:
        """Check if approval workflow exists"""
        return Path('watchers/approval_workflow.py').exists()

    def _check_scheduler(self) -> bool:
        """Check if scheduler scripts exist"""
        return Path('setup_scheduler.bat').exists() or Path('setup_scheduler.sh').exists()

    def _check_skills_requirement(self) -> bool:
        """Check if Agent Skills are implemented"""
        return Path('skills-lock.json').exists()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = './vault'

    tester = SilverTierTester(vault_path)
    tester.run_all_tests()


if __name__ == '__main__':
    main()
