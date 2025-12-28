# Phase 3 Feature 1: Natural Conversation MemAgent Integration
## (Aligned with CODEBASE_ANALYSIS_AND_STRATEGY Option 4 + Your Natural Conversation Philosophy)

---

## CRITICAL ALIGNMENT

**Strategy Document Says**: Feature 1 = 2-3 days for chat with memory commands
**Your Feedback Says**: No commands—natural conversation, just like original MCP with Claude

**Solution**: Use natural conversation approach within the 2-3 day timeline. The operations are identical; only the UX changes (command syntax → natural language intent detection).

---

## WHAT WE'RE BUILDING

### Goal
Users chat naturally about their plans. The system:
1. **Automatically detects memory operations** from natural language (no `/commands`)
2. **Retrieves relevant context** when users ask questions
3. **Stores insights** when appropriate without user prompting
4. **Maintains planning context awareness** (knows current plan, entities, memory scope)

### Architecture (Aligns with Option 4)
```
Streamlit Chat Tab (Already exists)
    ↓
IntegratedOrchestrator.chat_with_plan()
    ↓
[ChatIntentClassifier]
  - Detects: retrieve, store, query, or just chat
  - Lightweight rule-based (fast, 80% accuracy)
    ↓
[MemAgent Context Retrieval]
  - If retrieve intent: Query SegmentedMemory
  - Semantic search via existing memagent-modular-fixed system
  - Inject context into LLM prompt
    ↓
[Fireworks LLM Call]
  - User message + planning context + memory context
  - Llama generates natural response
  - NO awareness of memory operations
    ↓
[Smart Auto-Storage]
  - Response contains valuable insight?
  - Store to MemAgent automatically
  - Track what was stored in metadata
    ↓
[Response to Streamlit]
  - Natural response
  - Memory operations summary (subtle, in expander)
  - All context available for next message
```

---

## IMPLEMENTATION PLAN (2-3 Days)

### Day 1: Intent Classifier + Memory Retrieval
**What**: Build the decision layer that detects what user wants

**Deliverables**:
1. `ChatIntentClassifier` class
   - Input: user message
   - Output: `{'intent': 'retrieve'|'store'|'query'|'chat', 'entities': [...], 'confidence': 0.0-1.0}`
   - Uses keywords + optional lightweight LLM (fallback)

2. Memory retrieval integration
   - Connect to existing `SegmentedMemory.semantic_search()`
   - Retrieve top 3 relevant segments
   - Format for LLM context injection

3. Planning context manager
   - Track current plan, goal, entities, scope
   - Pass to LLM in system prompt

**Testing**: 5 sample conversations (retrieve, store, query, chat)

---

### Day 2: LLM Integration + Auto-Storage
**What**: Wire the LLM and implement smart storage

**Deliverables**:
1. Enhanced `chat_with_plan()` method
   - Takes: user_message, planning_context, memory_scope
   - Classifies intent
   - Retrieves context if needed
   - Calls Fireworks with enhanced prompt
   - Receives response

2. Smart auto-storage
   - Analyze LLM response for insights
   - Score importance (0-1)
   - Auto-store if score > 0.6
   - Track stored items in metadata

3. Response formatting
   ```python
   {
       'response': '<Full LLM response>',
       'memory_operations': {
           'retrieved': [...],  # What was retrieved
           'stored': [...]      # What was auto-stored
       },
       'planning_context': {...}
   }
   ```

**Testing**: End-to-end tests with sample conversations

---

### Day 3: Streamlit Integration + Polish
**What**: Connect to UI and ensure smooth experience

**Deliverables**:
1. Update `app.py` chat interface (minimal changes)
   - Call `orchestrator.chat_with_plan()` instead of current chat
   - Pass planning context
   - Display response naturally
   - Optional expander for memory operations

2. Memory operation summaries
   - Show what was retrieved/stored
   - Format: "✓ Retrieved Q3 insights (85% match)"
   - Format: "✓ Stored new market framework"

3. Testing & debugging
   - Chat with current plan
   - Verify memory context is relevant
   - Verify auto-storage works correctly

---

## CODE STRUCTURE

### New Class: ChatIntentClassifier

```python
class ChatIntentClassifier:
    """Detects memory operations from natural language"""

    RETRIEVE_KEYWORDS = [
        "remember", "previous", "past", "did we",
        "what do we know", "insights about", "learned"
    ]
    STORE_KEYWORDS = [
        "save this", "remember this", "note",
        "keep in mind", "capture", "should remember"
    ]
    QUERY_KEYWORDS = [
        "search", "find", "look up", "recommendations"
    ]

    def classify(self, message: str) -> Dict:
        """Returns {'intent': str, 'confidence': float, 'entities': list}"""
        # Check keywords first (fast path)
        for keyword in self.RETRIEVE_KEYWORDS:
            if keyword in message.lower():
                return {
                    'intent': 'retrieve',
                    'confidence': 0.85,
                    'entities': self._extract_entities(message)
                }

        for keyword in self.STORE_KEYWORDS:
            if keyword in message.lower():
                return {
                    'intent': 'store',
                    'confidence': 0.85,
                    'entities': []
                }

        # Default to chat
        return {'intent': 'chat', 'confidence': 1.0, 'entities': []}
```

### Enhanced chat_with_plan() in IntegratedOrchestrator

```python
def chat_with_plan(
    self,
    user_message: str,
    planning_context: Dict,
    memory_scope: str = "both"
) -> Dict:
    """
    Chat naturally about a plan with optional memory integration.

    planning_context = {
        'goal': str,
        'plan': str,
        'entities': List[str],
        'frameworks': List[str]
    }
    """
    # 1. Classify intent
    intent = self.intent_classifier.classify(user_message)

    # 2. Retrieve context if needed
    memory_context = ""
    if intent['intent'] in ['retrieve', 'query']:
        segments = self.segmented_memory.semantic_search(
            query=' '.join(intent['entities']) or user_message,
            scope=memory_scope,
            top_k=3
        )
        memory_context = self._format_segments(segments)

    # 3. Build enhanced prompt
    system_prompt = f"""You are discussing a strategic plan.

Plan Goal: {planning_context['goal']}
Current Plan: {planning_context['plan'][:2000]}...
Memory Scope: {memory_scope}
Entities Used: {', '.join(planning_context['entities'])}

{f'Relevant Memory Context:{memory_context}' if memory_context else ''}

Respond naturally to the user's message."""

    # 4. Call LLM
    from agent.agent import Agent
    agent = Agent(memory_path=str(self.memory_path_user))
    response = agent.chat(
        f"{system_prompt}\n\nUser: {user_message}"
    )

    # 5. Auto-store if valuable
    stored_items = []
    if self._is_valuable_insight(response):
        self.segmented_memory.add_segment(
            content=response,
            source=f"chat_insight_{planning_context['plan_id']}",
            importance_score=0.75,
            semantic_tags=['chat', 'insight']
        )
        stored_items.append({'content': response[:100], 'tags': ['chat', 'insight']})

    # 6. Format response
    return {
        'response': response,
        'memory_operations': {
            'retrieved': [s.to_dict() for s in segments] if memory_context else [],
            'stored': stored_items
        }
    }
```

### Streamlit Integration (Minimal)

```python
# In app.py chat section (replace current chat code)

st.markdown("### 💬 Chat with Your Plan")

current_plan = st.session_state.get('current_plan', {})
if not current_plan:
    st.info("Generate a plan first, then chat about it here.")
else:
    user_input = st.chat_input("Ask about your plan...")

    if user_input:
        response = st.session_state.orchestrator.chat_with_plan(
            user_message=user_input,
            planning_context={
                'goal': current_plan.get('goal', ''),
                'plan': current_plan.get('content', ''),
                'plan_id': current_plan.get('id', ''),
                'entities': current_plan.get('selected_entities', []),
                'frameworks': current_plan.get('metadata', {}).get('frameworks_used', [])
            },
            memory_scope=current_plan.get('memory_scope', 'both')
        )

        # Display response
        st.markdown(response['response'])

        # Show memory operations (optional)
        if response['memory_operations']['retrieved'] or response['memory_operations']['stored']:
            with st.expander("📚 Memory Context"):
                if response['memory_operations']['retrieved']:
                    st.caption("**Retrieved:**")
                    for item in response['memory_operations']['retrieved']:
                        st.write(f"✓ {item['source']}")

                if response['memory_operations']['stored']:
                    st.caption("**Stored to Memory:**")
                    for item in response['memory_operations']['stored']:
                        st.write(f"✓ {item['tags']}")
```

---

## TIMELINE (Aligns with Option 4)

| Day | Task | Effort |
|---|---|---|
| **Day 1** | ChatIntentClassifier + memory retrieval | Full day |
| **Day 2** | LLM integration + auto-storage logic | Full day |
| **Day 3** | Streamlit integration + testing + polish | Full day |
| **Reserve** | Buffer for debugging/refinement | 0.5 days |

**Total: 2.5-3 days** ✅ Matches strategy document estimate

**Combined Project Timeline:**
- Phase 1 (Adapter): ✅ 4-6 hours (DONE)
- Phase 2 (Streamlit): ✅ 1-2 hours (DONE)
- **Phase 3 Feature 1 (Chat)**: 2-3 days (THIS PLAN)
- **Phase 3 Feature 2 (Memory)**: ✅ 2-3 days (DONE in Phase 2)
- Testing & polish: 1-2 days

**Total: 4-6 days** ✅ Matches Option 4 estimate

---

## KEY DIFFERENCES FROM ORIGINAL STRATEGY DOCUMENT

| Aspect | Strategy Doc | This Plan |
|--------|---|---|
| **Approach** | Command-based (`/store`, `/retrieve`) | Natural conversation (intent detection) |
| **User Experience** | "Remember this is a command" | "Chat naturally, system handles memory" |
| **Philosophy** | Tool-like (explicit operations) | Agent-like (transparent operations) |
| **MCP Alignment** | ❌ Violates original | ✅ Emulates original |
| **Timeline** | 2-3 days ✅ | 2-3 days ✅ |
| **Memory Operations** | Same (API calls) | Same (API calls) |
| **Complexity** | Intent == syntax validation | Intent == keyword + optional LLM |

---

## WHAT YOU GET AT EACH MILESTONE

**End of Day 1:**
- ✅ ChatIntentClassifier works
- ✅ Memory retrieval integrated
- ✅ Planning context flows through system
- ✅ Can test intent detection manually

**End of Day 2:**
- ✅ Full end-to-end chat working
- ✅ Auto-storage detects valuable insights
- ✅ Response format includes memory operations
- ✅ Can test with actual plans

**End of Day 3:**
- ✅ Streamlit chat tab fully functional
- ✅ Natural conversation about plans
- ✅ Memory context retrieved automatically
- ✅ Insights stored without user actions
- ✅ Full integration testing complete

**Launch Ready:**
- ✅ System: Streamlit + memagent-fixed hybrid (proven quality)
- ✅ Chat: Natural conversation with transparent memory
- ✅ Memory: Private/shared enforcement + scope control
- ✅ Planning: Human-in-the-loop with approval gates
- ✅ Learning: Flow-GRPO improving with iterations

---

## NEXT STEPS

When ready to implement:
1. Review this plan
2. Begin Day 1 implementation
3. Test intent classifier with sample messages
4. Iterate based on testing feedback
