# Self-Improving Agent Knowledge Base

Last Updated: 2025-01-08

## Agent Behavior Guidelines

### Context Management
- ALWAYS load context.md before starting tasks
- Read multiple files in parallel when possible
- Prune context aggressively (>50% reduction ideal)
- Use extract tool to preserve key findings before pruning

### Validation
- Run lsp_diagnostics before completing any task
- Request review on all complex changes (>3 files)
- Verify with build/test commands when available
- Zero tolerance for type errors in production

### Coordination
- Default to 2 parallel workers (3 causes merge conflicts)
- Wait for worker confirmation before spawning new workers
- Merge results sequentially, not all at once
- Create all worktrees before spawning workers

### Task Management
- Break features into atomic, independently completable units
- Enforce dependencies to prevent blocking
- Track progress with immediate status updates
- Define clear, measurable exit criteria

### Common Pitfalls

**Don't:**
- Skip type checks to "save time"
- Assume patterns work without validation
- Batch-complete todos (mark individually)
- Execute tasks sequentially when parallel is possible
- Start execution before creating all worktrees

**Do:**
- Extract key findings before pruning context
- Verify work after delegation
- Learn from failures, not just successes
- Apply adaptations progressively (session → agent → system)
- Preserve original behavior in comments

## Agent-Specific Learning Rules

### Orchestrator
- Monitor merge conflicts and adjust worker count accordingly
- Track execution time for similar task types
- Capture coordination patterns across multiple phases

### Worker
- Mandatory trace capture before completion
- Learn from reviewer feedback patterns
- Track which approaches lead to successful reviews

### Reviewer
- Track recurring issue types across reviews
- Identify patterns that suggest agent-level improvements
- Generate pattern-aware feedback when issues repeat 3+ times

### Task Manager
- Monitor task breakdown effectiveness
- Learn optimal granularity for different feature types
- Track dependency flow and identify blocking patterns

## Learning Metrics

### Adaptation Success Rate
- Total adaptations applied: 0 (new system)
- Successful improvements: 0
- Neutral/no effect: 0
- Negative (reverted): 0

### Agent Performance
No baseline metrics collected yet. Track improvements after initial deployment.

### Knowledge Base Growth
- Traces collected: 0
- Insights extracted: 0
- Patterns validated: 0

---

**Note:** This knowledge base is automatically maintained by the self-learning skill. Insights are extracted from execution traces and validated across multiple sessions before being promoted to persistent rules.
