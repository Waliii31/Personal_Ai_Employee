"""
File System Watcher - Monitors file system for new files and creates action files
Based on the pattern outlined in the Platinum tier document
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from typing import List, Dict, Any
import hashlib


class FileSystemWatcher(BaseWatcher):
    """
    File system watcher implementation that monitors specified directories
    for new files and creates action files for the AI Employee to process.
    """

    def __init__(self, vault_path: str, watch_directories: List[str],
                 file_extensions: List[str] = None, check_interval: int = 30):
        """
        Initialize the file system watcher

        Args:
            vault_path: Path to the Obsidian vault
            watch_directories: List of directories to monitor
            file_extensions: List of file extensions to monitor (None means all)
            check_interval: How often to check for new files (in seconds)
        """
        super().__init__(vault_path, check_interval)

        # Directories to monitor
        self.watch_directories = [Path(d) for d in watch_directories]

        # File extensions to monitor (None means all files)
        self.file_extensions = [ext.lower() for ext in file_extensions] if file_extensions else None

        # Track processed files to avoid duplicates
        self.processed_files = {}

        # Load previously processed files if available
        self._load_processed_files()

    def _load_processed_files(self):
        """
        Load previously processed files from a file to avoid reprocessing
        """
        processed_file = self.vault_path / "processed_files.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = self.processed_files = {}
                    raw_data = json.load(f)
                    for path, info in raw_data.items():
                        self.processed_files[Path(path)] = {
                            'mtime': info['mtime'],
                            'size': info['size'],
                            'hash': info['hash']
                        }
            except Exception as e:
                self.logger.warning(f"Could not load processed files: {e}")

    def _save_processed_files(self):
        """
        Save processed files to a file
        """
        processed_file = self.vault_path / "processed_files.json"
        try:
            # Convert Path keys to strings for JSON serialization
            serializable_data = {}
            for path, info in self.processed_files.items():
                serializable_data[str(path)] = info

            with open(processed_file, 'w') as f:
                json.dump(serializable_data, f)
        except Exception as e:
            self.logger.error(f"Could not save processed files: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check monitored directories for new or modified files

        Returns:
            List of file dictionaries that need processing
        """
        import json

        new_or_modified_files = []

        for watch_dir in self.watch_directories:
            if not watch_dir.exists():
                self.logger.warning(f"Watch directory does not exist: {watch_dir}")
                continue

            # Get all files in the directory
            for file_path in watch_dir.rglob("*"):
                if file_path.is_file():
                    # Check if this file extension is monitored
                    if self.file_extensions:
                        if file_path.suffix.lower() not in self.file_extensions:
                            continue

                    # Get file stats
                    stat = file_path.stat()
                    current_mtime = stat.st_mtime
                    current_size = stat.st_size

                    # Check if file is new or has been modified
                    if file_path not in self.processed_files:
                        # New file
                        file_hash = self._calculate_file_hash(file_path)
                        self.processed_files[file_path] = {
                            'mtime': current_mtime,
                            'size': current_size,
                            'hash': file_hash
                        }
                        new_or_modified_files.append({
                            'path': file_path,
                            'reason': 'new'
                        })
                    else:
                        # Existing file - check if it's been modified
                        prev_info = self.processed_files[file_path]
                        if (current_mtime > prev_info['mtime'] or
                            current_size != prev_info['size']):

                            # File has been modified, check if content changed
                            current_hash = self._calculate_file_hash(file_path)
                            if current_hash != prev_info['hash']:
                                # Content changed
                                self.processed_files[file_path].update({
                                    'mtime': current_mtime,
                                    'size': current_size,
                                    'hash': current_hash
                                })
                                new_or_modified_files.append({
                                    'path': file_path,
                                    'reason': 'modified'
                                })

        # Save processed files
        self._save_processed_files()

        return new_or_modified_files

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate a hash of the file contents to detect changes

        Args:
            file_path: Path to the file

        Returns:
            Hash string
        """
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""

    def create_action_file(self, file_info) -> Path:
        """
        Create an action file for a new or modified file

        Args:
            file_info: Dictionary containing file path and reason

        Returns:
            Path to the created action file
        """
        file_path = file_info['path']
        reason = file_info['reason']

        # Get file details
        stat = file_path.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)

        # Try to read file content preview (first 1000 characters)
        content_preview = ""
        try:
            if file_path.suffix.lower() in ['.txt', '.md', '.csv', '.json', '.py', '.js', '.html', '.css']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_preview = f.read(1000)
            else:
                # For binary files, just show that it's a binary file
                content_preview = f"<Binary file of type {file_path.suffix}>"
        except Exception as e:
            content_preview = f"<Could not read file: {e}>"

        # Determine file type and category
        file_category = self._categorize_file(file_path)

        # Create markdown content
        content = f"""---
type: file_system_event
file_path: "{str(file_path)}"
file_name: "{file_path.name}"
file_extension: "{file_path.suffix}"
file_size: {size}
modified_time: "{mtime.isoformat()}"
event_type: {reason}
category: {file_category}
status: pending
priority: medium
---

# File System Event Detected

## File Details
- **Path:** {str(file_path)}
- **Name:** {file_path.name}
- **Extension:** {file_path.suffix}
- **Size:** {size:,} bytes ({self._format_file_size(size)})
- **Last Modified:** {mtime.isoformat()}
- **Event Type:** {reason.title()}
- **Category:** {file_category}

## File Content Preview
```
{content_preview[:500]}
```

## Recommended Actions
- [ ] Review file content
- [ ] Determine appropriate action
- [ ] Move to appropriate location if needed
- [ ] Update system records
- [ ] Archive if appropriate

## Security Check
- [ ] Verify file source and integrity
- [ ] Check for potential threats
- [ ] Confirm file is expected

## Classification
- **File Type:** {self._classify_file_type(file_path.suffix)}
- **Sensitivity:** {self._assess_sensitivity(file_path.name, content_preview)}
- **Action Required:** {'Yes' if self._requires_action(file_path, content_preview) else 'No'}

## Context
This {'new' if reason == 'new' else 'modified'} file was detected in a monitored directory.
Based on its location and name, it may require processing or categorization.
"""

        # Create a unique filename based on the file path and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean file name for action file
        clean_name = "".join(c for c in file_path.name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        clean_name = clean_name[:50]  # Limit length
        action_filename = f"FILESYS_{timestamp}_{reason.upper()}_{clean_name.replace('.', '_')}.md"
        action_filepath = self.needs_action / action_filename

        # Write the content to the action file
        action_filepath.write_text(content, encoding='utf-8')

        return action_filepath

    def _categorize_file(self, file_path: Path) -> str:
        """
        Categorize a file based on its extension and name

        Args:
            file_path: Path to the file

        Returns:
            Category string
        """
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        # Define categories by extension
        categories = {
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.md'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'data': ['.csv', '.xlsx', '.xls', '.json', '.xml', '.yaml', '.yml'],
            'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.sql'],
            'media': ['.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac'],
            'archive': ['.zip', '.rar', '.tar', '.gz', '.7z'],
            'executable': ['.exe', '.bat', '.sh', '.bin', '.app']
        }

        # Check by extension first
        for category, extensions in categories.items():
            if suffix in extensions:
                return category

        # Check by content or name patterns
        if any(pattern in name for pattern in ['invoice', 'receipt', 'bill', 'statement']):
            return 'financial'
        elif any(pattern in name for pattern in ['contract', 'agreement', 'nda', 'legal']):
            return 'legal'
        elif any(pattern in name for pattern in ['photo', 'pic', 'image']):
            return 'image'
        elif any(pattern in name for pattern in ['backup', 'archive']):
            return 'archive'

        # Default category
        return 'other'

    def _classify_file_type(self, extension: str) -> str:
        """
        Classify the file type based on extension

        Args:
            extension: File extension

        Returns:
            File type string
        """
        extension = extension.lower()

        if extension in ['.pdf', '.doc', '.docx']:
            return 'Document'
        elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'Image'
        elif extension in ['.csv', '.xlsx', '.json']:
            return 'Data'
        elif extension in ['.py', '.js', '.ts', '.html', '.css']:
            return 'Code'
        elif extension in ['.mp3', '.mp4']:
            return 'Media'
        elif extension in ['.zip', '.rar']:
            return 'Archive'
        else:
            return 'Other'

    def _assess_sensitivity(self, filename: str, content: str) -> str:
        """
        Assess the sensitivity of a file based on its name and content

        Args:
            filename: File name
            content: File content preview

        Returns:
            Sensitivity level string
        """
        filename_lower = filename.lower()
        content_lower = content.lower()

        # High sensitivity indicators
        high_indicators = [
            'password', 'credential', 'secret', 'private', 'confidential',
            'ssn', 'social security', 'credit card', 'bank', 'account'
        ]

        # Medium sensitivity indicators
        medium_indicators = [
            'personal', 'contact', 'employee', 'salary', 'hr', 'medical',
            'insurance', 'tax', 'invoice', 'payment'
        ]

        # Check for high sensitivity
        for indicator in high_indicators:
            if indicator in filename_lower or indicator in content_lower:
                return 'High'

        # Check for medium sensitivity
        for indicator in medium_indicators:
            if indicator in filename_lower or indicator in content_lower:
                return 'Medium'

        return 'Low'

    def _requires_action(self, file_path: Path, content: str) -> bool:
        """
        Determine if a file requires action based on its properties

        Args:
            file_path: Path to the file
            content: File content preview

        Returns:
            Boolean indicating if action is required
        """
        # Files that always require action
        if file_path.suffix.lower() in ['.csv', '.json', '.xlsx']:
            return True

        # Files with certain names require action
        name = file_path.name.lower()
        if any(pattern in name for pattern in ['invoice', 'receipt', 'bill', 'contract']):
            return True

        # Files with potential business importance
        if any(pattern in name for pattern in ['report', 'analysis', 'data']):
            return True

        return False

    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"


def main():
    """
    Example usage of the file system watcher
    """
    import argparse

    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to the vault directory')
    parser.add_argument('--watch-dirs', nargs='+', required=True, help='Directories to monitor')
    parser.add_argument('--extensions', nargs='+', help='File extensions to monitor (default: all)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds (default: 30)')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create and run the file system watcher
    watcher = FileSystemWatcher(
        vault_path=args.vault,
        watch_directories=args.watch_dirs,
        file_extensions=args.extensions,
        check_interval=args.interval
    )

    # Run the watcher (this will run indefinitely)
    watcher.run()


if __name__ == "__main__":
    main()