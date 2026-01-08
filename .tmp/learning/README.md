# Self-Improving Agent System

A self-learning capability for agents that transforms execution traces into actionable insights, enabling continuous improvement without human intervention.

## Overview

This system enables agents to learn from their execution history by capturing traces, extracting patterns, and adapting behavior. Based on the pskoett self-improving agent pattern, it implements the core learning loop:

**Trace Collection → Pattern Analysis → Insight Extraction → Behavior Adaptation → Performance Improvement**

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Self-Learning Skill                       │
├─────────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Trace        │───→│ Analysis     │───→│ Insight      │  │
│  │ Collection   │    │ & Patterns   │    │ Extraction   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │               │
│         │                   ▼                   ▼               │
│         │            ┌──────────────┐    ┌──────────────┐    │
│         │            │ Knowledge    │───→│ Adaptation   │    │
│         │            │ Base         │    │ Engine       │    │
│         │            └──────────────┘    └──────────────┘    │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │           Agent Behavior Optimization               │      │
│  │  (Session-Local → Agent-Specific → System-Wide)   │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │  Integrated Agents         │
              │  • Orchestrator          │
              │  • Worker                │
              │  • Reviewer              │
              │  • Task Manager          │
              └─────────────────────────────┘
```

## Components

### 1. Core Skill (`skills/self-learning/`)

**SKILL.md** - Comprehensive guide covering:
- When to use the skill
- Core capabilities (trace collection, insight extraction, adaptation)
- Integration examples for each agent
- Safety guidelines
- Usage examples

**Scripts:**
- `analyze_traces.py` - Analyze collected traces to extract patterns
- `apply_adaptation.py` - Apply adaptations at different levels (session/agent/system)

### 2. Learning Storage (`.tmp/learning/`)

```
learning/
├── traces/           # Raw execution traces from agents
├── insights/         # Extracted insights by category
├── adaptations/      # Applied adaptations by level
├── patterns/         # Recurring patterns detected by agents
├── knowledge-base.md  # Consolidated actionable knowledge
└── test_suite.md    # Test scenarios for learning mechanism
```

### 3. Integrated Agents

**Agents with Learning Hooks:**
- **Orchestrator** - Post-merge learning, coordination patterns
- **Worker** - Pre-completion trace capture, execution insights
- **Reviewer** - Pattern detection, recurring issue tracking
- **Task Manager** - Decomposition insights, planning patterns

## Usage Patterns

### Pattern 1: Automatic Learning in Swarm Workflows

When running a swarm, learning happens automatically:

```bash
# User triggers swarm
/swarm

# Orchestrator:
# 1. Spawns workers (2 by default, based on learned patterns)
# 2. Workers capture traces after completion
# 3. Reviewer detects patterns
# 4. Orchestrator captures coordination trace
# 5. Task manager captures decomposition insights
# 6. Learning system extracts insights automatically
```

**Result:** System improves for next swarm without manual intervention.

---

### Pattern 2: Manual Trace Analysis

After collecting 5+ traces, analyze them:

```bash
python skills/self-learning/scripts/analyze_traces.py \
  --traces .tmp/learning/traces/ \
  --output .tmp/learning/insights
```

**Output:** Insights categorized by success/failure patterns with impact scores.

---

### Pattern 3: Applying Adaptations

#### Session-Local (Low Risk)

```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent orchestrator \
  --adaptation "Default to 2 workers for <5 subtasks" \
  --level session
```

**Effect:** Applies only to current session. No persistent changes.

---

#### Agent-Specific (Medium Risk)

After 3+ successful validations:

```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent worker \
  --adaptation "Always run lsp_diagnostics before completion" \
  --level agent \
  --agent-file agent/worker.md
```

**Effect:** Updates agent.md with new rule. Persists across sessions.

---

#### System-Wide (High Risk, Manual Approval)

After extensive validation (10+ sessions):

```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent orchestrator \
  --adaptation "Always use 2 workers regardless of task count" \
  --level system
```

**Effect:** Documents in `.tmp/learning/adaptations/system_pending.md`
**Next Step:** Manual review, then update all relevant agents.

---

## Safety Guidelines

### Critical Constraints

1. **Never Adapt Without Evidence**
   - Require minimum 5 traces before extracting patterns
   - Validate insights across 3+ sessions
   - Seek confirmation before major changes

2. **Start Local, Scale Slowly**
   ```
   Session-Local (1 session) 
   → Agent-Specific (3+ validations) 
   → System-Wide (10+ validations)
   ```

3. **Preserve Original Behavior**
   - Document all changes with rationale
   - Keep comments showing original patterns
   - Enable rollback if adaptation causes issues

4. **Don't Override User Intent**
   - Learning optimizes, doesn't override
   - Adaptations respect explicit instructions
   - Conflicts: User instructions > learned patterns

5. **Monitor for Negative Feedback**
   - Track adaptation effectiveness
   - Revert if success rate decreases
   - Learn from adaptation failures

### Risk Levels

| Adaptation Type | Risk | Evidence Required | Approval |
|----------------|------|------------------|-----------|
| Session-Local   | Low  | 1 session        | Automatic |
| Agent-Specific  | Medium| 3 validations   | Auto (after validation) |
| System-Wide     | High  | 10 validations  | Manual |

---

## Integration Examples

### Example 1: Orchestrator Learns Optimal Worker Count

**Initial State:**
```markdown
# orchestrator.md
# Spawns up to 3 parallel workers
```

**After 5 Swarms with Merge Conflicts:**

1. Traces captured: `orchestrator_swarm_*.md`
2. Pattern detected: 3 workers → 5+ merge conflicts
3. Insight extracted: "Reduce to 2 workers"

**Session-Local Adaptation:**
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent orchestrator \
  --adaptation "Default to 2 workers for <5 subtasks" \
  --level session
```

**Result:** Next swarm uses 2 workers, conflicts reduced to 1.

**After 3+ Successful Validations:**

```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent orchestrator \
  --adaptation "Default to 2 workers for <5 subtasks" \
  --level agent \
  --agent-file agent/orchestrator.md
```

**Result:** Orchestrator.md permanently updated.

---

### Example 2: Worker Learns Validation Importance

**Initial State:**
```markdown
# worker.md
# Workflow: implement → review → complete
```

**After 3 Tasks with Type Errors:**

1. Reviewer detects pattern: "Missing lsp_diagnostics leads to type errors"
2. Pattern documented in: `.tmp/learning/patterns/reviewer_type_safety.md`
3. Adaptation suggested.

**Agent-Specific Adaptation:**
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent worker \
  --adaptation "Always run lsp_diagnostics before calling swarm_worker_complete" \
  --level agent \
  --agent-file agent/worker.md
```

**Result:** Worker.md updated with new step in workflow.

---

### Example 3: Reviewer Detects Recurring Issues

**Pattern Detection:**
```markdown
# reviewer pattern tracking
- Issue 1: "Missing type annotation" (task-1)
- Issue 2: "Missing type annotation" (task-2)
- Issue 3: "Missing type annotation" (task-3)
```

**Action:**
1. Reviewer detects 3rd occurrence
2. Documents pattern in: `.tmp/learning/patterns/reviewer_type_safety.md`
3. Suggests agent adaptation
4. Includes pattern-aware feedback:
   > "Note: This is the 4th occurrence of missing type annotations. Recommend adding validation to worker workflow."

**Outcome:** System suggests worker improvement before next task.

---

## Best Practices

### For Users

1. **Enable Learning Early**
   - Let agents collect traces from day 1
   - More traces = better patterns

2. **Review Insights Regularly**
   - Check `.tmp/learning/insights/` weekly
   - Validate high-impact insights manually

3. **Monitor Adaptations**
   - Review `.tmp/learning/adaptations/` for new changes
   - Verify adaptations don't break workflows

4. **Provide Feedback**
   - If an adaptation causes issues, report it
   - Rollback immediately if success rate decreases

### For Agents

1. **Capture Traces Consistently**
   - Every task completion → trace capture
   - Include failures and successes
   - Be specific about tools and approaches

2. **Detect Patterns Proactively**
   - Look for 3+ occurrences of same issue
   - Document patterns before adapting
   - Prioritize high-impact insights

3. **Adapt Progressively**
   - Start with session-local adaptations
   - Promote only after validation
   - Document all changes with rationale

---

## Testing

Run the test suite to verify learning mechanism:

```bash
# Review test scenarios
cat .tmp/learning/test_suite.md

# Execute tests manually or via automated workflow
# Test 1: Worker Trace Capture
# Test 2: Reviewer Pattern Detection
# Test 3: Orchestrator Worker Count Optimization
# Test 4: Trace Analysis
# Test 5: Adaptation Application
# Test 6: Knowledge Base Update
```

---

## Metrics Tracking

Track learning effectiveness over time:

```markdown
# .tmp/learning/knowledge-base.md

## Adaptation Success Rate
- Total adaptations applied: {count}
- Successful improvements: {count} ({percentage}%)
- Neutral/no effect: {count} ({percentage}%)
- Negative (reverted): {count} ({percentage}%)

## Agent Performance (Before/After)
- Orchestrator: {time} → {time} ({percentage}% improvement)
- Worker: {failures} → {failures} ({percentage}% reduction)
- Reviewer: {issues} → {issues} ({percentage}% reduction)

## Knowledge Base Growth
- Traces collected: {count}
- Insights extracted: {count}
- Patterns validated: {count}
```

---

## Troubleshooting

### Problem: No traces being captured

**Solution:**
- Verify agents have learning hooks integrated
- Check `.tmp/learning/traces/` directory exists
- Ensure agents are calling trace capture before completion

### Problem: Insights seem inaccurate

**Solution:**
- Collect more traces (minimum 5 for meaningful patterns)
- Verify trace quality (specificity, completeness)
- Manually review insights before applying adaptations

### Problem: Adaptations causing issues

**Solution:**
- Revert adaptation immediately
- Check `.tmp/learning/adaptations/` for the change
- Review original behavior in agent files
- Report issue for future learning

---

## Future Enhancements

**Planned Features:**
1. **Automated Insight Validation** - Automatically test insights before applying
2. **Cross-Agent Pattern Sharing** - Share learnings between agent types
3. **Performance Baseline Tracking** - Automatic before/after metrics
4. **Adaptation Rollback** - One-click revert of problematic adaptations
5. **Learning Dashboard** - Visual overview of learning progress

---

## Contributing

To add learning capabilities to new agents:

1. **Add Trace Capture Hook** - Capture execution before completion
2. **Add Pattern Detection** - Watch for recurring issues/successes
3. **Document Integration** - Add example in SKILL.md
4. **Test Thoroughly** - Verify with test_suite.md
5. **Update Knowledge Base** - Add agent-specific guidelines

---

## License

Part of OhMyOpenCode. Follows project license.

---

**Key Principle:** This system transforms execution history into actionable knowledge, enabling agents to systematically improve without human intervention. Start small, validate thoroughly, scale cautiously.
