"""
Base Watcher Class - Template for all watchers in the AI Employee system
Follows the pattern defined in the Platinum tier document
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
import json
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers in the AI Employee system.
    All watchers must inherit from this class and implement the required methods.
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: How often to check for updates (in seconds)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create the Needs_Action directory if it doesn't exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Initialize processed items tracking
        self.processed_ids = set()

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Abstract method to check for new items to process.
        Must be implemented by subclasses.

        Returns:
            List of new items to process
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Abstract method to create a markdown file in the Needs_Action folder.
        Must be implemented by subclasses.

        Args:
            item: The item to create an action file for

        Returns:
            Path to the created file
        """
        pass

    def run(self):
        """
        Main run loop for the watcher.
        Continuously checks for updates at the specified interval.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')

        while True:
            try:
                items = self.check_for_updates()

                for item in items:
                    # Create an action file for each new item
                    action_file_path = self.create_action_file(item)

                    # Add to processed items to avoid duplicates
                    item_id = getattr(item, 'id', str(item))
                    self.processed_ids.add(item_id)

                    self.logger.info(f'Created action file: {action_file_path}')

            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')

            # Wait before the next check
            time.sleep(self.check_interval)


class WatcherManager:
    """
    Manages multiple watchers and runs them concurrently.
    """

    def __init__(self):
        self.watchers = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_watcher(self, watcher: BaseWatcher):
        """
        Add a watcher to the manager.

        Args:
            watcher: An instance of a BaseWatcher subclass
        """
        self.watchers.append(watcher)

    def run_all(self):
        """
        Run all registered watchers concurrently.
        Each watcher runs in its own thread.
        """
        import threading

        threads = []

        for watcher in self.watchers:
            thread = threading.Thread(target=watcher.run)
            thread.daemon = True  # Dies when main thread dies
            threads.append(thread)
            thread.start()

        # Keep the main thread alive
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            self.logger.info("Watcher manager stopped by user")


# Example implementation of a simple file system watcher
class FileSystemWatcher(BaseWatcher):
    """
    Example implementation of a file system watcher.
    Monitors a specific directory for new files and creates action files.
    """

    def __init__(self, vault_path: str, watch_directory: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.watch_directory = Path(watch_directory)
        self.last_seen_files = set()

        # Initially populate the last seen files
        if self.watch_directory.exists():
            self.last_seen_files = {f.name for f in self.watch_directory.iterdir() if f.is_file()}

    def check_for_updates(self) -> list:
        """
        Check the watched directory for new files.

        Returns:
            List of new file paths
        """
        if not self.watch_directory.exists():
            return []

        current_files = {f.name for f in self.watch_directory.iterdir() if f.is_file()}
        new_files = current_files - self.last_seen_files

        # Update the last seen files
        self.last_seen_files = current_files

        # Convert to file paths
        new_file_paths = [self.watch_directory / name for name in new_files]

        return new_file_paths

    def create_action_file(self, file_path) -> Path:
        """
        Create an action file for a new file.

        Args:
            file_path: Path to the new file

        Returns:
            Path to the created action file
        """
        content = f"""---
type: file_drop
original_name: {file_path.name}
size: {file_path.stat().st_size if file_path.exists() else 0}
created: {datetime.now().isoformat()}
status: pending
---

# New File Detected

A new file has been detected in the monitored directory.

## File Details
- Name: {file_path.name}
- Size: {file_path.stat().st_size if file_path.exists() else 0} bytes
- Path: {file_path}

## Recommended Actions
- [ ] Review the file content
- [ ] Determine appropriate processing
- [ ] Move file to appropriate location
- [ ] Update system records

## File Preview (first 500 characters)
```
{file_path.read_text(encoding='utf-8', errors='ignore')[:500] if file_path.exists() else 'File not found'}
```
"""

        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        action_filename = f"FILE_DROP_{timestamp}_{file_path.name.replace('.', '_')}.md"
        action_filepath = self.needs_action / action_filename

        # Write the content to the action file
        action_filepath.write_text(content, encoding='utf-8')

        return action_filepath


def main():
    """
    Example usage of the watcher system.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Run AI Employee watchers')
    parser.add_argument('--vault', type=str, required=True, help='Path to the vault directory')
    parser.add_argument('--watch-dir', type=str, help='Directory to watch for new files')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create watcher manager
    manager = WatcherManager()

    # Add file system watcher if directory is specified
    if args.watch_dir:
        fs_watcher = FileSystemWatcher(args.vault, args.watch_dir)
        manager.add_watcher(fs_watcher)

    # Run all watchers
    manager.run_all()


if __name__ == "__main__":
    main()