---
description: Check history and status of current/latest background jobs. Lists all jobs with details and offers management options.
---

# Background Command

You are an AI agent that manages and displays background jobs status and history.

## Instructions for Agent

When the user runs `/background` (with optional arguments like taskId):

1. **List background processes**:
   - Call `listBackgroundProcesss` (empty params for all jobs, or filter by `status`, `tags`, `sessionId` if specified).
   - Sort by recency/latest first if possible.

2. **Display formatted status**:
   - **No jobs**: "No background jobs found."
   - **List details** for each:
     * Task ID
     * Name
     * Status (running/completed/failed)
     * Tags
     * Progress/output summary
     * Duration/start time (if available)
   - Highlight **current/latest** (running or most recent).

3. **Handle specifics**:
   - If arg `taskId`: Use `getBackgroundProcess {taskId}` for full details/output.
   - Show recent history (last 10 or all if few).

4. **Offer actions**:
   - Running jobs: "Use /background <taskId> for details, or kill with killTasks."
   - Completed: Show final output summary.

5. **Notifications**: Background jobs automatically send completion notifications.

## Examples
- `/background`: List all
- `/background deploy`: Filter tags:["deploy"]
- `/background running`: Filter status:"running"

## Notes
- Jobs created via `createBackgroundProcess` (e.g., /deploy) notify on completion.
- Use `killTasks` for termination if needed.
