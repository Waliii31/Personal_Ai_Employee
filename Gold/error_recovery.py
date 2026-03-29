"""
Error Recovery Module
Provides retry logic, error categorization, and graceful degradation
"""

import time
import logging
import functools
from typing import Callable, Any
from datetime import datetime
from pathlib import Path
import json


class ErrorCategory:
    """Error categories for different recovery strategies"""
    TRANSIENT = 'transient'  # Network timeouts, temporary unavailability
    AUTH = 'auth'  # Authentication/authorization failures
    LOGIC = 'logic'  # Business logic errors
    DATA = 'data'  # Data validation errors
    SYSTEM = 'system'  # System-level errors


class ErrorRecovery:
    """Error recovery and retry logic"""

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        self.logger = self._setup_logger()
        self.operation_queue = []

        if self.vault_path:
            self.error_log_dir = self.vault_path / 'Logs' / 'errors'
            self.error_log_dir.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self) -> logging.Logger:
        """Setup error recovery logger"""
        logger = logging.getLogger('ErrorRecovery')
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def categorize_error(self, error: Exception) -> str:
        """
        Categorize error for appropriate recovery strategy

        Args:
            error: Exception to categorize

        Returns:
            Error category
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Transient errors - retry with backoff
        if any(keyword in error_str for keyword in [
            'timeout', 'connection', 'network', 'temporary', 'unavailable',
            'rate limit', '429', '503', '504'
        ]):
            return ErrorCategory.TRANSIENT

        # Authentication errors - alert human
        if any(keyword in error_str for keyword in [
            'auth', 'unauthorized', '401', '403', 'permission', 'credential',
            'token', 'api key'
        ]):
            return ErrorCategory.AUTH

        # Data validation errors - quarantine
        if any(keyword in error_str for keyword in [
            'validation', 'invalid', 'malformed', 'parse', 'format'
        ]) or error_type in ['ValueError', 'TypeError', 'KeyError']:
            return ErrorCategory.DATA

        # System errors - watchdog restart
        if any(keyword in error_str for keyword in [
            'memory', 'disk', 'resource', 'system'
        ]) or error_type in ['MemoryError', 'OSError']:
            return ErrorCategory.SYSTEM

        # Default to logic error
        return ErrorCategory.LOGIC

    def retry_with_backoff(
        self,
        func: Callable,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        *args,
        **kwargs
    ) -> Any:
        """
        Retry function with exponential backoff

        Args:
            func: Function to retry
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Backoff multiplier
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.info(f'Attempt {attempt}/{max_attempts} for {func.__name__}')
                result = func(*args, **kwargs)
                if attempt > 1:
                    self.logger.info(f'Success on attempt {attempt}')
                return result

            except Exception as e:
                last_exception = e
                category = self.categorize_error(e)

                self.logger.warning(
                    f'Attempt {attempt} failed: {e} (category: {category})'
                )

                # Log error
                self._log_error(func.__name__, e, category, attempt)

                # Don't retry non-transient errors
                if category != ErrorCategory.TRANSIENT:
                    self.logger.error(f'Non-transient error, not retrying: {category}')
                    raise

                # Wait before retry (except on last attempt)
                if attempt < max_attempts:
                    self.logger.info(f'Waiting {delay:.1f}s before retry...')
                    time.sleep(delay)
                    delay *= backoff_factor

        # All retries failed
        self.logger.error(f'All {max_attempts} attempts failed for {func.__name__}')
        raise last_exception

    def with_recovery(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """
        Decorator for automatic retry with backoff

        Usage:
            @error_recovery.with_recovery(max_attempts=3)
            def my_function():
                # function code
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.retry_with_backoff(
                    func,
                    max_attempts,
                    initial_delay,
                    backoff_factor,
                    *args,
                    **kwargs
                )
            return wrapper
        return decorator

    def handle_error(self, error: Exception, operation: str, context: dict = None) -> dict:
        """
        Handle error with appropriate recovery strategy

        Args:
            error: Exception that occurred
            operation: Operation that failed
            context: Additional context

        Returns:
            Recovery action dictionary
        """
        category = self.categorize_error(error)
        self._log_error(operation, error, category, context=context)

        if category == ErrorCategory.TRANSIENT:
            return {
                'action': 'retry',
                'strategy': 'exponential_backoff',
                'max_attempts': 3,
                'message': 'Transient error, will retry',
            }

        elif category == ErrorCategory.AUTH:
            return {
                'action': 'alert_human',
                'strategy': 'pause_operations',
                'message': 'Authentication error, human intervention required',
            }

        elif category == ErrorCategory.LOGIC:
            return {
                'action': 'move_to_review',
                'strategy': 'human_review_queue',
                'message': 'Logic error, moving to human review',
            }

        elif category == ErrorCategory.DATA:
            return {
                'action': 'quarantine',
                'strategy': 'data_quarantine',
                'message': 'Data validation error, quarantining data',
            }

        elif category == ErrorCategory.SYSTEM:
            return {
                'action': 'restart',
                'strategy': 'watchdog_restart',
                'message': 'System error, triggering restart',
            }

        return {
            'action': 'unknown',
            'strategy': 'manual_intervention',
            'message': 'Unknown error category',
        }

    def queue_operation(self, operation: dict):
        """
        Queue operation for retry when service is available

        Args:
            operation: Operation details
        """
        operation['queued_at'] = datetime.now().isoformat()
        self.operation_queue.append(operation)
        self.logger.info(f'Queued operation: {operation.get("name")}')

    def process_queue(self):
        """Process queued operations"""
        if not self.operation_queue:
            return

        self.logger.info(f'Processing {len(self.operation_queue)} queued operations')

        processed = []
        for operation in self.operation_queue:
            try:
                # Attempt to execute queued operation
                self.logger.info(f'Executing queued operation: {operation.get("name")}')
                # In production, would actually execute the operation
                processed.append(operation)
            except Exception as e:
                self.logger.error(f'Queued operation failed: {e}')

        # Remove processed operations
        for op in processed:
            self.operation_queue.remove(op)

    def _log_error(
        self,
        operation: str,
        error: Exception,
        category: str,
        attempt: int = None,
        context: dict = None
    ):
        """Log error to file"""
        if not self.vault_path:
            return

        error_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category,
            'attempt': attempt,
            'context': context or {},
        }

        # Log to daily error file
        date_str = datetime.now().strftime('%Y-%m-%d')
        error_file = self.error_log_dir / f'errors_{date_str}.json'

        # Append to file
        errors = []
        if error_file.exists():
            try:
                errors = json.loads(error_file.read_text())
            except Exception:
                pass

        errors.append(error_data)
        error_file.write_text(json.dumps(errors, indent=2))


# Global error recovery instance
_error_recovery = None


def get_error_recovery(vault_path: str = None) -> ErrorRecovery:
    """Get global error recovery instance"""
    global _error_recovery
    if _error_recovery is None:
        _error_recovery = ErrorRecovery(vault_path)
    return _error_recovery


# Convenience decorator
def with_retry(max_attempts: int = 3, initial_delay: float = 1.0):
    """
    Convenience decorator for retry logic

    Usage:
        @with_retry(max_attempts=3)
        def my_function():
            # function code
    """
    recovery = get_error_recovery()
    return recovery.with_recovery(max_attempts, initial_delay)
