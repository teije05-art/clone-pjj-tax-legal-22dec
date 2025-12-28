# Research Framework Alignment
## How Project Jupiter Implements MemAgent, PDDL-INSTRUCT, and Flow-GRPO

This document maps research principles to their implementation in Project Jupiter. It serves as the "why" behind all architectural decisions and code changes in Phases 1-5.

---

## Table of Contents

1. [MemAgent: Segment-Based Memory Integration](#memagent-segment-based-memory-integration)
2. [PDDL-INSTRUCT: Logical Reasoning & Verification](#pddl-instruct-logical-reasoning--verification)
3. [Flow-GRPO: Mid-Iteration Learning & Training Signals](#flow-grpo-mid-iteration-learning--training-signals)
4. [System Integration Loop: Memory ↔ Reasoning ↔ Learning](#system-integration-loop)
5. [Implementation Phase Map](#implementation-phase-map)

---

## MemAgent: Segment-Based Memory Integration

### Research Foundation: ByteDance MemAgent (2507.02259v1)

**What It Is:**
MemAgent is a multi-conversation reinforcement learning approach that addresses the "infinite context window" problem by using:
- **Fixed-length memory**: Unlike traditional LLMs that grow context with each conversation, MemAgent maintains a constant-size memory bank
- **Segment-based compression**: Long documents are divided into overlapping segments that compress losslessly
- **RL-trained overwrite strategy**: When memory is full, the system learns which segments to overwrite based on future utility
- **Token-level compression**: Memory updates use token-level (not feature-space) compression for precision

**Key Metrics (from paper):**
- Extrapolates from 8K context window to 3.5M tokens with <5% performance loss
- Linear O(N) complexity through constant memory size
- DAPO training (Dynamic RL algorithm) learns segment importance scores
- Works across long documents without catastrophic forgetting

### Implementation in Project Jupiter: Phase 1

#### Current State (Before Phase 1):
- Checkpoint summaries stored as unbounded dicts (`checkpoint_summaries = {}`)
- Iteration progress tracked without fixed limits (`iteration_progress = {}`)
- No compression of old memory
- Memory grows linearly with planning iterations

#### New State (After Phase 1):
```
Project Jupiter: MemAgent-Based Memory
├── Fixed-Size Memory (12 segments max, ~24K tokens total)
│   ├── Segment 0: Planning frameworks used
│   ├── Segment 1: User's approved patterns
│   ├── Segment 2: Market context & research
│   ├── Segment 3-11: Iteration results, entity info, etc.
│   └── When memory is full: Least-important segment is compressed
├── Compression Strategy
│   ├── Token counting per segment
│   ├── Importance scoring based on plan outcomes
│   ├── Lossless compression using abstractive summarization
│   └── Retains semantic meaning despite 30-50% token reduction
└── Overwrite Training
    ├── Track which segments were used in successful plans
    ├── Update segment importance scores
    └── Learn which segments to overwrite first
```

#### Module: `orchestrator/memory/memagent_memory.py` (NEW)

**SegmentedMemory Class:**
```python
class SegmentedMemory:
    """Fixed-length memory following MemAgent principles."""

    def __init__(self, max_segments: int = 12, max_tokens_per_segment: int = 2000):
        """Initialize with fixed segment count."""
        self.segments = []  # Max 12 segments
        self.segment_metadata = {}  # Track importance, tokens, source
        self.overwrite_scores = {}  # RL-trained scores

    def add_segment(self, content: str, source: str, importance_score: float):
        """Add segment with compression if needed."""
        # If at capacity, find least important segment (RL scoring)
        # Compress that segment or remove it
        # Add new segment

    def get_relevant_segments(self, query: str) -> List[str]:
        """Retrieve top-K segments for query using semantic search."""
        # Embed query (via MemAgent)
        # Score segments by relevance
        # Return top-3 most relevant segments

    def compress_segment(self, segment_idx: int) -> str:
        """Lossless compression of segment."""
        # Use abstractive summarization
        # Maintain semantic meaning
        # Track compression ratio

    def train_overwrite_scores(self, plan_result: dict):
        """Update which segments matter based on plan outcome."""
        # Which segments were used in this iteration?
        # Did user approve the plan? (positive signal)
        # Update segment importance scores
        # Learn overwrite preferences
```

**Integration Points:**
- `approval_gates.py`: Replace `self.checkpoint_summaries = {}` with `self.memory_manager = SegmentedMemory(max_segments=12)`
- `llama_planner.py`: Add `extract_memory_deltas()` and `estimate_segment_importance()` methods
- `simple_chatbox.py`: Pass memory context to all agents during planning

#### Success Criteria for Phase 1:
- ✅ Memory stays bounded at 12 segments max (~24K tokens)
- ✅ Semantic search retrieves relevant segments
- ✅ Old plans still execute without regression
- ✅ System learns which segments matter (overwrite scores improve)

---

## PDDL-INSTRUCT: Logical Reasoning & Verification

### Research Foundation: PDDL-INSTRUCT (2509.13351v1)

**What It Is:**
PDDL-INSTRUCT teaches LLMs to plan with logical chain-of-thought reasoning by:
- **Symbolic planning format**: Preconditions → Actions → Effects structure
- **Two-stage optimization**: (1) Reasoning chain quality → (2) End-task performance
- **VAL verification**: Check if action preconditions are met and effects match expectations
- **Binary vs. detailed feedback**: System can provide fine-grained feedback on what failed

**Key Metrics (from paper):**
- Blocksworld planning: 94% accuracy
- Logistics domain: 79% accuracy
- Mystery Blocksworld: 64% accuracy
- Verification feedback improves quality when detailed (not just binary)

**Example PDDL Reasoning Chain:**
```
GOAL: Create marketing strategy for e-commerce brand

PRECONDITIONS:
- Market research complete
- Target audience defined
- Competitor analysis done
- Budget constraints clear

REASONING_CHAIN:
1. Analyze market: Gap analysis reveals opportunity
2. Define positioning: Premium eco-friendly segment
3. Plan tactics: Content marketing + partnerships
4. Set KPIs: Revenue target, brand awareness, engagement
5. Timeline: Phases over 6 months

EFFECTS:
- Strategic roadmap created
- Implementation timeline defined
- KPIs established
- Risks identified

VERIFICATION:
✅ All preconditions met? Yes
✅ Each step sound? Yes (market → positioning → tactics → KPIs → timeline)
✅ Effects align with goal? Yes
```

### Implementation in Project Jupiter: Phase 2

#### Current State (Before Phase 2):
- Agents run with generic LLM prompts
- No formal reasoning chain structure
- No precondition checking
- No verification feedback on plan logic

#### New State (After Phase 2):
```
Project Jupiter: PDDL-Based Reasoning
├── Logical Planning Prompts (NEW)
│   ├── Goal statement with context
│   ├── Required preconditions for planning
│   ├── Reasoning chain structure (5-7 steps)
│   └── Expected effects definition
├── Agent Results Now Include
│   ├── content: The plan (as before)
│   ├── reasoning_chain: Steps taken (NEW)
│   ├── preconditions_met: Boolean (NEW)
│   └── verification_feedback: What worked/failed (NEW)
└── Verification System
    ├── Check preconditions before planning
    ├── Validate reasoning chain logic
    ├── Verify effects match preconditions
    └── Return detailed feedback
```

#### Module: `orchestrator/reasoning/logical_planner.py` (NEW)

**LogicalPlanningPrompt Class:**
```python
class LogicalPlanningPrompt:
    """Generates PDDL-style reasoning prompts."""

    def __init__(self, goal: str, domain: str):
        """Initialize logical planning context."""
        self.goal = goal
        self.domain = domain

    def generate_precondition_checks(self, context: dict) -> str:
        """Generate precondition verification."""
        # "For this goal, these preconditions must be true: X, Y, Z"
        # Check each precondition against context
        # Return: list of met/unmet preconditions

    def generate_reasoning_chain_prompt(self) -> str:
        """Generate prompt requesting structured reasoning."""
        # Return prompt asking for 5-7 step reasoning
        # Include template: "Step 1: [Action]. Why? [Justification]"
        # Include verification section

    def generate_effect_verification(self, expected_effects: list) -> str:
        """Generate verification prompt for effects."""
        # "After this plan, these effects should occur: A, B, C"
        # Ask: "Do your proposed actions create these effects?"
        # Request justification for each effect
```

#### Module: `orchestrator/reasoning/verification_feedback.py` (NEW)

**VerificationFeedback Class:**
```python
class VerificationFeedback:
    """VAL-like verification for symbolic planning."""

    def check_preconditions(self, action: str, state: dict) -> dict:
        """Verify preconditions for an action."""
        # Return: {"precondition": "...", "met": True/False}
        # Example: "Market research complete" → met=True

    def check_effects(self, action: str, expected_effects: list,
                      actual_state: dict) -> dict:
        """Verify effects occurred."""
        # Return: {"effect": "...", "occurred": True/False}
        # Example: "Strategic roadmap created" → occurred=True

    def generate_binary_feedback(self, success: bool) -> str:
        """Simple: 'Correct' / 'Incorrect'"""
        return "Correct" if success else "Incorrect"

    def generate_detailed_feedback(self, checks: dict) -> str:
        """Detailed: Which preconditions failed? Which effects missing?"""
        # Return: "Preconditions met: 3/4 (missing: Budget constraints)"
        # Return: "Effects achieved: 3/4 (missing: Implementation timeline)"
```

#### Integration with Agents: `orchestrator/agents/planner_agent.py` (MODIFIED)

**Modified PlannerAgent to include logical reasoning:**
```python
class PlannerAgent(BaseAgent):
    def run(self, context: dict) -> AgentResult:
        # NEW: Generate logical planning prompt
        logical_prompt = LogicalPlanningPrompt(
            goal=context['goal'],
            domain=context['domain']
        )

        # NEW: Include precondition checks in prompt
        precondition_text = logical_prompt.generate_precondition_checks(context)

        # NEW: Request reasoning chain from Llama
        llm_response = self.llm.generate(
            self._generate_planning_prompt(context, precondition_text)
        )

        # Extract content + reasoning chain from response
        content = llm_response['content']
        reasoning_chain = llm_response.get('reasoning_chain', [])
        preconditions_met = llm_response.get('preconditions_met', True)

        # NEW: Return extended AgentResult
        return AgentResult(
            success=True,
            content=content,
            metadata={
                'reasoning_chain': reasoning_chain,
                'preconditions_met': preconditions_met,
                'domain': context['domain']
            }
        )
```

#### Integration with Workflow: `orchestrator/workflow_coordinator.py` (MODIFIED)

**Modified to collect verification feedback:**
```python
# After each agent runs:
planner_result = planner.run(context)

# NEW: Verify the reasoning
verifier = VerificationFeedback()
verification_report = {
    'agent': 'planner',
    'preconditions_met': planner_result.metadata.get('preconditions_met', True),
    'reasoning_chains': planner_result.metadata.get('reasoning_chain', [])
}

# Next agent uses verification feedback
verifier_result = verifier.run(
    planner_result.content,
    feedback=verification_report  # NEW
)

# Store feedback for learning system
session.iteration_progress[iteration]['verification_feedback'] = verification_report
```

#### Success Criteria for Phase 2:
- ✅ Agent responses include logical reasoning chains
- ✅ Verification feedback correctly identifies logic errors
- ✅ System tracks reasoning quality (% preconditions met)
- ✅ No performance regression in planning speed

---

## Flow-GRPO: Mid-Iteration Learning & Training Signals

### Research Foundation: AgentFlow + Flow-GRPO (lupantech/AgentFlow)

**What It Is:**
Flow-GRPO is an on-policy reinforcement learning approach for training agents in workflows:
- **Group Relative Policy Optimization**: Train agents based on relative performance against baselines
- **In-the-flow training**: Learn during execution, not as separate batch process
- **Sparse rewards from verification**: Use logical verification feedback as reward signal
- **Agent selection learning**: Learn which agents to run and in what order

**Key Concepts:**
- **Reward Signal**: Verification feedback quality + user approval = reward
- **Policy**: Which agents to run, which patterns to apply
- **Training**: Update agent selection and pattern recommendation based on rewards

### Implementation in Project Jupiter: Phase 3

#### Current State (Before Phase 3):
- 4-agent pipeline is hardcoded (always: Planner → Verifier → Executor → Generator)
- Learning only happens at end of planning (batch)
- No mid-iteration pattern recommendations
- Agent coordination is fixed, not learned

#### New State (After Phase 3):
```
Project Jupiter: Flow-GRPO Learning
├── Mid-Iteration Learning (NEW)
│   ├── After iteration N: Calculate flow_score
│   ├── flow_score = verification_feedback_quality × user_approval
│   ├── Store flow_score in iteration metadata
│   ├── Update agent selection weights immediately
│   └── Recommend patterns for iteration N+1
├── Pattern Effectiveness Tracking (NEW)
│   ├── Track which patterns were used
│   ├── Score by: flow_score × verification_quality
│   ├── High-value: Good flow + verification + user approved
│   ├── Medium-value: Good flow OR verification (not both)
│   └── Low-value: Failed verification (don't recommend)
└── Agent Coordination Learning (NEW)
    ├── Track which agent pairs work well
    ├── Example: "Planner + Verifier flow_score=0.85"
    ├── Example: "Executor without Verifier flow_score=0.61"
    └── Recommend sequences dynamically
```

#### Module: `orchestrator/learning/flow_grpo_trainer.py` (NEW)

**FlowGRPOTrainer Class:**
```python
class FlowGRPOTrainer:
    """Trains agent selection and pattern recommendation via Flow-GRPO."""

    def __init__(self):
        """Initialize trainer."""
        self.agent_selection_weights = {
            'planner': 1.0,
            'verifier': 1.0,
            'executor': 1.0,
            'generator': 1.0
        }
        self.agent_pair_scores = {}  # (agent1, agent2) → score

    def record_iteration_signal(self,
                               iteration: int,
                               agent_name: str,
                               verification_feedback: dict,
                               user_approved: bool,
                               reasoning_quality: float):
        """Record training signal for this iteration."""
        # Calculate flow_score
        flow_score = (
            verification_feedback['quality'] *  # 0-1 score
            (1.0 if user_approved else 0.5) *  # Approved=1.0, Rejected=0.5
            reasoning_quality  # 0-1 score
        )

        # Update agent weight
        self.agent_selection_weights[agent_name] *= (1 + 0.1 * (flow_score - 0.5))

        # Store for pattern learning
        self.iteration_signals[iteration] = {
            'agent': agent_name,
            'flow_score': flow_score,
            'user_approved': user_approved,
            'verification_feedback': verification_feedback
        }

    def update_agent_selection_weights(self):
        """Normalize weights so they sum to 1.0."""
        total = sum(self.agent_selection_weights.values())
        for agent in self.agent_selection_weights:
            self.agent_selection_weights[agent] /= total

    def get_recommended_agent_sequence(self) -> List[str]:
        """Return [agents] sorted by selection weight."""
        sorted_agents = sorted(
            self.agent_selection_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [agent for agent, weight in sorted_agents]
```

#### Module: `orchestrator/learning/agent_coordination.py` (NEW)

**Agent Coordination Learning:**
```python
class AgentCoordination:
    """Learn which agents work well together."""

    def __init__(self):
        """Initialize coordination tracker."""
        self.agent_pair_effectiveness = {}  # (agent1, agent2) → float

    def record_pair_performance(self,
                               agent1: str,
                               agent2: str,
                               flow_score: float):
        """Record how well this pair worked."""
        pair_key = (agent1, agent2)
        if pair_key not in self.agent_pair_effectiveness:
            self.agent_pair_effectiveness[pair_key] = []

        self.agent_pair_effectiveness[pair_key].append(flow_score)

    def get_pair_score(self, agent1: str, agent2: str) -> float:
        """Get average effectiveness of this pair."""
        pair_key = (agent1, agent2)
        if pair_key not in self.agent_pair_effectiveness:
            return 0.5  # Neutral score for untested pairs

        scores = self.agent_pair_effectiveness[pair_key]
        return sum(scores) / len(scores)

    def recommend_agent_sequence(self, available_agents: list) -> list:
        """Recommend best agent sequence based on learned pairs."""
        # Use pair scores to order agents
        # Example: If (Planner, Verifier) scored 0.85,
        # and (Verifier, Executor) scored 0.78,
        # recommend: [Planner, Verifier, Executor, Generator]
```

#### Modified Pattern Recommender: `orchestrator/learning/pattern_recommender.py` (ENHANCED)

**Enhanced to track flow scores:**
```python
def score_pattern(self, pattern: dict, flow_score: float,
                  verification_feedback: dict, user_approved: bool) -> float:
    """Score pattern by: flow_score × verification × user_approval."""

    # Extract verification quality (0-1)
    verification_quality = len([
        f for f in verification_feedback.values() if f is True
    ]) / len(verification_feedback)

    # Calculate pattern score
    pattern_score = (
        flow_score * 0.4 +              # Flow quality
        verification_quality * 0.4 +    # Verification success
        (1.0 if user_approved else 0.0) * 0.2  # User approval
    )

    return pattern_score

def get_patterns_for_next_iteration(self) -> List[str]:
    """Return top-3 patterns for next iteration."""
    # Sort patterns by score (updated each iteration)
    top_patterns = sorted(
        self.pattern_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    return [pattern for pattern, score in top_patterns]
```

#### Integration into Agents: Agent Prompt Enhancement

**Each agent now receives:**
```python
# In agent system prompt:
context['recommended_patterns'] = recommender.get_patterns_for_next_iteration()

# Example in planner prompt:
f"""
You are planning for: {context['goal']}

Patterns that worked well in previous iterations:
{format_patterns(context['recommended_patterns'])}

Please incorporate these patterns if relevant to this iteration.
"""
```

#### Success Criteria for Phase 3:
- ✅ System learns which patterns improve quality
- ✅ Pattern recommendations update after each iteration
- ✅ Agent selection weights change based on flow scores
- ✅ Quality improves over iterations (measurable)

---

## System Integration Loop

### Memory ↔ Reasoning ↔ Learning Loop

After Phases 1-3, Project Jupiter implements a closed feedback loop:

```
┌─────────────────────────────────────────────────────────────┐
│                   Planning Iteration N                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. MEMORY PHASE                                             │
│     └─ Load relevant SegmentedMemory segments                │
│     └─ Retrieve top-3 memory chunks via semantic search      │
│     └─ Pass to agents: market research, past patterns, etc.  │
│                                                              │
│  2. REASONING PHASE                                          │
│     └─ Agents receive recommended patterns from learning     │
│     └─ Generate reasoning chains (PDDL style)                │
│     └─ Verify preconditions & effects                        │
│     └─ Collect verification feedback                         │
│                                                              │
│  3. LEARNING SIGNAL PHASE                                    │
│     └─ Calculate flow_score = verification × approval        │
│     └─ Update pattern effectiveness scores                   │
│     └─ Update agent selection weights                        │
│     └─ Train overwrite scores for SegmentedMemory            │
│                                                              │
│  4. CHECKPOINT & APPROVAL PHASE                              │
│     └─ Show user: reasoning chain + memory updates + quality │
│     └─ User approves/rejects                                 │
│     └─ If approved: Apply user feedback to memory & patterns │
│                                                              │
│  5. MEMORY UPDATE PHASE (on approval)                        │
│     └─ Add new iteration findings to memory                  │
│     └─ Compress old segments if needed                       │
│     └─ Update segment importance scores                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         Loop: N → N+1
                    With each iteration:
                    - Memory more relevant
                    - Patterns more effective
                    - Reasoning more rigorous
```

### Data Structures Supporting the Loop

**PlanningSession now tracks:**
```python
class PlanningSession:
    # Memory system (Phase 1)
    self.memory_manager = SegmentedMemory(max_segments=12)

    # Reasoning chains (Phase 2)
    self.reasoning_chains = {}  # iteration → reasoning_chain
    self.verification_feedback = {}  # iteration → feedback

    # Learning signals (Phase 3)
    self.iteration_signals = {}  # iteration → flow_score, approval
    self.pattern_scores = {}  # pattern_name → effectiveness_score
    self.agent_selection_weights = {}  # agent_name → weight

    # Loop data
    self.memory_deltas = []  # What changed in memory each iteration
    self.approved_patterns = []  # Patterns that passed user approval
```

---

## Implementation Phase Map

### Phase 1: MemAgent Memory System (Days 1-2)
**Files Created/Modified:**
- CREATE: `orchestrator/memory/memagent_memory.py` (SegmentedMemory class)
- MODIFY: `approval_gates.py` (PlanningSession integration)
- MODIFY: `llama_planner.py` (memory delta extraction)
- MODIFY: `simple_chatbox.py` (memory context usage)

**Success Metrics:**
- Memory bounded at 12 segments
- Semantic search working
- No regression in planning
- Token counting accurate

---

### Phase 2: PDDL-INSTRUCT Reasoning (Days 3-4)
**Files Created/Modified:**
- CREATE: `orchestrator/reasoning/logical_planner.py` (LogicalPlanningPrompt)
- CREATE: `orchestrator/reasoning/verification_feedback.py` (VerificationFeedback)
- MODIFY: `orchestrator/agents/planner_agent.py` (logical prompts)
- MODIFY: `orchestrator/agents/verifier_agent.py` (verification integration)
- MODIFY: `orchestrator/workflow_coordinator.py` (feedback collection)

**Success Metrics:**
- Reasoning chains in agent responses
- Verification feedback accurate
- Precondition checking working
- No performance regression

---

### Phase 3: Flow-GRPO Learning (Days 5-6)
**Files Created/Modified:**
- CREATE: `orchestrator/learning/flow_grpo_trainer.py` (FlowGRPOTrainer)
- CREATE: `orchestrator/learning/agent_coordination.py` (AgentCoordination)
- MODIFY: `orchestrator/learning_analyzer.py` (mid-iteration signals)
- MODIFY: `orchestrator/pattern_recommender.py` (flow_score tracking)
- MODIFY: All agents to use recommended patterns

**Success Metrics:**
- Flow scores calculated correctly
- Pattern recommendations improving
- Agent weights updating
- Learning signals driving quality improvement

---

### Phase 4: Integration (Days 7-8)
**Files Created/Modified:**
- CREATE: `orchestrator/integration/planning_loop.py` (IntegratedPlanningLoop)
- MODIFY: `simple_chatbox.py` (integrated execution flow)
- MODIFY: `context_manager.py` (enhanced checkpoint summaries)
- ADD ENDPOINT: `/api/checkpoint-details` (show reasoning trace)

**Success Metrics:**
- Loop executes without errors
- Memory updates on approval
- Patterns improve each iteration
- User can see decision-making process

---

### Phase 5: Testing & Validation (Days 9-10)
**Files Created/Modified:**
- CREATE: `tests/test_memagent_integration.py`
- CREATE: `tests/test_logical_reasoning.py`
- CREATE: `tests/test_flow_grpo.py`
- CREATE: `tests/test_integrated_loop.py`
- MODIFY: `tests/test_baseline.py` (ensure zero regressions)

**Success Metrics:**
- 22/22 baseline tests pass
- New integration tests pass
- Performance tests show learning
- Memory usage bounded

---

### Phase 6: Documentation & Alignment (NOW)
**Files Created/Modified:**
- CREATE: `RESEARCH_FRAMEWORK_ALIGNMENT.md` (this file)
- MODIFY: `CLAUDE.md` (MemAgent, PDDL, Flow-GRPO sections)
- MODIFY: `README.md` (learning, memory, monitoring sections)
- MODIFY: `user.md` (enhanced with system context)

**Success Metrics:**
- Clear "why" for all code changes
- Reference document for implementation
- Future developers understand research basis
- Code structure aligns with docs

---

## Key Principles

### Design Philosophy
1. **Research-First**: All code changes map to peer-reviewed research
2. **Backward Compatible**: No breaking changes to existing APIs
3. **Incremental Value**: Each phase provides immediate benefit
4. **Deep Integration**: Not bolted-on; woven through architecture
5. **Learning Enabled**: System improves with each iteration

### Quality Standards
- **No Regressions**: All 22 baseline tests pass throughout
- **Clear Feedback**: Users see reasoning, verification, learning
- **Measurable Improvement**: Track quality metrics each iteration
- **Bounded Complexity**: Memory fixed-size, learning signals sparse
- **Explainability**: Users understand WHY system made decisions

### Developer Experience
- Single responsibility per module
- Clear interfaces between phases
- Comprehensive test coverage
- Documentation explains research basis
- Easy to extend or modify

---

## Success Definition

**Phase 6 (Documentation-First) Success:**
✅ This document exists and is clear
✅ CLAUDE.md updated with research sections
✅ README.md has learning/memory sections
✅ Code structure is ready to implement

**Overall Project Success (After Phases 1-5):**
✅ Memory stays bounded at 12 segments
✅ Reasoning chains generated correctly
✅ Verification feedback identifies logic issues
✅ Flow-GRPO signals guide agent selection
✅ Patterns improve with each iteration
✅ User can see decision-making process
✅ Zero regressions (22/22 tests pass)
✅ Quality improves measurably over iterations

---

## References

**Research Papers:**
- MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent (ByteDance/Tsinghua, 2507.02259v1)
- PDDL-INSTRUCT: Teaching LLMs to Plan with Logical Chain-of-Thought Instruction Tuning (2509.13351v1)
- AgentFlow: Dynamic Agent Selection (lupantech, GitHub)

**Implementation Guidance:**
- See CLAUDE.md for code locations and integration points
- See README.md for running system and monitoring learning
- See individual module docstrings for implementation details

