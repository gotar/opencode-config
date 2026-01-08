# Self-Improving Agent Test Suite

## Test 1: Worker Trace Capture

**Scenario:** Worker completes a task after reviewer approval

**Steps:**
1. Worker implements a task (e.g., add authentication feature)
2. Worker requests review
3. Reviewer approves
4. Worker captures trace before completing

**Expected Trace:**
```markdown
# Trace: worker_20250108_1120
Agent: worker
Task: task-1 - Add JWT authentication
Status: Success

## Approach
1. Analyzed existing auth patterns in codebase
2. Implemented JWT token validation
3. Added tests for edge cases

## Tools Invoked
- Read: agent/openagent.md, code/auth.ts, tests/auth.test.ts
- Write: code/auth.ts
- lsp_diagnostics: code/auth.ts

## Results
- Auth implemented successfully
- All tests passing
- Zero diagnostics errors

## Failures/Issues
- Initial JWT secret configuration missing
- Fixed by reading config patterns from code/config.ts
- Reviewer requested 1 change: add rate limiting
```

**Verify:** Trace saved to `.tmp/learning/traces/worker_*.md`

---

## Test 2: Reviewer Pattern Detection

**Scenario:** Reviewer encounters same issue 3 times

**Steps:**
1. Worker submits code with missing type annotation
2. Reviewer flags missing type annotation (review 1)
3. Another worker submits similar code
4. Reviewer flags missing type annotation again (review 2)
5. Third worker submits similar code
6. Reviewer flags missing type annotation (review 3)

**Expected Pattern Detection:**
- Reviewer detects recurring pattern
- Documents in: `.tmp/learning/patterns/reviewer_type_safety.md`
- Suggests adaptation:
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent worker \
  --adaptation "Always add type annotations before requesting review" \
  --level session
```

**Verify:** Pattern documented, adaptation suggested

---

## Test 3: Orchestrator Worker Count Optimization

**Scenario:** Orchestrator experiences merge conflicts with 3 workers

**Steps:**
1. Orchestrator spawns 3 workers
2. Workers complete tasks with overlapping file changes
3. Orchestrator encounters 5+ merge conflicts
4. Orchestrator resolves conflicts and completes

**Expected Trace:**
```markdown
# Trace: orchestrator_swarm_20250108_1120
Agent: orchestrator
Task: Multi-feature implementation
Workers: 3
Merge Conflicts: 5 (high)
Total Time: 45min
Status: Success (with issues)
```

**Expected Insight:**
```markdown
## Insight: Worker Count Optimization
**Finding**: 3 workers cause 5 merge conflicts
**Evidence**: Compared to previous 2-worker tasks (0-1 conflicts)
**Action**: Reduce to 2 workers for similar tasks
**Impact**: High (prevents merge conflicts, faster completion)
```

**Expected Adaptation:**
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent orchestrator \
  --adaptation "Default to 2 workers instead of 3 for tasks with <5 subtasks" \
  --level session
```

**Verify:** Insight extracted, adaptation applied

---

## Test 4: Trace Analysis

**Scenario:** Multiple traces collected, analyze for patterns

**Steps:**
1. Collect 5+ worker traces
2. Run trace analysis script:
```bash
python skills/self-learning/scripts/analyze_traces.py \
  --traces .tmp/learning/traces/ \
  --output .tmp/learning/insights
```

**Expected Output:**
- Insights generated in `.tmp/learning/insights/`
- Success patterns identified (e.g., "lsp_diagnostics appears in 5/5 successful traces")
- Failure patterns identified (e.g., "Missing validation appears in 3/5 failed traces")
- Prioritized by impact

**Verify:** Insights file created, patterns identified

---

## Test 5: Adaptation Application

**Scenario:** Apply adaptation at different levels

**Session-Local Adaptation:**
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent worker \
  --adaptation "Always run lsp_diagnostics before completion" \
  --level session
```

**Expected:** File created in `.tmp/learning/adaptations/session_*.md`

**Agent-Specific Adaptation:**
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent worker \
  --adaptation "Always run lsp_diagnostics before completion" \
  --level agent \
  --agent-file agent/worker.md
```

**Expected:** Worker.md updated with new rule under "## Learning Rule"

**System-Wide Adaptation:**
```bash
python skills/self-learning/scripts/apply_adaptation.py \
  --agent orchestrator \
  --adaptation "Default to 2 workers for all tasks" \
  --level system
```

**Expected:** Adaptation documented in `.tmp/learning/adaptations/system_pending.md`

**Verify:** Correct file created/updated at each level

---

## Test 6: Knowledge Base Update

**Scenario:** Multiple validated insights accumulated

**Steps:**
1. Run 3+ successful swarms with learning enabled
2. Collect traces and extract insights
3. Validate patterns across sessions
4. Update knowledge-base.md with consolidated insights

**Expected Knowledge Base Update:**
- Agent behavior guidelines updated
- Common pitfalls section enhanced
- Agent-specific learning rules added
- Metrics tracking initialized

**Verify:** Knowledge base updated with validated patterns

---

## Integration Test: Full Learning Cycle

**Scenario:** Complete learning workflow across multiple agents

**Steps:**
1. User requests: "Implement user authentication system"
2. Orchestrator spawns swarm (2 workers)
3. Workers complete tasks, capture traces
4. Reviewer reviews, detects patterns
5. Orchestrator merges, captures coordination trace
6. Task manager analyzes decomposition
7. Trace analysis script runs automatically
8. Insights extracted and validated
9. Adaptations applied where appropriate
10. Knowledge base updated

**Expected Outcome:**
- All traces captured (worker, reviewer, orchestrator, task-manager)
- Insights extracted from patterns
- Adaptations applied (session-local initially)
- Knowledge base enriched with validated learnings
- System improved for future similar tasks

**Verify:** Complete learning cycle executed successfully

---

## Test Execution Order

1. Run Test 1 (Worker Trace Capture) - Test basic trace capture
2. Run Test 4 (Trace Analysis) - Test pattern extraction
3. Run Test 5 (Adaptation Application) - Test all adaptation levels
4. Run Test 2 (Reviewer Pattern Detection) - Test pattern detection
5. Run Test 3 (Orchestrator Optimization) - Test multi-agent coordination
6. Run Test 6 (Knowledge Base Update) - Test knowledge consolidation
7. Run Integration Test - Test end-to-end learning cycle

---

**Note:** These tests verify the self-learning mechanism works correctly. In production, learning happens automatically as agents execute tasks.
