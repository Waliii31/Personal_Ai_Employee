#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Persistent Claude execution for multi-step tasks
Implements the Ralph Wiggum pattern for continuous task completion
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess


class RalphWiggumLoop:
    """
    Implements the Ralph Wiggum pattern: a Stop hook that intercepts Claude's exit
    and feeds the prompt back until a task is complete.
    """

    def __init__(self, task_description: str, completion_condition: str = None,
                 max_iterations: int = 10, iteration_delay: int = 5):
        """
        Initialize the Ralph Wiggum loop

        Args:
            task_description: Description of the task to be completed
            completion_condition: String that indicates completion when found in output
            max_iterations: Maximum number of iterations before giving up
            iteration_delay: Delay between iterations in seconds
        """
        self.task_description = task_description
        self.completion_condition = completion_condition
        self.max_iterations = max_iterations
        self.iteration_delay = iteration_delay
        self.iteration_count = 0

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Create state directory
        self.state_dir = Path("./ralph_state")
        self.state_dir.mkdir(exist_ok=True)

    def run_claude_iteration(self, prompt: str) -> str:
        """
        Run a single iteration of Claude with the given prompt

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Claude's response
        """
        # In a real implementation, this would call Claude Code
        # For now, we'll simulate by calling a command that would run Claude
        try:
            # This is a placeholder - in reality, you'd call Claude Code directly
            # or use its API to send the prompt
            result = subprocess.run([
                sys.executable, "-c",
                f"print('Simulated Claude response for: {prompt[:50]}...')"
            ], capture_output=True, text=True)

            return result.stdout
        except Exception as e:
            self.logger.error(f"Error running Claude iteration: {e}")
            return f"Error: {e}"

    def check_completion(self, output: str, task_file_path: Path = None) -> bool:
        """
        Check if the task is complete based on various criteria

        Args:
            output: Claude's output from the iteration
            task_file_path: Path to a task file that should exist when complete

        Returns:
            Boolean indicating if task is complete
        """
        # Check if completion condition is met
        if self.completion_condition and self.completion_condition in output:
            self.logger.info(f"Completion condition '{self.completion_condition}' found in output")
            return True

        # Check if task file exists (advanced completion strategy)
        if task_file_path and task_file_path.exists():
            self.logger.info(f"Task completion file {task_file_path} exists")
            return True

        # Check if output contains promise of completion
        if "<promise>TASK_COMPLETE</promise>" in output:
            self.logger.info("Task completion promise found in output")
            return True

        return False

    def save_state(self):
        """Save the current state of the loop"""
        state_file = self.state_dir / "loop_state.json"
        state_data = {
            "iteration_count": self.iteration_count,
            "task_description": self.task_description,
            "timestamp": datetime.now().isoformat()
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    def load_state(self):
        """Load the previous state of the loop"""
        state_file = self.state_dir / "loop_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                self.iteration_count = state_data.get("iteration_count", 0)
                self.logger.info(f"Loaded previous state: iteration {self.iteration_count}")

    def run(self, task_file_path: Path = None):
        """
        Run the Ralph Wiggum loop until completion or max iterations reached

        Args:
            task_file_path: Path to a file that indicates completion when it exists
        """
        self.logger.info(f"Starting Ralph Wiggum loop for task: {self.task_description}")
        self.logger.info(f"Max iterations: {self.max_iterations}, Delay: {self.iteration_delay}s")

        # Load previous state if available
        self.load_state()

        # Initial prompt
        prompt = f"""
        {self.task_description}

        You are in a continuous loop designed to complete complex multi-step tasks.
        You must continue working until the entire task is complete.
        When you finish a step, immediately proceed to the next required step.
        Only stop when the ENTIRE task is completely finished.

        Current iteration: {self.iteration_count + 1}/{self.max_iterations}
        """

        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            self.save_state()

            self.logger.info(f"Iteration {self.iteration_count}/{self.max_iterations}")

            # Run Claude iteration
            output = self.run_claude_iteration(prompt)
            self.logger.debug(f"Output: {output[:200]}...")

            # Check for completion
            if self.check_completion(output, task_file_path):
                self.logger.info(f"Task completed successfully after {self.iteration_count} iterations!")
                return True

            # Prepare next iteration prompt
            prompt = f"""
            Continue working on the task: {self.task_description}

            Previous output: {output}

            Continue working on the task. If you completed part of it, continue with the next part.
            If you encountered an issue, try a different approach.
            You are in a continuous loop and must keep working until the entire task is complete.

            Current iteration: {self.iteration_count}/{self.max_iterations}
            Remaining iterations: {self.max_iterations - self.iteration_count}
            """

            # Wait before next iteration
            if self.iteration_count < self.max_iterations:
                time.sleep(self.iteration_delay)

        self.logger.warning(f"Max iterations ({self.max_iterations}) reached. Task may be incomplete.")
        return False


def main():
    """Command-line interface for the Ralph Wiggum loop"""
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop - Continuous Claude Execution')
    parser.add_argument('task', help='Description of the task to complete')
    parser.add_argument('--condition', '-c', help='String that indicates completion')
    parser.add_argument('--max-iterations', '-m', type=int, default=10,
                       help='Maximum number of iterations (default: 10)')
    parser.add_argument('--delay', '-d', type=int, default=5,
                       help='Delay between iterations in seconds (default: 5)')
    parser.add_argument('--task-file', '-f', type=Path,
                       help='Path to a file that indicates completion when it exists')

    args = parser.parse_args()

    # Create and run the loop
    ralph_loop = RalphWiggumLoop(
        task_description=args.task,
        completion_condition=args.condition,
        max_iterations=args.max_iterations,
        iteration_delay=args.delay
    )

    success = ralph_loop.run(task_file_path=args.task_file)

    if success:
        print("\n✅ Task completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Task did not complete within {args.max_iterations} iterations.")
        sys.exit(1)


if __name__ == "__main__":
    main()