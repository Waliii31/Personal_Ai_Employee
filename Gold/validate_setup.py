"""
Gold Tier System Validation Script
Tests all components to ensure proper setup
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class GoldTierValidator:
    """Validates Gold Tier installation and configuration"""

    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []

    def check(self, name: str, condition: bool, error_msg: str = None, warning: bool = False):
        """Record a check result"""
        if condition:
            self.results.append(f"[OK] {name}")
            return True
        else:
            msg = error_msg or f"{name} failed"
            if warning:
                self.warnings.append(f"[WARN] {msg}")
            else:
                self.errors.append(f"[FAIL] {msg}")
            return False

    def validate_directory_structure(self):
        """Validate vault directory structure"""
        print("\n=== Validating Directory Structure ===")

        vault = Path('vault')
        required_dirs = [
            'Needs_Action',
            'Pending_Approval',
            'Approved',
            'Rejected',
            'Done',
            'Accounting',
            'Social_Media/Drafts',
            'Briefings',
            'Logs/audit',
            'Logs/errors',
            'Logs/loop_state',
        ]

        for dir_path in required_dirs:
            full_path = vault / dir_path
            self.check(
                f"Directory: {dir_path}",
                full_path.exists() and full_path.is_dir(),
                f"Missing directory: {dir_path}"
            )

    def validate_mcp_servers(self):
        """Validate MCP server files"""
        print("\n=== Validating MCP Servers ===")

        # Odoo MCP
        odoo_files = [
            'mcp-servers/odoo-mcp/index.js',
            'mcp-servers/odoo-mcp/odoo_client.js',
            'mcp-servers/odoo-mcp/package.json',
            'mcp-servers/odoo-mcp/README.md',
        ]

        for file_path in odoo_files:
            self.check(
                f"Odoo MCP: {Path(file_path).name}",
                Path(file_path).exists(),
                f"Missing file: {file_path}"
            )

        # Social Media MCP
        social_files = [
            'mcp-servers/social-media-mcp/index.js',
            'mcp-servers/social-media-mcp/facebook_api.js',
            'mcp-servers/social-media-mcp/instagram_api.js',
            'mcp-servers/social-media-mcp/twitter_api.js',
            'mcp-servers/social-media-mcp/package.json',
        ]

        for file_path in social_files:
            self.check(
                f"Social Media MCP: {Path(file_path).name}",
                Path(file_path).exists(),
                f"Missing file: {file_path}"
            )

    def validate_watchers(self):
        """Validate watcher files"""
        print("\n=== Validating Watchers ===")

        watchers = [
            'watchers/facebook_watcher.py',
            'watchers/instagram_watcher.py',
            'watchers/twitter_watcher.py',
            'watchers/odoo_sync_watcher.py',
            'watchers/briefing_scheduler.py',
        ]

        for watcher in watchers:
            self.check(
                f"Watcher: {Path(watcher).name}",
                Path(watcher).exists(),
                f"Missing watcher: {watcher}"
            )

    def validate_skills(self):
        """Validate agent skills"""
        print("\n=== Validating Agent Skills ===")

        skills = [
            ('accounting-assistant', 'accounting_assistant.py'),
            ('social-media-manager', 'social_media_manager.py'),
            ('business-auditor', 'business_auditor.py'),
            ('task-orchestrator', 'task_orchestrator.py'),
        ]

        for skill_dir, skill_file in skills:
            skill_path = Path(f'skills/{skill_dir}/{skill_file}')
            skill_doc = Path(f'skills/{skill_dir}/SKILL.md')

            self.check(
                f"Skill: {skill_dir}",
                skill_path.exists(),
                f"Missing skill: {skill_path}"
            )

            self.check(
                f"Skill doc: {skill_dir}",
                skill_doc.exists(),
                f"Missing skill documentation: {skill_doc}",
                warning=True
            )

    def validate_core_files(self):
        """Validate core system files"""
        print("\n=== Validating Core Files ===")

        core_files = [
            'orchestrator.py',
            'orchestrator_config.json',
            'ralph_wiggum_loop.py',
            'error_recovery.py',
            'audit_logger.py',
            'init_vault.py',
            'requirements.txt',
            '.env.example',
        ]

        for file_path in core_files:
            self.check(
                f"Core file: {file_path}",
                Path(file_path).exists(),
                f"Missing core file: {file_path}"
            )

    def validate_documentation(self):
        """Validate documentation files"""
        print("\n=== Validating Documentation ===")

        docs = [
            'README.md',
            'QUICKSTART.md',
            'ARCHITECTURE.md',
            'COMPLETION_SUMMARY.md',
        ]

        for doc in docs:
            self.check(
                f"Documentation: {doc}",
                Path(doc).exists(),
                f"Missing documentation: {doc}",
                warning=True
            )

    def validate_odoo_setup(self):
        """Validate Odoo setup files"""
        print("\n=== Validating Odoo Setup ===")

        odoo_files = [
            'odoo-integration/docker-compose.yml',
            'odoo-integration/config/odoo.conf',
            'odoo-integration/setup_guide.md',
        ]

        for file_path in odoo_files:
            self.check(
                f"Odoo: {Path(file_path).name}",
                Path(file_path).exists(),
                f"Missing Odoo file: {file_path}"
            )

    def validate_configuration(self):
        """Validate configuration files"""
        print("\n=== Validating Configuration ===")

        # Check orchestrator config
        config_file = Path('orchestrator_config.json')
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                self.check(
                    "Orchestrator config valid JSON",
                    True
                )

                self.check(
                    "Orchestrator config has watchers",
                    'watchers' in config and len(config['watchers']) > 0
                )

                self.check(
                    "Orchestrator config has MCP servers",
                    'mcp_servers' in config and len(config['mcp_servers']) > 0
                )
            except Exception as e:
                self.check(
                    "Orchestrator config valid JSON",
                    False,
                    f"Invalid JSON in orchestrator_config.json: {e}"
                )

        # Check .env.example
        env_example = Path('.env.example')
        if env_example.exists():
            content = env_example.read_text()
            required_vars = [
                'ODOO_URL',
                'ODOO_DB',
                'ODOO_USERNAME',
                'FACEBOOK_PAGE_ID',
                'INSTAGRAM_USER_ID',
                'TWITTER_BEARER_TOKEN',
            ]

            for var in required_vars:
                self.check(
                    f"Env var template: {var}",
                    var in content,
                    f"Missing environment variable template: {var}",
                    warning=True
                )

    def check_dependencies(self):
        """Check if dependencies can be imported"""
        print("\n=== Checking Python Dependencies ===")

        try:
            import dotenv
            self.check("Python: python-dotenv", True)
        except ImportError:
            self.check("Python: python-dotenv", False, "Run: pip install python-dotenv", warning=True)

        try:
            import watchdog
            self.check("Python: watchdog", True)
        except ImportError:
            self.check("Python: watchdog", False, "Run: pip install watchdog", warning=True)

        try:
            import requests
            self.check("Python: requests", True)
        except ImportError:
            self.check("Python: requests", False, "Run: pip install requests", warning=True)

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)

        print(f"\n[OK] Passed: {len(self.results)}")
        print(f"[FAIL] Failed: {len(self.errors)}")
        print(f"[WARN] Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n=== ERRORS ===")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n=== WARNINGS ===")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors:
            print("\n[SUCCESS] Gold Tier installation is VALID!")
            print("\nNext steps:")
            print("1. Follow QUICKSTART.md to set up Odoo")
            print("2. Configure .env with your credentials")
            print("3. Test Odoo MCP connection")
            print("4. Start the orchestrator")
        else:
            print("\n[ERROR] Gold Tier installation has ERRORS!")
            print("Please fix the errors above before proceeding.")

        print("\n" + "="*60)

        return len(self.errors) == 0

    def run(self):
        """Run all validations"""
        print("Gold Tier System Validation")
        print(f"Timestamp: {datetime.now().isoformat()}")

        self.validate_directory_structure()
        self.validate_mcp_servers()
        self.validate_watchers()
        self.validate_skills()
        self.validate_core_files()
        self.validate_documentation()
        self.validate_odoo_setup()
        self.validate_configuration()
        self.check_dependencies()

        return self.generate_report()


if __name__ == '__main__':
    validator = GoldTierValidator()
    success = validator.run()
    sys.exit(0 if success else 1)
