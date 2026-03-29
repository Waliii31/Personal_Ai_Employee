#!/usr/bin/env python3
"""
Orchestrator.py - The master process for the AI Employee system
Manages all components: watchers, MCP servers, and file-based coordination
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages subprocesses for the AI Employee system"""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True

    def start_process(self, name: str, cmd: List[str], cwd: str = ".") -> bool:
        """Start a subprocess and store its reference"""
        try:
            if name in self.processes:
                logger.warning(f"Process {name} already running, stopping first")
                self.stop_process(name)

            logger.info(f"Starting process: {name} with command: {' '.join(cmd)}")
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes[name] = proc
            logger.info(f"Started process {name} with PID {proc.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start process {name}: {e}")
            return False

    def stop_process(self, name: str) -> bool:
        """Stop a subprocess by name"""
        if name not in self.processes:
            logger.warning(f"Process {name} not found")
            return False

        proc = self.processes[name]
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
            except subprocess.TimeoutExpired:
                proc.kill()  # Force kill if not responding
                proc.wait()  # Wait for process to actually terminate
            del self.processes[name]
            logger.info(f"Stopped process {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop process {name}: {e}")
            return False

    def stop_all(self):
        """Stop all managed processes"""
        logger.info("Stopping all processes...")
        for name in list(self.processes.keys()):
            self.stop_process(name)
        self.running = False

class FileWatcher:
    """Monitors file system changes in the vault"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.rejected_path = self.vault_path / "Rejected"
        self.in_progress_path = self.vault_path / "In_Progress"
        self.plans_path = self.vault_path / "Plans"
        self.logs_path = self.vault_path / "Logs"

        # Create required directories
        for path in [
            self.needs_action_path,
            self.done_path,
            self.pending_approval_path,
            self.approved_path,
            self.rejected_path,
            self.in_progress_path,
            self.plans_path,
            self.logs_path
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def check_needs_action(self) -> List[Path]:
        """Check for new files in Needs_Action folder"""
        files = []
        if self.needs_action_path.exists():
            files = list(self.needs_action_path.glob("*.md"))
        return files

    def check_pending_approval(self) -> List[Path]:
        """Check for files in Pending_Approval folder"""
        files = []
        if self.pending_approval_path.exists():
            files = list(self.pending_approval_path.glob("*.md"))
        return files

    def check_approved(self) -> List[Path]:
        """Check for files in Approved folder"""
        files = []
        if self.approved_path.exists():
            files = list(self.approved_path.glob("*.md"))
        return files

    def move_file_to_in_progress(self, file_path: Path, agent_name: str) -> Optional[Path]:
        """Move a file to In_Progress folder with agent-specific subfolder"""
        agent_folder = self.in_progress_path / agent_name
        agent_folder.mkdir(exist_ok=True)

        new_path = agent_folder / file_path.name
        file_path.rename(new_path)
        logger.info(f"Moved {file_path.name} to in-progress for {agent_name}")
        return new_path

class MCPManager:
    """Manages MCP (Model Context Protocol) servers"""

    def __init__(self, config_path: str = "./mcp-config.json"):
        self.config_path = config_path
        self.servers: Dict[str, subprocess.Popen] = {}

    def start_server(self, name: str, command: List[str]) -> bool:
        """Start an MCP server"""
        try:
            logger.info(f"Starting MCP server: {name}")
            proc = subprocess.Popen(command)
            self.servers[name] = proc
            logger.info(f"MCP server {name} started with PID {proc.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start MCP server {name}: {e}")
            return False

    def stop_all_servers(self):
        """Stop all MCP servers"""
        for name, proc in self.servers.items():
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error stopping MCP server {name}: {e}")

class AIEmployeeOrchestrator:
    """Main orchestrator for the AI Employee system"""

    def __init__(self, vault_path: str = "./vault"):
        self.vault_path = Path(vault_path)
        self.file_watcher = FileWatcher(vault_path)
        self.process_manager = ProcessManager()
        self.mcp_manager = MCPManager()
        self.agent_name = os.getenv("AGENT_NAME", "local-agent")
        self.running = True

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()

    def start_watchers(self):
        """Start all watcher processes"""
        # Gmail watcher
        self.process_manager.start_process(
            "gmail_watcher",
            ["python", "watchers/gmail_watcher.py", "--vault", str(self.vault_path)]
        )

        # WhatsApp watcher
        self.process_manager.start_process(
            "whatsapp_watcher",
            ["python", "watchers/whatsapp_watcher.py", "--vault", str(self.vault_path)]
        )

        # File system watcher
        self.process_manager.start_process(
            "filesystem_watcher",
            ["python", "watchers/filesystem_watcher.py", "--vault", str(self.vault_path)]
        )

        # Finance watcher
        self.process_manager.start_process(
            "finance_watcher",
            ["python", "watchers/finance_watcher.py", "--vault", str(self.vault_path)]
        )

    def start_mcp_servers(self):
        """Start MCP servers"""
        # Email MCP server
        self.mcp_manager.start_server(
            "email_mcp",
            ["node", "mcp-servers/email-mcp/index.js"]
        )

        # Browser MCP server
        self.mcp_manager.start_server(
            "browser_mcp",
            ["npx", "@anthropic/browser-mcp"]
        )

    def process_needs_action(self):
        """Process files in Needs_Action folder"""
        files = self.file_watcher.check_needs_action()
        for file_path in files:
            # Claim the task by moving it to in-progress
            in_progress_path = self.file_watcher.move_file_to_in_progress(file_path, self.agent_name)
            if in_progress_path:
                # Trigger Claude to process this file
                self.trigger_claude_processing(in_progress_path)

    def trigger_claude_processing(self, file_path: Path):
        """Trigger Claude to process a file"""
        # This would call Claude Code to process the file
        logger.info(f"Triggering Claude processing for {file_path}")

        # In a real implementation, this would call Claude with the appropriate prompt
        # For now, we'll simulate by checking if it needs approval
        content = file_path.read_text()

        # If the file contains "REQUIRES_APPROVAL", move to pending approval
        if "REQUIRES_APPROVAL" in content.upper():
            new_path = self.file_watcher.pending_approval_path / file_path.name
            file_path.rename(new_path)
            logger.info(f"Moved {file_path.name} to pending approval")
        else:
            # Otherwise move to done
            new_path = self.file_watcher.done_path / file_path.name
            file_path.rename(new_path)
            logger.info(f"Processed {file_path.name} and moved to done")

    def process_approvals(self):
        """Process approved files"""
        approved_files = self.file_watcher.check_approved()
        for file_path in approved_files:
            logger.info(f"Processing approved file: {file_path.name}")
            # Execute the action specified in the file
            self.execute_approved_action(file_path)

            # Move to done
            done_path = self.file_watcher.done_path / file_path.name
            file_path.rename(done_path)

    def execute_approved_action(self, file_path: Path):
        """Execute an approved action"""
        content = file_path.read_text()
        logger.info(f"Executing action from {file_path.name}")
        # In a real implementation, this would parse the file and execute the appropriate action
        # via the appropriate MCP server

    def run_health_check(self):
        """Perform system health checks"""
        # Check if all processes are running
        # Check disk space
        # Check network connectivity
        logger.info("Performing health check...")

        # Log current status of important directories
        needs_action_count = len(list(self.file_watcher.needs_action_path.glob("*.md")))
        pending_approval_count = len(list(self.file_watcher.pending_approval_path.glob("*.md")))

        logger.info(f"Health check - Needs Action: {needs_action_count}, Pending Approval: {pending_approval_count}")

    def run(self):
        """Main run loop"""
        logger.info("Starting AI Employee Orchestrator...")

        # Start all components
        self.start_watchers()
        self.start_mcp_servers()

        # Main loop
        while self.running:
            try:
                # Process any pending tasks
                self.process_needs_action()

                # Process any approved actions
                self.process_approvals()

                # Perform periodic health checks
                current_time = datetime.now().minute
                if current_time % 5 == 0:  # Every 5 minutes
                    self.run_health_check()

                # Sleep briefly to prevent busy waiting
                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying

        self.shutdown()

    def shutdown(self):
        """Gracefully shut down the orchestrator"""
        logger.info("Shutting down orchestrator...")
        self.running = False
        self.process_manager.stop_all()
        self.mcp_manager.stop_all_servers()
        logger.info("Orchestrator shutdown complete")

if __name__ == "__main__":
    # Create vault directory if it doesn't exist
    vault_dir = os.getenv("VAULT_PATH", "./vault")
    Path(vault_dir).mkdir(parents=True, exist_ok=True)

    # Initialize and run the orchestrator
    orchestrator = AIEmployeeOrchestrator(vault_dir)
    orchestrator.run()