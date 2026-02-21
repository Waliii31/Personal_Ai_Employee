"""
Test script for Bronze Tier AI Employee
Verifies all components are properly set up
"""
from pathlib import Path
import sys


def check_directory_structure(vault_path: Path) -> bool:
    """Check if all required directories exist"""
    required_dirs = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Plans',
        'Logs',
        'Pending_Approval',
        'Approved',
        'Rejected'
    ]

    print("Checking directory structure...")
    all_exist = True
    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists():
            print(f"  [OK] {dir_name}/")
        else:
            print(f"  [MISSING] {dir_name}/")
            all_exist = False

    return all_exist


def check_core_files(vault_path: Path) -> bool:
    """Check if core markdown files exist"""
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md'
    ]

    print("\nChecking core files...")
    all_exist = True
    for file_name in required_files:
        file_path = vault_path / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            print(f"  [MISSING] {file_name}")
            all_exist = False

    return all_exist


def check_watcher_scripts(base_path: Path) -> bool:
    """Check if watcher scripts exist"""
    watchers_dir = base_path / 'watchers'
    required_scripts = [
        'base_watcher.py',
        'filesystem_watcher.py'
    ]

    print("\nChecking watcher scripts...")
    all_exist = True
    for script_name in required_scripts:
        script_path = watchers_dir / script_name
        if script_path.exists():
            print(f"  [OK] {script_name}")
        else:
            print(f"  [MISSING] {script_name}")
            all_exist = False

    return all_exist


def check_dependencies() -> bool:
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")

    try:
        import watchdog
        print(f"  [OK] watchdog")
        return True
    except ImportError:
        print("  [MISSING] watchdog - NOT INSTALLED")
        print("    Run: pip install -r requirements.txt")
        return False


def check_agent_skill(base_path: Path) -> bool:
    """Check if Agent Skill is properly configured"""
    skill_path = base_path / '.claude' / 'skills' / 'process-vault-tasks' / 'SKILL.md'

    print("\nChecking Agent Skills...")
    if skill_path.exists():
        print(f"  [OK] process-vault-tasks skill")
        return True
    else:
        print(f"  [MISSING] process-vault-tasks skill")
        return False


def create_test_file(vault_path: Path) -> bool:
    """Create a test file in Inbox"""
    print("\nCreating test file...")

    inbox = vault_path / 'Inbox'
    test_file = inbox / 'test_document.txt'

    try:
        test_file.write_text(
            "This is a test document for the AI Employee system.\n"
            "If you can see this in Needs_Action, the watcher is working!"
        )
        print(f"  [OK] Created test file: {test_file.name}")
        return True
    except Exception as e:
        print(f"  [FAILED] Failed to create test file: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Bronze Tier AI Employee - System Verification")
    print("=" * 60)
    print()

    # Determine paths
    script_dir = Path(__file__).parent
    vault_path = script_dir / 'AI_Employee_Vault'

    print(f"Base directory: {script_dir}")
    print(f"Vault directory: {vault_path}")
    print()

    # Run checks
    results = []
    results.append(("Directory Structure", check_directory_structure(vault_path)))
    results.append(("Core Files", check_core_files(vault_path)))
    results.append(("Watcher Scripts", check_watcher_scripts(script_dir)))
    results.append(("Python Dependencies", check_dependencies()))
    results.append(("Agent Skills", check_agent_skill(script_dir)))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(result for _, result in results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {name}")

    print()

    if all_passed:
        print("SUCCESS! All checks passed! Bronze tier is ready.")
        print()
        print("Next steps:")
        print("1. Start the watcher: ./start_watcher.sh (or start_watcher.bat)")
        print("2. Drop files in Inbox/ to test")
        print("3. Use Claude Code to process tasks: claude /process-vault-tasks")

        # Offer to create test file
        response = input("\nCreate a test file in Inbox? (y/n): ")
        if response.lower() == 'y':
            create_test_file(vault_path)
            print("\nTest file created! Start the watcher to see it in action.")
    else:
        print("FAILED: Some checks failed. Please fix the issues above.")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
