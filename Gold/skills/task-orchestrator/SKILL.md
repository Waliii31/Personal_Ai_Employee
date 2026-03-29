# Task Orchestrator Skill

Agent skill for managing Ralph Wiggum loop execution and multi-step task coordination.

## Purpose

Manages autonomous task completion including:
- Starting Ralph Wiggum loop for complex tasks
- Tracking task state across iterations
- Detecting task completion
- Managing iteration limits
- Emergency stop mechanisms

## Usage

### Command Line

```bash
python task_orchestrator.py --vault /path/to/vault --task-file /path/to/task.md --action start
```

### From Claude Code

Automatically invoked when processing complex multi-step tasks.

## Actions

### start_loop

Start Ralph Wiggum loop for a task.

**Required fields:**
- `task_file`: Path to task file
- `max_iterations`: Maximum iterations (default: 10)
- `timeout_per_iteration`: Timeout in seconds (default: 300)

**Returns:** Loop state file path

### check_completion

Check if task is complete.

**Completion detection strategies:**
1. **File movement**: Task file moved to `/Done` folder
2. **Promise tag**: Claude outputs `<promise>TASK_COMPLETE</promise>`
3. **Metadata flag**: Task metadata contains `status: completed`

### stop_loop

Stop a running loop (emergency stop).

### get_loop_state

Get current state of a running loop.

## Loop State Management

State is persisted in `vault/Logs/loop_state/` as JSON:

```json
{
  "task_file": "/path/to/task.md",
  "task_id": "task_123",
  "status": "running",
  "iteration": 3,
  "max_iterations": 10,
  "started_at": "2026-03-14T10:00:00",
  "last_iteration_at": "2026-03-14T10:15:00",
  "completion_strategy": "file_movement",
  "history": [
    {
      "iteration": 1,
      "started_at": "2026-03-14T10:00:00",
      "completed_at": "2026-03-14T10:05:00",
      "status": "incomplete"
    }
  ]
}
```

## Completion Detection

### File Movement Strategy

Monitors task file location:
- Task in `/Needs_Action` = incomplete
- Task in `/Done` = complete
- Task in `/Pending_Approval` = waiting for approval

### Promise Strategy

Parses Claude's output for completion promise:
```
<promise>TASK_COMPLETE</promise>
```

### Metadata Strategy

Checks task file frontmatter for:
```yaml
status: completed
```

## Safety Limits

- **Max iterations**: Default 10, configurable
- **Timeout per iteration**: Default 5 minutes
- **Emergency stop**: Manual stop via stop_loop action
- **Stale detection**: Auto-stop if no progress in 30 minutes

## Integration

### With Ralph Wiggum Loop

The orchestrator manages loop state, while ralph_wiggum_loop.py handles the actual iteration logic.

### With Vault

- Reads tasks from `Needs_Action/`
- Monitors task file location
- Stores state in `Logs/loop_state/`

## Output Format

```json
{
  "success": true,
  "action": "start_loop",
  "loop_id": "loop_123",
  "state_file": "/path/to/state.json",
  "message": "Loop started for task_123"
}
```

## Dependencies

- Python 3.8+
- Access to vault filesystem
- Ralph Wiggum loop engine
