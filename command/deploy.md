---
description: Deploy the project using Kamal if configured. Runs asynchronously in background.
---

# Deploy Command

You are an AI agent that deploys Kamal-based projects asynchronously. Always check for Kamal config first.

## Instructions for Agent

When the user runs `/deploy`:

1. **Check for Kamal**:
   - Run `bash` tool: `test -f config/deploy.yml &amp;&amp; echo &quot;Kamal project&quot; || echo &quot;Not a Kamal project&quot;`
   - Or check for `.kamal/` directory or `grep -q kamal Gemfile`
   - If not a Kamal project: Reply &quot;This is not a Kamal-based project.&quot; and stop.

2. **Pre-deploy checks** (optional, skip if no issues):
   - Run `git status` to ensure clean state or staged changes committed.
   - If issues, inform user but proceed unless critical.

3. **Start async deploy**:
   - Use `createBackgroundProcess` with:
     - command: `kamal deploy`
     - name: &quot;Kamal Deploy&quot;
     - tags: [&quot;deploy&quot;, &quot;kamal&quot;]
   - Reply: &quot;🚀 Kamal deploy started in background (task ID: &lt;taskId&gt;). You will be notified when it completes.&quot;

4. **Monitor completion** (if possible):
   - Opencode will handle notifications. No further action needed.

## Notes
- Do not run synchronously to avoid timeouts.
- Kamal deploy can take several minutes.
- Ensure `kamal` is installed and configured.