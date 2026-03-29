"""
Test Gmail Watcher Path Configuration
"""
from pathlib import Path

def test_gmail_paths():
    """Test that Gmail watcher can find credentials"""

    print("Testing Gmail Watcher Path Configuration")
    print("=" * 60)

    # Get paths
    script_dir = Path(__file__).parent
    silver_dir = script_dir
    credentials_path = silver_dir / 'credentials.json'
    token_path = silver_dir / 'token.pickle'

    print(f"\nScript directory: {script_dir}")
    print(f"Silver directory: {silver_dir}")
    print(f"Credentials path: {credentials_path}")
    print(f"Token path: {token_path}")

    # Check if credentials exist
    print("\n" + "=" * 60)
    print("Checking files...")
    print("=" * 60)

    if credentials_path.exists():
        print(f"[OK] credentials.json found at: {credentials_path}")
    else:
        print(f"[MISSING] credentials.json not found at: {credentials_path}")
        print(f"\nPlease place credentials.json in: {silver_dir}")
        print("See GMAIL_SETUP.md for instructions")

    if token_path.exists():
        print(f"[OK] token.pickle found at: {token_path}")
        print("     (Already authenticated)")
    else:
        print(f"[INFO] token.pickle not found at: {token_path}")
        print("       (Not authenticated yet - run gmail_watcher.py to authenticate)")

    print("\n" + "=" * 60)

    # Test watcher import
    try:
        import sys
        sys.path.insert(0, str(silver_dir / 'watchers'))
        from gmail_watcher import GmailWatcher
        print("[OK] Gmail watcher module can be imported")

        # Check the path logic
        watcher_script = silver_dir / 'watchers' / 'gmail_watcher.py'
        if watcher_script.exists():
            print(f"[OK] Gmail watcher script found at: {watcher_script}")

    except Exception as e:
        print(f"[ERROR] Failed to import gmail_watcher: {e}")

    print("=" * 60)
    print("\nNext steps:")
    if not credentials_path.exists():
        print("1. Download credentials.json from Google Cloud Console")
        print(f"2. Place it at: {credentials_path}")
        print("3. Run: cd watchers && python gmail_watcher.py ../vault")
    elif not token_path.exists():
        print("1. Run: cd watchers && python gmail_watcher.py ../vault")
        print("2. Complete OAuth flow in browser")
        print("3. Press Ctrl+C after authentication")
    else:
        print("1. Gmail is configured and authenticated!")
        print("2. Run: cd watchers && python gmail_watcher.py ../vault")
        print("3. Or start orchestrator: python orchestrator.py ./vault")

if __name__ == '__main__':
    test_gmail_paths()
