# IMPLEMENTATION PLAN: User-Constrained MemAgent Architecture

**Date Created:** November 10, 2025
**Status:** Ready for Execution
**Estimated Duration:** 3.5 hours

---

## Core Principle

ALL MemAgent searches throughout the system must respect user-selected boundaries (`selected_plans` and `selected_entities`). No autonomous memory scouring. Users maintain control over what information informs planning.

**Variable Naming:** Keep existing names (`selected_plans`, `selected_entities`) - already clear from docstrings that these are "user selected". Add explicit comments about constraint boundaries.

---

## PHASE 1: Constrain ALL MemAgent Searches (Architectural Foundation)

### 1.1 Update MemoryContextProvider
**File:** `orchestrator/context/memory_context.py`

**Change:** Add `selected_plans` parameter to all methods

Methods to update:
- `retrieve_successful_patterns(agent, selected_plans=None)` → Constrain search to selected_plans
- `retrieve_error_patterns(agent, selected_plans=None)` → Constrain search to selected_plans
- `retrieve_execution_history(agent, selected_plans=None)` → Constrain search to selected_plans
- `retrieve_agent_performance(agent, selected_plans=None)` → Constrain search to selected_plans

**Pattern:** Each method adds constraint to MemAgent query:
```python
# USER-DEFINED CONSTRAINT BOUNDARIES:
# These selected_plans represent user's explicit choice of context
# MemAgent searches ONLY within these boundaries
query = f"""
CONSTRAINT: Analyze ONLY within these {len(selected_plans)} user-selected plans:
{', '.join(selected_plans)}

Do NOT search beyond these specified plans.
"""
```

**Fallback Logic:** If `selected_plans` is empty or None:
- Return empty results (don't search broadly)
- User hasn't selected plans, so don't assume what to learn from

---

### 1.2 Update ContextBuilder to Propagate Constraints
**File:** `orchestrator/context/context_builder.py`

**Change:** Accept and pass `selected_plans` parameter through

**Current signature (line 44):**
```python
def retrieve_context(self, goal: str, session=None, selected_entities: list = None) -> Dict[str, str]:
```

**New signature:**
```python
def retrieve_context(self, goal: str, session=None, selected_entities: list = None, selected_plans: list = None) -> Dict[str, str]:
```

**Implementation:**
- Pass `selected_plans` to all MemoryContextProvider method calls (lines 84-87)
- Each call includes: `selected_plans=selected_plans or []`

**Return context includes:**
- Existing: goal_analysis, current_status, web_search_results, memory_segments, selected_entities, entities_context
- Now constrained: successful_patterns, error_patterns, execution_history, agent_performance (all respect user boundaries)

---

### 1.3 Update SimpleOrchestrator to Pass Constraints
**File:** `orchestrator/simple_orchestrator.py`

**Current code (line 167-171):**
```python
context = self.context_manager.retrieve_context(
    goal,
    session=self.segmented_memory,
    selected_entities=self.selected_entities
)
```

**New code:**
```python
context = self.context_manager.retrieve_context(
    goal,
    session=self.segmented_memory,
    selected_entities=self.selected_entities,
    selected_plans=self.selected_plans  # ADD THIS LINE
)
```

**Comment to add:**
```python
# USER-DEFINED CONSTRAINT BOUNDARIES:
# Pass selected_plans so ALL MemAgent searches respect user's choices
# No autonomous memory scouring - only search what user explicitly selected
```

---

## PHASE 2: Enhance CheckpointAgent (Synthesis & Analysis)

### 2.1 Add New Analysis Methods to CheckpointAgent
**File:** `orchestrator/agents/checkpoint_agent.py`

**New Method 1: `_analyze_entity_usage()`**
- Input: Iteration outputs, selected_entities count
- Logic: Count entity name mentions in iteration output
- Output:
  ```python
  {
      "entities_referenced": 3,
      "entities_total": 5,
      "coverage_percent": 60.0,
      "assessment": "Good utilization of selected context"
  }
  ```

**New Method 2: `_analyze_plan_alignment()`**
- Input: Iteration results, selected_plans
- Logic: Check if frameworks from selected plans were used
- Output:
  ```python
  {
      "patterns_applied": 2,
      "patterns_available": 5,
      "frameworks_aligned": 3,
      "learning_quality": 0.78,
      "assessment": "Strong alignment with selected plans"
  }
  ```

**Update Method: `_find_relevant_patterns()`**
- Keep existing constrained search (ONLY within selected_plans)
- Improve extraction to return top 3 patterns with confidence scores
- Mark source as "selected_plans" to distinguish from broad pattern searches

---

### 2.2 Update CheckpointAgent Output Structure
**File:** `orchestrator/agents/checkpoint_agent.py`

**New metadata structure in synthesize_checkpoint() return:**
```python
metadata = {
    "iteration": current_iteration,

    # NEW: Entity & Plan Usage Analysis
    "entity_usage": {
        "entities_referenced": 3,
        "entities_total": 5,
        "coverage_percent": 60.0,
        "assessment": "Good utilization"
    },

    "plan_alignment": {
        "patterns_applied": 2,
        "patterns_available": 5,
        "frameworks_aligned": 3,
        "learning_quality": 0.78,
        "assessment": "Strong alignment"
    },

    # EXISTING (leveraged): Improvements from iteration tracking
    "improvements": {
        "data_points_delta": 15,
        "evidence_density_improvement": 0.22,
        "frameworks_new": 2,
        "gaps_narrowed": 4
    },

    # EXISTING (leveraged): Confidence scores from FlowGRPO
    "confidence": {
        "planner": 0.85,
        "verifier": 0.78,
        "executor": 0.82,
        "generator": 0.80,
        "overall": 0.81
    },

    # EXISTING (leveraged): Reasoning from PDDL-INSTRUCT
    "reasoning_chain": [...],

    # NEW: Patterns from constrained search
    "pattern_recommendations": [
        {"pattern": "...", "source": "selected_plans", "relevance": "high"},
        {"pattern": "...", "source": "selected_plans", "relevance": "medium"}
    ],

    # NEW: Synthesis recommendation
    "recommendation": {
        "status": "continue",
        "reason": "...",
        "confidence": "81%",
        "next_steps": "..."
    }
}
```

---

## PHASE 3: Update Frontend (Minimal, Complementary)

### 3.1 Checkpoint Modal Updates
**File:** `static/index.html`

**Remove rendering for:**
- ❌ `flow_score_metrics.frameworks_so_far` (doesn't exist - frameworks tracked at iteration level)
- ❌ `memory_segments` array (not provided by checkpoint)
- ❌ `data_points_so_far` cumulative (only delta available)

**Add rendering for:**
- ✅ `entity_usage` section (show coverage % and assessment)
- ✅ `plan_alignment` section (show patterns applied and learning quality)
- ✅ `improvements` section (show deltas from iteration)
- ✅ `confidence` section (show agent scores and overall)
- ✅ `reasoning_chain` section (show logical steps)
- ✅ `recommendation` section (show continue/review with reasoning)

**UI Structure:**
```
[Checkpoint Summary Tab]
  → Full narrative from CheckpointAgent synthesis

[Entity & Plan Utilization Tab]
  → 3 of 5 selected entities referenced (60% coverage)
  → 2 of 5 selected plan patterns applied
  → Learning quality: 78%

[Iteration Improvements Tab]
  → Data points: +15 this iteration
  → Evidence density: +22%
  → Frameworks: 2 new
  → Gaps narrowed: 4

[Verification & Confidence Tab]
  → Planner: 85%, Verifier: 78%, Executor: 82%, Generator: 80%
  → Overall Confidence: 81%
  → Reasoning chain steps (from PDDL-INSTRUCT)

[Recommendation Tab]
  → Continue / Review decision with reasoning
  → Next steps guidance
```

---

## Implementation Order

| Phase | Task | Files | Complexity | Estimated Time |
|-------|------|-------|-----------|-----------------|
| 1 | Constrain MemoryContextProvider | memory_context.py | Small | 30 min |
| 1 | Update ContextBuilder signatures | context_builder.py | Tiny | 15 min |
| 1 | Update SimpleOrchestrator flow | simple_orchestrator.py | Tiny | 10 min |
| 2 | Add entity_usage analysis method | checkpoint_agent.py | Small | 20 min |
| 2 | Add plan_alignment analysis method | checkpoint_agent.py | Small | 20 min |
| 2 | Update metadata output structure | checkpoint_agent.py | Tiny | 10 min |
| 3 | Update frontend checkpoint rendering | index.html | Medium | 60 min |
| - | **End-to-end testing** | All | Medium | 30 min |
| - | **TOTAL** | - | - | **~3.5 hours** |

---

## What This Achieves

✅ **True Human-In-Loop:** Every MemAgent search constrained to user selections
✅ **No Autonomous Scouring:** All memory access intentional and user-boundary-respecting
✅ **Complements Existing System:** Builds on FlowGRPO + PDDL + iteration tracking (nothing breaks)
✅ **Session-Only Storage:** No file creation during iterations (stored in memory)
✅ **Meaningful Checkpoints:** Users see exactly how iteration leveraged their selections
✅ **Clear Naming:** Existing `selected_plans`/`selected_entities` kept; comments clarify intent
✅ **Minimal Changes:** Only adds constraints and analysis, doesn't rebuild architecture

---

## What Stays Unchanged

- ProposalAgent (analysis only)
- 4-agent workflow (planner, verifier, executor, generator)
- FlowGRPO learning mechanism
- PDDL-INSTRUCT reasoning
- IterationManager tracking
- LearningManager synthesis
- All variable names (`selected_plans`, `selected_entities`)

---

## Architecture Context

**Related Discovery Documents:**
- See `COMPREHENSIVE_ARCHITECTURE_ANALYSIS.md` for detailed data flow mapping
- See `CLAUDE.md` for system overview

**Key Files Involved:**
- `orchestrator/context/memory_context.py` - MemAgent constraints
- `orchestrator/context/context_builder.py` - Context propagation
- `orchestrator/simple_orchestrator.py` - Orchestrator integration
- `orchestrator/agents/checkpoint_agent.py` - Analysis enhancements
- `simple_chatbox.py` - API endpoints (already integrated)
- `static/index.html` - Frontend rendering
