# Phase 1-3 Detailed Design: The Core Fix

**Date**: November 5, 2025
**Purpose**: Reference guide for implementing Phases 1-3 of executor/generator redesign
**Critical Note**: This is the FOUNDATION of the entire system improvement. Everything after depends on these three phases working correctly.

---

# Overview: What We're Building

## The Problem We're Solving

**Root Cause**: Executor and Generator agents expect deliverables to exist, but nothing creates them
- Current: Planner → Executor looks for files (finds none) → Generator finds nothing → Falls back to repeating planner text
- Result: All iterations identical, no variation, no data integration

## The Solution: Three Phases

**Phase 1 (Executor)**: Executor CREATES in-memory Deliverable objects from planner's text
**Phase 2 (Generator)**: Generator SYNTHESIZES from Deliverable objects (not files, not nothing)
**Phase 3 (Memory)**: Memory context passed to executor, executor uses it to enrich deliverables

**Result**: Executor produces structured deliverables → Generator has real input → Iterations naturally vary

---

# Critical Clarification: IN-MEMORY OBJECTS, NOT FILES

## What We're Creating

```python
@dataclass
class Deliverable:
    """In-memory deliverable object (NOT a file, NOT a MemAgent entity)"""
    title: str                          # e.g., "Market Analysis"
    content: str                        # The actual completed deliverable text
    citations: List[str]                # Web sources used
    domain: str                         # e.g., "manufacturing"
    iteration: int                      # Which iteration created this
    metrics: Optional[Dict] = None      # Key metrics extracted (optional)
    source_data: Optional[Dict] = None  # Raw data used (optional)
```

## Where They Live

- **Created**: In executor_agent.py during execution
- **Passed**: From executor → generator as Python list
- **Stored**: In memory (RAM) during planning session only
- **Destroyed**: When session ends (unless explicitly saved to MemAgent)

## What They're NOT

- ❌ NOT files on disk (.md files)
- ❌ NOT MemAgent entities (that's Phase 4, beyond scope here)
- ❌ NOT persistent storage (session-scoped only)
- ✅ Just Python dataclass instances passed between agents

**Your concern about 10-20 files per iteration**: SOLVED by using in-memory objects instead of files

---

# Phase 1: Executor Agent Redesign

## Current State (Broken)

```python
# orchestrator/agents/executor_agent.py (CURRENT - BROKEN)

def execute_plan(self, plan: str, goal: str, context: Dict = None):
    # Sends prompt to LLM asking "create deliverables"
    prompt = f"Based on this plan: {plan}, create 5 deliverables..."

    response = get_model_response(prompt)

    # Counts keywords in response
    deliverable_count = response.count("deliverable")

    return AgentResult(
        success=True,
        output=response,
        content=response,
        metadata={"deliverable_count": deliverable_count}
    )

    # Returns: 0 deliverables (nothing actually created)
```

## What It Should Do

```python
# orchestrator/agents/executor_agent.py (PHASE 1 - FIXED)

def execute_plan(self, plan: str, goal: str, context: Dict = None) -> AgentResult:
    """
    Take planner's plan text and ACTUALLY CREATE deliverables.

    Flow:
    1. Parse planner text to identify what deliverables are needed
    2. For each deliverable, gather web search data + memory context
    3. Create in-memory Deliverable object with actual content
    4. Return list of Deliverable objects (not text, not files)
    """

    # STEP 1: Parse planner text to extract deliverables needed
    # Example: Planner says "We need market analysis, competitive analysis, execution plan"
    deliverables_needed = extract_deliverables_from_plan(plan)

    # STEP 2: For each deliverable, ACTUALLY CREATE it
    created_deliverables = []

    for deliverable_type in deliverables_needed:
        # Get web search data for this specific deliverable
        relevant_search_data = context.get('web_search_results', '')

        # Get memory context (if available)
        memory_context = context.get('memory_segments', [])

        # Create prompt that CREATES this deliverable
        execution_prompt = f"""
        Create a detailed {deliverable_type} for: {goal}

        Use this web search data: {relevant_search_data}
        Previous insights from memory: {memory_context}

        Include specific metrics, numbers, data points from the web search.
        Cite which sources you're using.
        """

        # Get LLM response (actual content for this deliverable)
        deliverable_content = get_model_response(execution_prompt, client=self.agent._client)

        # Create in-memory Deliverable object
        deliverable = Deliverable(
            title=deliverable_type,
            content=deliverable_content,
            citations=extract_citations(deliverable_content),
            domain=context.get('domain', 'general'),
            iteration=context.get('iteration_number', 1),
            metrics=extract_metrics(deliverable_content)
        )

        created_deliverables.append(deliverable)

    # STEP 3: Return Deliverable objects (not text, not files)
    return AgentResult(
        success=True,
        output=created_deliverables,  # List of Deliverable objects
        deliverables=created_deliverables,  # Explicit field for clarity
        metadata={
            "deliverable_count": len(created_deliverables),
            "types": [d.title for d in created_deliverables]
        }
    )
```

## Key Phase 1 Requirements

### What MUST Stay the Same
- ✅ Agent signature stays: `execute_plan(self, plan: str, goal: str, context: Dict)`
- ✅ Returns AgentResult (same class)
- ✅ Uses same domain classification from context
- ✅ Uses web search data from context (not new calls)
- ✅ Uses memory context from context (not new calls)
- ✅ Doesn't create files
- ✅ Doesn't require MemAgent yet (Phase 3)

### What CHANGES
- Input: Same (planner text)
- Processing: Parse text → Create deliverables with data → Return objects
- Output: From text → List of Deliverable objects

### Helper Functions Needed (New)

```python
def extract_deliverables_from_plan(plan_text: str) -> List[str]:
    """
    Parse planner text to identify what deliverables are needed.

    Example input: "We need market analysis, competitive landscape, and execution roadmap"
    Example output: ["Market Analysis", "Competitive Landscape", "Execution Roadmap"]

    Implementation: Could be regex, could call LLM to extract, could use domain templates
    """
    pass

def extract_citations(text: str) -> List[str]:
    """Extract citation references from deliverable text"""
    pass

def extract_metrics(text: str) -> Dict:
    """Extract key metrics/numbers from deliverable text"""
    pass
```

## Phase 1 Success Criteria

✅ Executor creates in-memory Deliverable objects
✅ Each deliverable has title, content, citations, domain, iteration
✅ Content is drawn from web search data + memory context
✅ No files created on disk
✅ Single-iteration test produces 3-5 deliverables per iteration
✅ Deliverables are different when run multiple times (due to LLM variation)
✅ No regression: Planner and Verifier agents still work unchanged

## Phase 1 Abort Criteria

❌ If agent signature changes (breaks contract with generator)
❌ If deliverables are empty/None
❌ If single-iteration test fails to produce output
❌ If system crashes trying to create deliverables
❌ If web search data not being used

---

# Phase 2: Generator Agent Redesign

## Current State (Broken)

```python
# orchestrator/agents/generator_agent.py (CURRENT - BROKEN)

def synthesize_results(self, planner_result, executor_result, verifier_result, goal, context):
    # Executor returns text with "0 deliverables"
    # Generator tries to work with that (gets nothing useful)

    # Falls back to just concatenating agent outputs
    synthesis = f"Plan: {planner_result.output}\nVerified: {verifier_result.output}"

    return AgentResult(success=True, output=synthesis)

    # Returns: Text that's basically a copy of planner output
```

## What It Should Do

```python
# orchestrator/agents/generator_agent.py (PHASE 2 - FIXED)

def synthesize_results(self, planner_result: AgentResult, executor_result: AgentResult,
                       verifier_result: AgentResult, goal: str, context: Dict) -> AgentResult:
    """
    Synthesize FROM actual deliverables (not from nothing).

    Flow:
    1. Receive list of Deliverable objects from executor
    2. Organize them into comprehensive structure
    3. Synthesize into final plan, different per iteration
    4. Return comprehensive synthesized plan
    """

    # STEP 1: Extract deliverables from executor result
    deliverables = executor_result.output  # This is the list of Deliverable objects!

    # STEP 2: Organize deliverables by type/domain
    organized_deliverables = organize_by_type(deliverables)

    # STEP 3: Build synthesis prompt that uses actual deliverable data
    synthesis_prompt = f"""
    Synthesize the following planning deliverables into a comprehensive final plan:

    Goal: {goal}
    Iteration: {context.get('iteration_number', 1)}

    Completed Deliverables:
    {format_deliverables_for_synthesis(deliverables)}

    Planning Approach Validation: {verifier_result.output}

    Create a comprehensive, structured final plan that:
    - Synthesizes all deliverables into coherent sections
    - Maintains data from each deliverable
    - Structures per iteration level (iteration {context.get('iteration_number')} approach)
    - Is different from previous iteration if this is iteration 2+

    For iteration 2+, emphasize what's NEW and what's DEEPER compared to iteration 1.
    """

    # STEP 4: Get synthesized output
    final_synthesis = get_model_response(synthesis_prompt, client=self.agent._client)

    # STEP 5: Return comprehensive plan
    return AgentResult(
        success=True,
        output=final_synthesis,
        content=final_synthesis,
        metadata={
            "deliverable_count": len(deliverables),
            "deliverable_types": [d.title for d in deliverables],
            "iteration": context.get('iteration_number', 1),
            "synthesis_quality": "comprehensive"  # vs fallback which was "simple"
        }
    )
```

## Key Phase 2 Requirements

### What MUST Stay the Same
- ✅ Agent signature: `synthesize_results(self, planner_result, executor_result, verifier_result, goal, context)`
- ✅ Returns AgentResult
- ✅ Uses verifier feedback for validation
- ✅ Works with domain context
- ✅ Doesn't create files

### What CHANGES
- Input executor_result: From text → List of Deliverable objects
- Processing: From "concatenate text" → "Synthesize from structured deliverables"
- Output: From "copy of planner" → "Unique synthesis per iteration"

### Helper Functions Needed (New)

```python
def organize_by_type(deliverables: List[Deliverable]) -> Dict:
    """Organize deliverables by type for easier synthesis"""
    pass

def format_deliverables_for_synthesis(deliverables: List[Deliverable]) -> str:
    """Format deliverable objects as readable text for LLM synthesis"""
    pass
```

## Phase 2 Success Criteria

✅ Generator receives list of Deliverable objects from executor
✅ Generator synthesizes from deliverables (not from executor text)
✅ Synthesis is different for iteration 2+ (emphasizes NEW/DEEPER)
✅ Final plan is comprehensive and data-driven
✅ Browser displays varied plans across iterations
✅ Each iteration's synthesis is substantively different
✅ Verifier feedback incorporated into synthesis

## Phase 2 Abort Criteria

❌ If executor_result doesn't contain deliverables list
❌ If generator crashes trying to access deliverables
❌ If synthesis is empty or just fallback text
❌ If iteration 2 synthesis is identical to iteration 1
❌ If browser shows error instead of plan

---

# Phase 3: SegmentedMemory Integration

## Current State (Partially Broken)

```python
# approval_gates.py (CURRENT - PARTIAL)

self.memory_manager = SegmentedMemory(
    max_segments=12,
    max_tokens_per_segment=2000,
    memagent_client=self.agent
)

# Memory IS initialized but:
# - Not passed to context_builder.py
# - Agents don't receive memory_segments in context
# - Log says "No segmented memory available"
```

## What It Should Do

```python
# orchestrator/context/context_builder.py (PHASE 3 - FIXED)

def retrieve_context(self, goal: str, session=None) -> Dict:
    """Retrieve full planning context including memory segments"""

    # ... existing retrieval code ...

    # ADD: Retrieve memory segments
    memory_segments = []
    if session and hasattr(session, 'memory_manager'):
        memory_segments = session.memory_manager.get_relevant_segments(
            query=goal,
            top_k=3  # Get top 3 most relevant segments
        )

    context = {
        "goal": goal,
        "domain": goal_analysis.domain,
        "web_search_results": web_search_results,
        "successful_patterns": ...,
        "memory_segments": memory_segments,  # NEW
        "iteration_number": ...,
        # ... other context fields ...
    }

    return context
```

## Phase 3: Pass Memory to Agents

```python
# orchestrator/agents/executor_agent.py (PHASE 3 - UPDATED)

def execute_plan(self, plan: str, goal: str, context: Dict = None):
    # NEW: Use memory context
    memory_context = context.get('memory_segments', [])

    for deliverable_type in deliverables_needed:
        execution_prompt = f"""
        Create a detailed {deliverable_type}

        Web search data: {context.get('web_search_results')}
        Previous successful patterns from memory: {memory_context}  # NEW

        Learn from what worked before. Avoid what failed.
        """

        # ... rest of execution ...
```

## Key Phase 3 Requirements

### What MUST Stay the Same
- ✅ SegmentedMemory initialization (don't touch approval_gates.py creation)
- ✅ Memory limit of 12 segments (don't change max_segments)
- ✅ Agent signatures unchanged
- ✅ Context structure (just add memory_segments field)

### What CHANGES
- Context builder: Retrieve and pass memory_segments
- Executor: Use memory_segments when creating deliverables
- Agents: Reference memory in their prompts

### Phase 3 Success Criteria

✅ Memory segments retrieved successfully (not "unavailable")
✅ Executor receives memory_segments in context
✅ Executor uses memory to inform deliverable creation
✅ Deliverables reference memory patterns/insights
✅ Memory stays bounded (< 12 segments)
✅ Multi-iteration test shows memory influence (iteration 2 different from 1)

### Phase 3 Abort Criteria

❌ If memory retrieval fails or returns None
❌ If agent prompts don't reference memory context
❌ If memory explodes beyond 12 segments
❌ If system crashes trying to access memory

---

# What ABSOLUTELY MUST NOT CHANGE

## Safety Guardrails (Non-Negotiable)

### 1. Domain Classification System
- ✅ Keep: goal_analyzer.py (classification logic)
- ✅ Keep: Domain detection (manufacturing, healthcare, etc.)
- ✅ Keep: Template selection based on domain
- ❌ DON'T: Modify domain classification
- ❌ DON'T: Let agents choose their own domain guidance

### 2. Four-Agent Workflow Order
- ✅ Keep: Planner → Verifier → Executor → Generator order
- ✅ Keep: Each agent depends on previous output
- ❌ DON'T: Reorder agents
- ❌ DON'T: Skip agents
- ❌ DON'T: Let agents run in parallel

### 3. Structured Context Passing
- ✅ Keep: Context as Dict with known fields
- ✅ Keep: Each field populated before use
- ✅ Add: memory_segments field (append, not replace)
- ❌ DON'T: Make context unstructured
- ❌ DON'T: Let agents hallucinate missing context

### 4. Template-Based Planning
- ✅ Keep: Domain-specific templates guide agent prompts
- ✅ Keep: Templates constrain agent behavior
- ✅ Enhance: Templates can reference more data
- ❌ DON'T: Remove templates
- ❌ DON'T: Let agents ignore templates
- ❌ DON'T: Make planning completely unstructured

### 5. Fallback Mechanisms
- ✅ Keep: All existing fallbacks (don't touch them)
- ✅ Keep: System won't crash if something fails
- ✅ Keep: Fallback synthesis as safety net during Phase 1-2
- ❌ DON'T: Remove fallbacks (we're working alongside them)

---

# Data Flow Changes

## From → To

```
BEFORE (Broken):
Planner Text
  ↓
Executor (looks for files) → finds nothing
  ↓
Generator (finds nothing) → falls back to repeating planner
  ↓
Identical iterations

AFTER (Fixed Phase 1-3):
Planner Text ("we need market analysis, competitive analysis, roadmap")
  ↓
Executor (creates Deliverable objects with actual web data + memory context)
  ↓
Generator (synthesizes from Deliverable objects)
  ↓
Varied, data-driven iterations
```

## Context Flow Changes

```
BEFORE:
Context = {
  'goal': str,
  'domain': str,
  'web_search_results': str,
  'successful_patterns': dict,
  # memory_segments missing or unavailable
}

AFTER (Phase 3):
Context = {
  'goal': str,
  'domain': str,
  'web_search_results': str,
  'successful_patterns': dict,
  'memory_segments': List[MemorySegment],  # NEW - Phase 3
  'iteration_number': int,
  # ... other fields ...
}
```

---

# Testing Strategy for Each Phase

## Phase 1 Testing (Executor)

```bash
# Single iteration, single goal
Test: "Create a product expansion approach for Oriental Saigon"
Expected:
  1. Planner generates plan text ✅
  2. Executor creates 3-5 Deliverable objects ✅
  3. Each deliverable has title, content, citations ✅
  4. No files created on disk ✅
  5. Browser shows executor output (or generator falls back to it)

Verify:
  - Planner test still works (single iteration)
  - No crashes in executor
  - Deliverables list non-empty
```

## Phase 2 Testing (Generator)

```bash
# Single iteration
Test: "Create a product expansion approach for Oriental Saigon"
Expected:
  1. Executor creates deliverables ✅
  2. Generator receives deliverables list ✅
  3. Generator synthesizes into comprehensive plan ✅
  4. Browser shows DIFFERENT content from pure planner (synthesized from deliverables)
  5. Plan is substantive (has data, not generic template)

Verify:
  - Synthesis is different from Phase 1 (uses deliverables)
  - No fallback needed (generator works)
  - Output quality good
```

## Phase 3 Testing (Memory)

```bash
# Two iterations, 1 checkpoint interval
Test: "Create a product expansion approach" → Approve → Iteration 2
Expected:
  1. Iteration 1: Executor creates deliverables (no prior memory)
  2. Memory segments available for iteration 2
  3. Iteration 2: Executor creates DIFFERENT deliverables (uses iteration 1 memory)
  4. Iteration 2 and 1 outputs are substantively different
  5. Memory stays bounded (< 12 segments after 2 iterations)

Verify:
  - Memory successfully passed through context
  - Executor uses memory when creating deliverables
  - Iteration 2 is different from iteration 1 (NEW frameworks, different metrics)
  - No memory explosion
```

---

# Success Criteria (Overall Phase 1-3)

Once all three phases complete:

✅ **Executor creates structured Deliverable objects**
✅ **Generator synthesizes from those objects**
✅ **Iterations are substantively different** (not identical)
✅ **Plans are data-driven** (web search + memory context visible)
✅ **System produces no errors** (all 3 iterations complete successfully)
✅ **Memory stays bounded** (< 12 segments)
✅ **All existing tests still pass** (no regressions)
✅ **Browser shows comprehensive, varying plans**
✅ **Manual planning iterations still work unchanged**

---

# Abort Criteria (Stop and Rollback)

If ANY of these happen, STOP immediately and rollback:

❌ Domain classification breaks (agents get wrong domain)
❌ Domain templates no longer used (agents go off-rails)
❌ Four-agent order changes (workflow integrity broken)
❌ Executor crashes trying to create deliverables
❌ Generator crashes trying to synthesize
❌ Memory explodes beyond 12 segments
❌ Single iteration test fails (regression)
❌ Planner agent broken (unintended side effect)
❌ System produces no output at all
❌ Verification cascades into system failure

**If any of above happen**: Revert changes, analyze what went wrong, design safer approach.

---

# Key Design Decisions

## Decision 1: Deliverable Structure
- **Chosen**: Minimal dataclass with title, content, citations, domain, iteration
- **Why**: Simple, passes between agents easily, no external dependencies
- **Alternative rejected**: Rich structure (would require Phase 4 MemAgent)

## Decision 2: Extract Deliverables from Planner Text
- **Chosen**: Parse planner output to identify deliverables needed
- **Why**: Planner already describes them, just need to extract
- **Alternative rejected**: Hardcode deliverable types (inflexible)

## Decision 3: One Deliverable Creation Call per Type
- **Chosen**: For each deliverable type, call LLM once to create it fully
- **Why**: Full content per call, uses context properly, clean separation
- **Alternative rejected**: Create all at once (harder to cite sources per deliverable)

## Decision 4: Keep Fallback Synthesis Active
- **Chosen**: Don't disable fallback during Phase 1-3
- **Why**: Safety net if something breaks, can rollback gracefully
- **Alternative rejected**: Remove fallback (too risky)

## Decision 5: Phase 3 = Just Pass Memory (Not Store)
- **Chosen**: Phase 1-3 create and use in-memory objects, Phase 4 would store to MemAgent
- **Why**: Reduces scope, reduces complexity, proves concept first
- **Alternative rejected**: Store to MemAgent in Phase 3 (adds complexity, not needed for MVP)

---

# Reference During Implementation

**When unsure, ask:**
1. "Is this creating files or in-memory objects?" → Should be objects
2. "Am I changing agent signatures?" → Should NOT change them
3. "Am I removing domain classification?" → Should NOT touch it
4. "Am I removing template system?" → Should NOT touch it
5. "Does this still pass data through Context?" → Should use structured context
6. "Does this keep fallback mechanisms?" → Should NOT disable fallbacks
7. "Am I making Phase X changes in the wrong phase?" → Should follow sequence

**Keep this file open during all implementation.** Reference sections as you code.

---

# Summary

**What we're doing**:
- Executor creates Deliverable objects (in-memory, not files)
- Generator synthesizes from those objects
- Memory context provided to executor
- Result: Varied, data-driven iterations without breaking current structure

**Timeline**: ~1-2 days per phase (3-6 days total for Phases 1-3)

**Risk Level**: MEDIUM-HIGH (core pipeline) but MANAGEABLE (clear phases, testing checkpoints)

**Outcome**: System still runs the same way, but produces MASSIVELY different quality plans with natural iteration variation

**If something breaks**: Reference abort criteria, rollback, analyze safely
