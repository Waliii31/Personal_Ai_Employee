"""
Task Orchestrator Agent Skill
Manages Ralph Wiggum loop execution for autonomous task completion
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime


class TaskOrchestrator:
    """Agent skill for managing autonomous task loops"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.loop_state_dir = self.vault_path / 'Logs' / 'loop_state'
        self.loop_state_dir.mkdir(parents=True, exist_ok=True)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done_dir = self.vault_path / 'Done'

    def start_loop(self, task_file: str, max_iterations: int = 10, timeout: int = 300) -> dict:
        """
        Start Ralph Wiggum loop for a task

        Args:
            task_file: Path to task file
            max_iterations: Maximum iterations
            timeout: Timeout per iteration in seconds

        Returns:
            Result with loop state
        """
        task_path = Path(task_file)

        if not task_path.exists():
            return {
                'success': False,
                'error': f'Task file not found: {task_file}',
            }

        # Generate loop ID
        loop_id = f"loop_{uuid.uuid4().hex[:8]}"
        task_id = task_path.stem

        # Create loop state
        state = {
            'loop_id': loop_id,
            'task_file': str(task_path),
            'task_id': task_id,
            'status': 'running',
            'iteration': 0,
            'max_iterations': max_iterations,
            'timeout_per_iteration': timeout,
            'started_at': datetime.now().isoformat(),
            'last_iteration_at': None,
            'completion_strategy': 'file_movement',
            'history': [],
        }

        # Save state
        state_file = self._save_state(loop_id, state)

        return {
            'success': True,
            'action': 'start_loop',
            'loop_id': loop_id,
            'task_id': task_id,
            'state_file': str(state_file),
            'message': f'Loop started for {task_id}',
        }

    def check_completion(self, loop_id: str) -> dict:
        """
        Check if task is complete

        Args:
            loop_id: Loop identifier

        Returns:
            Completion status
        """
        state = self._load_state(loop_id)

        if not state:
            return {
                'success': False,
                'error': f'Loop state not found: {loop_id}',
            }

        task_path = Path(state['task_file'])

        # Strategy 1: File movement
        if self._check_file_movement(task_path):
            return {
                'success': True,
                'complete': True,
                'strategy': 'file_movement',
                'message': 'Task file moved to Done folder',
            }

        # Strategy 2: Check if in Pending_Approval (waiting state)
        if self._check_pending_approval(task_path):
            return {
                'success': True,
                'complete': False,
                'waiting': True,
                'strategy': 'pending_approval',
                'message': 'Task waiting for approval',
            }

        # Strategy 3: Check metadata
        if self._check_metadata_completion(task_path):
            return {
                'success': True,
                'complete': True,
                'strategy': 'metadata',
                'message': 'Task marked as completed in metadata',
            }

        # Not complete
        return {
            'success': True,
            'complete': False,
            'message': 'Task not yet complete',
        }

    def stop_loop(self, loop_id: str, reason: str = 'manual_stop') -> dict:
        """
        Stop a running loop

        Args:
            loop_id: Loop identifier
            reason: Reason for stopping

        Returns:
            Stop status
        """
        state = self._load_state(loop_id)

        if not state:
            return {
                'success': False,
                'error': f'Loop state not found: {loop_id}',
            }

        # Update state
        state['status'] = 'stopped'
        state['stopped_at'] = datetime.now().isoformat()
        state['stop_reason'] = reason

        self._save_state(loop_id, state)

        return {
            'success': True,
            'action': 'stop_loop',
            'loop_id': loop_id,
            'reason': reason,
            'message': f'Loop {loop_id} stopped',
        }

    def get_loop_state(self, loop_id: str) -> dict:
        """
        Get current loop state

        Args:
            loop_id: Loop identifier

        Returns:
            Loop state
        """
        state = self._load_state(loop_id)

        if not state:
            return {
                'success': False,
                'error': f'Loop state not found: {loop_id}',
            }

        return {
            'success': True,
            'state': state,
        }

    def update_iteration(self, loop_id: str) -> dict:
        """
        Update iteration count and history

        Args:
            loop_id: Loop identifier

        Returns:
            Updated state
        """
        state = self._load_state(loop_id)

        if not state:
            return {
                'success': False,
                'error': f'Loop state not found: {loop_id}',
            }

        # Increment iteration
        state['iteration'] += 1
        state['last_iteration_at'] = datetime.now().isoformat()

        # Add to history
        state['history'].append({
            'iteration': state['iteration'],
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress',
        })

        # Check if max iterations reached
        if state['iteration'] >= state['max_iterations']:
            state['status'] = 'max_iterations_reached'

        self._save_state(loop_id, state)

        return {
            'success': True,
            'iteration': state['iteration'],
            'max_iterations': state['max_iterations'],
            'status': state['status'],
        }

    def _check_file_movement(self, task_path: Path) -> bool:
        """Check if task file moved to Done folder"""
        # Check if file exists in Done folder
        done_file = self.done_dir / task_path.name
        return done_file.exists()

    def _check_pending_approval(self, task_path: Path) -> bool:
        """Check if task is in Pending_Approval folder"""
        pending_approval = self.vault_path / 'Pending_Approval'
        pending_file = pending_approval / task_path.name
        return pending_file.exists()

    def _check_metadata_completion(self, task_path: Path) -> bool:
        """Check if task metadata indicates completion"""
        if not task_path.exists():
            return False

        try:
            content = task_path.read_text()
            # Simple check for status: completed in frontmatter
            return 'status: completed' in content or 'status: done' in content
        except Exception:
            return False

    def _save_state(self, loop_id: str, state: dict) -> Path:
        """Save loop state to file"""
        state_file = self.loop_state_dir / f'{loop_id}.json'
        state_file.write_text(json.dumps(state, indent=2))
        return state_file

    def _load_state(self, loop_id: str) -> dict:
        """Load loop state from file"""
        state_file = self.loop_state_dir / f'{loop_id}.json'

        if not state_file.exists():
            return None

        try:
            return json.loads(state_file.read_text())
        except Exception:
            return None


def main():
    """Main entry point for the skill"""
    import argparse

    parser = argparse.ArgumentParser(description='Task Orchestrator Skill')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--action', required=True, choices=['start', 'check', 'stop', 'state'])
    parser.add_argument('--task-file', help='Path to task file (for start action)')
    parser.add_argument('--loop-id', help='Loop ID (for check/stop/state actions)')
    parser.add_argument('--max-iterations', type=int, default=10, help='Max iterations')

    args = parser.parse_args()

    orchestrator = TaskOrchestrator(args.vault)

    if args.action == 'start':
        if not args.task_file:
            print(json.dumps({'success': False, 'error': 'task-file required for start action'}))
            sys.exit(1)
        result = orchestrator.start_loop(args.task_file, args.max_iterations)

    elif args.action == 'check':
        if not args.loop_id:
            print(json.dumps({'success': False, 'error': 'loop-id required for check action'}))
            sys.exit(1)
        result = orchestrator.check_completion(args.loop_id)

    elif args.action == 'stop':
        if not args.loop_id:
            print(json.dumps({'success': False, 'error': 'loop-id required for stop action'}))
            sys.exit(1)
        result = orchestrator.stop_loop(args.loop_id)

    elif args.action == 'state':
        if not args.loop_id:
            print(json.dumps({'success': False, 'error': 'loop-id required for state action'}))
            sys.exit(1)
        result = orchestrator.get_loop_state(args.loop_id)

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
