"""
Ralph Wiggum Loop
Autonomous iteration engine for multi-step task completion

Named after Ralph Wiggum's famous line "I'm helping!" - this loop
keeps Claude working on a task until it's complete or max iterations reached.
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import json


class RalphWiggumLoop:
    """Autonomous iteration engine for task completion"""

    def __init__(self, vault_path: str, max_iterations: int = 10, timeout: int = 300):
        """
        Initialize Ralph Wiggum loop

        Args:
            vault_path: Path to vault
            max_iterations: Maximum iterations before stopping
            timeout: Timeout per iteration in seconds
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done_dir = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.state_dir = self.vault_path / 'Logs' / 'loop_state'
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def run_task(self, task_file: Path, loop_id: str = None) -> dict:
        """
        Run task with autonomous iteration until complete

        Args:
            task_file: Path to task file
            loop_id: Optional loop ID for resuming

        Returns:
            Result dictionary with completion status
        """
        if not task_file.exists():
            return {
                'success': False,
                'error': f'Task file not found: {task_file}',
            }

        # Generate or use existing loop ID
        if not loop_id:
            loop_id = f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize state
        state = self._init_state(task_file, loop_id)

        print(f"[Ralph Wiggum Loop] Starting loop {loop_id} for {task_file.name}")
        print(f"[Ralph Wiggum Loop] Max iterations: {self.max_iterations}")

        # Main iteration loop
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n[Ralph Wiggum Loop] Iteration {iteration}/{self.max_iterations}")

            # Update state
            state['iteration'] = iteration
            state['last_iteration_at'] = datetime.now().isoformat()
            self._save_state(loop_id, state)

            # Check if task is complete
            completion_status = self._check_completion(task_file)

            if completion_status['complete']:
                print(f"[Ralph Wiggum Loop] Task complete! Strategy: {completion_status['strategy']}")
                state['status'] = 'completed'
                state['completed_at'] = datetime.now().isoformat()
                state['completion_strategy'] = completion_status['strategy']
                self._save_state(loop_id, state)

                return {
                    'success': True,
                    'status': 'completed',
                    'iterations': iteration,
                    'strategy': completion_status['strategy'],
                    'message': f'Task completed in {iteration} iterations',
                }

            if completion_status.get('waiting'):
                print(f"[Ralph Wiggum Loop] Task waiting for approval, pausing loop")
                state['status'] = 'waiting_approval'
                self._save_state(loop_id, state)

                return {
                    'success': True,
                    'status': 'waiting_approval',
                    'iterations': iteration,
                    'message': 'Task waiting for human approval',
                }

            # Invoke Claude Code to continue working
            print(f"[Ralph Wiggum Loop] Invoking Claude Code...")
            result = self._invoke_claude(task_file)

            # Add to history
            state['history'].append({
                'iteration': iteration,
                'timestamp': datetime.now().isoformat(),
                'result': result,
            })
            self._save_state(loop_id, state)

            # Check if Claude indicated completion
            if self._check_promise_completion(result):
                print(f"[Ralph Wiggum Loop] Claude indicated task complete")
                state['status'] = 'completed'
                state['completed_at'] = datetime.now().isoformat()
                state['completion_strategy'] = 'promise'
                self._save_state(loop_id, state)

                return {
                    'success': True,
                    'status': 'completed',
                    'iterations': iteration,
                    'strategy': 'promise',
                    'message': f'Task completed in {iteration} iterations',
                }

            # Wait before next iteration
            if iteration < self.max_iterations:
                print(f"[Ralph Wiggum Loop] Waiting 5 seconds before next iteration...")
                time.sleep(5)

        # Max iterations reached
        print(f"[Ralph Wiggum Loop] Max iterations ({self.max_iterations}) reached")
        state['status'] = 'max_iterations_reached'
        state['completed_at'] = datetime.now().isoformat()
        self._save_state(loop_id, state)

        return {
            'success': False,
            'status': 'max_iterations_reached',
            'iterations': self.max_iterations,
            'message': f'Task incomplete after {self.max_iterations} iterations',
        }

    def _check_completion(self, task_file: Path) -> dict:
        """
        Check if task is complete using multiple strategies

        Args:
            task_file: Path to task file

        Returns:
            Dictionary with completion status and strategy
        """
        # Strategy 1: File movement - task moved to Done folder
        done_file = self.done_dir / task_file.name
        if done_file.exists():
            return {
                'complete': True,
                'strategy': 'file_movement',
            }

        # Strategy 2: Pending approval - task waiting for human
        pending_file = self.pending_approval / task_file.name
        if pending_file.exists():
            return {
                'complete': False,
                'waiting': True,
                'strategy': 'pending_approval',
            }

        # Strategy 3: Metadata check - status in frontmatter
        if task_file.exists():
            try:
                content = task_file.read_text()
                if 'status: completed' in content or 'status: done' in content:
                    return {
                        'complete': True,
                        'strategy': 'metadata',
                    }
            except Exception:
                pass

        # Not complete
        return {
            'complete': False,
            'strategy': None,
        }

    def _check_promise_completion(self, claude_output: dict) -> bool:
        """
        Check if Claude indicated completion via promise tag

        Args:
            claude_output: Output from Claude invocation

        Returns:
            True if completion promise found
        """
        output_text = claude_output.get('output', '')
        return '<promise>TASK_COMPLETE</promise>' in output_text

    def _invoke_claude(self, task_file: Path) -> dict:
        """
        Invoke Claude Code to work on task

        Args:
            task_file: Path to task file

        Returns:
            Dictionary with invocation result
        """
        try:
            # Build Claude Code command
            # In production, this would use the actual Claude Code CLI
            # For now, return a placeholder
            cmd = [
                'claude',
                'code',
                '--task', str(task_file),
                '--vault', str(self.vault_path),
            ]

            # Placeholder - in production would actually invoke Claude
            print(f"[Ralph Wiggum Loop] Would invoke: {' '.join(cmd)}")

            return {
                'success': True,
                'output': 'Claude Code invocation placeholder',
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            }

    def _init_state(self, task_file: Path, loop_id: str) -> dict:
        """Initialize loop state"""
        return {
            'loop_id': loop_id,
            'task_file': str(task_file),
            'task_id': task_file.stem,
            'status': 'running',
            'iteration': 0,
            'max_iterations': self.max_iterations,
            'timeout_per_iteration': self.timeout,
            'started_at': datetime.now().isoformat(),
            'last_iteration_at': None,
            'completed_at': None,
            'completion_strategy': None,
            'history': [],
        }

    def _save_state(self, loop_id: str, state: dict):
        """Save loop state to file"""
        state_file = self.state_dir / f'{loop_id}.json'
        state_file.write_text(json.dumps(state, indent=2))

    def _load_state(self, loop_id: str) -> dict:
        """Load loop state from file"""
        state_file = self.state_dir / f'{loop_id}.json'
        if state_file.exists():
            return json.loads(state_file.read_text())
        return None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop - Autonomous Task Iteration')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--task-file', required=True, help='Path to task file')
    parser.add_argument('--max-iterations', type=int, default=10, help='Max iterations')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout per iteration (seconds)')
    parser.add_argument('--loop-id', help='Loop ID for resuming')

    args = parser.parse_args()

    # Create loop and run
    loop = RalphWiggumLoop(args.vault, args.max_iterations, args.timeout)
    result = loop.run_task(Path(args.task_file), args.loop_id)

    # Output result
    print("\n" + "="*60)
    print("RESULT:")
    print(json.dumps(result, indent=2))
    print("="*60)

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
