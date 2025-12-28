# Comprehensive Fix Plan: Tax Workflow System

**Status**: Ready for Implementation
**Context**: System test run revealed critical issues - 0 results, empty synthesis, broken human-in-the-loop
**User Requirements**: MemAgent should do SEMANTIC extraction based on query, NEVER auto-reject, human makes ALL decisions

---

## MemAgent Architecture Understanding

### Key Finding: MemAgent is a File Navigator, NOT a Semantic Search Engine

After analyzing the core MemAgent code (`agent/tools.py`, `agent/agent.py`, `agent/system_prompt.txt`):

**Available Tools:**
- `read_file(path)` → Returns entire file content
- `list_files()` → Lists files in current directory
- `os.chdir()` → Navigate directories (standard Python)

**No Built-in Semantic Search.** The "semantic" part must come from the LLM (Llama 3.3 70B) writing intelligent Python code that:
1. Reads file contents
2. Analyzes them against the user's query
3. Extracts relevant sections (not blind slicing)

### The Problem

Current prompts explicitly tell the LLM: `content[:3000]` (blindly take first 3000 chars)

This overrides the LLM's ability to do intelligent extraction. Instead, prompts should:
1. Pass the user's query
2. Ask the LLM to write code that extracts query-relevant sections
3. Let the LLM decide what's relevant (using keyword matching, semantic understanding)

---

## Executive Summary

After comprehensive investigation and user input, the following fixes are needed:

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Past response search returns 0 results | Query not passed to Agent | Pass full query for semantic matching |
| Content extraction is positional | `content[:3000]` blindly slices | Semantic extraction based on query |
| Preview shows only YAML metadata | `summary[:250]` captures headers | MemAgent selects key info semantically |
| Empty synthesis output | No content reaching compiler | Fixed by Issues 1-3 |
| No human review | Auto-verification rejects output | Remove auto-rejection, add draft review |

---

## Phase 1: Fix Search Agents to Pass Full Query

### Files to Modify:
- `/Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/tax_searcher_agent.py`
- `/Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/tax_recommender_agent.py`

### Current Problem (tax_searcher_agent.py lines 158-183):
```python
constrained_query = f"""You MUST respond with ONLY these sections:
<python>
# REQUIREMENTS (write Python code to implement these):
# 2. Set category_dirs to: {absolute_category_dirs!r}
# 3. For each dir in category_dirs:
#    - 'content' should be content[:3000] (first 3000 chars)  ← WRONG: No query, positional slicing
</python>
"""
```

The `{request}` variable exists but is NOT in the prompt.

### Fix: Pass Full Query + Semantic Extraction Instructions

```python
constrained_query = f"""You MUST respond with ONLY these sections:

<think>
[Your plan to search these directories for content relevant to the user's query]
</think>

<python>
# USER'S QUERY (search for content relevant to this):
# "{request}"
#
# DIRECTORIES TO SEARCH:
# {absolute_category_dirs!r}
#
# REQUIREMENTS:
# 1. Create empty 'results' list
# 2. For each directory, use os.walk() to find all .md files
# 3. For each .md file:
#    a. Read full content with read_file()
#    b. Skip YAML front matter (content between first --- and second ---)
#    c. Search for paragraphs/sections that relate to the user's query
#    d. Extract RELEVANT sections (not just first N chars)
#    e. If relevant content found, append to results:
#       - 'source_file': filename
#       - 'directory': full path
#       - 'content': the relevant section(s) up to 3000 chars
#       - 'relevance': brief explanation of why this is relevant
#
# IMPORTANT: Extract content that ANSWERS the query, not just first 3000 characters
# Use keyword matching and semantic understanding to find relevant sections
#
# Write executable Python code:
</python>

CRITICAL: Your code must create a 'results' variable with relevant content for the query."""
```

### Changes Summary:
- Line 158-183: Replace prompt with new query-aware prompt
- Line 244: Change `"summary": full_text[:250]` to use extracted relevance/summary
- Apply identical changes to `tax_recommender_agent.py` lines 167-193

---

## Phase 2: Implement True Semantic Extraction

### Current Behavior:
Agent is told: "extract `content[:3000]`" - blind positional slicing that includes YAML headers

### New Behavior:
Agent should:
1. Skip YAML front matter
2. Search for paragraphs containing query-relevant keywords
3. Extract those sections (preserving paragraph boundaries)
4. Return up to 3000 chars of RELEVANT content

### Helper Function to Add (both search agents):

```python
def _create_semantic_extraction_prompt(self, request: str, directories: List[str]) -> str:
    """Create prompt that instructs Agent to extract relevant content semantically."""
    return f"""You MUST respond with ONLY these sections:

<think>
[Your plan to find documents and extract content relevant to the query]
</think>

<python>
import os
import re

# The user's query - find content that helps answer this:
query = '''{request}'''

# Directories to search:
category_dirs = {directories!r}

results = []

def skip_yaml_frontmatter(text):
    '''Remove YAML front matter from markdown content'''
    if text.startswith('---'):
        end_marker = text.find('---', 3)
        if end_marker != -1:
            return text[end_marker + 3:].strip()
    return text

def extract_relevant_sections(content, query, max_chars=3000):
    '''Extract paragraphs that mention keywords from the query'''
    # Get query keywords (words > 3 chars)
    keywords = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 3]

    # Split into paragraphs
    paragraphs = content.split('\\n\\n')

    relevant = []
    total_chars = 0

    for para in paragraphs:
        para_lower = para.lower()
        # Check if paragraph mentions any keywords
        if any(kw in para_lower for kw in keywords):
            if total_chars + len(para) <= max_chars:
                relevant.append(para)
                total_chars += len(para)

    # If no keyword matches, return first 3000 chars as fallback
    if not relevant:
        return content[:max_chars]

    return '\\n\\n'.join(relevant)

for dir_path in category_dirs:
    if not os.path.exists(dir_path):
        continue
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            if filename.endswith('.md'):
                try:
                    os.chdir(root)
                    content = read_file(filename)
                    if len(content) > 50:
                        # Skip YAML and extract relevant content
                        clean_content = skip_yaml_frontmatter(content)
                        relevant_content = extract_relevant_sections(clean_content, query)

                        if relevant_content:
                            results.append({{
                                'source_file': filename,
                                'directory': root,
                                'content': relevant_content,
                                'full_path': os.path.join(root, filename)
                            }})
                except Exception as e:
                    pass  # Skip files that can't be read

# results now contains semantically extracted content
</python>

CRITICAL: Your <python> section must contain executable code that creates 'results'."""
```

---

## Phase 3: Fix Preview Display

### Current Problem:
```python
"summary": full_text[:250]  # Shows only YAML front matter
```

### Fix:
The `summary` field should contain the Agent's extracted relevant content (or first 250 chars of it):

```python
# In result extraction (lines 238-248):
for result in raw_results:
    if isinstance(result, dict):
        content = result.get("content", "")  # Already semantically extracted
        past_responses.append({
            "filename": result.get("source_file", "Unknown"),
            "content": content,  # Full relevant content for synthesis
            "summary": content[:250] if content else "No relevant content found",  # Preview of relevant content
            "full_path": result.get("full_path", ""),
            "categories": categories,
        })
```

Since Phase 2 extracts RELEVANT content, the summary will show relevant content preview (not YAML).

---

## Phase 4: DELETE Verifier & Add Draft Review

### User Requirement:
- "Never ever have any auto rejection at any steps"
- "I want to see the draft before the final synthesis"
- "Verification step is not really needed - the human should be verifying"
- **"Just delete the verifier part, its currently not necessary"**

### Files to Modify:
- `/Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/frontend/tax_app.py`
- `/Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/tax_orchestrator.py`
- `/Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/tax_verifier_agent.py` → **DELETE**
- `/Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/tax_tracker_agent.py` → Keep for citations only

### Changes:

#### A. DELETE tax_verifier_agent.py

```bash
# Delete the file entirely
rm /Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax-Legal/orchestrator/tax_workflow/tax_verifier_agent.py
```

#### B. Remove verifier imports and calls from tax_orchestrator.py

```python
# REMOVE these lines:
from orchestrator.tax_workflow.tax_verifier_agent import DocumentVerifier
self.verifier = DocumentVerifier(agent, memory_path)
verifier_result = self.verifier.generate(...)
```

#### B. Add Draft Review Step in tax_app.py

Current flow:
```
Step 5: Select Documents → Step 6: Synthesize + Verify + Cite → Show Final
```

New flow:
```
Step 5: Select Documents
  → Step 6a: Generate Draft → Show Draft → User Approves
  → Step 6b: Show Final (no verification, just format citations)
```

**Implementation in tax_app.py**:

```python
# After Step 5 (document selection), before final synthesis:

# === STEP 6A: DRAFT GENERATION ===
if st.session_state.workflow_step == "draft_review":
    st.header("Step 6a: Review Draft Response")

    # Generate draft
    if "draft_response" not in st.session_state:
        draft_result = orchestrator.generate_draft(
            request=st.session_state.user_request,
            selected_contents=st.session_state.selected_file_contents,
            categories=st.session_state.confirmed_categories
        )
        st.session_state.draft_response = draft_result.get("draft", "")

    # Display draft
    st.subheader("Draft KPMG Memorandum")
    st.markdown(st.session_state.draft_response)

    # User controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve Draft - Proceed to Final"):
            st.session_state.workflow_step = "final_output"
            st.rerun()
    with col2:
        if st.button("🔄 Regenerate Draft"):
            del st.session_state.draft_response
            st.rerun()

# === STEP 6B: FINAL OUTPUT ===
if st.session_state.workflow_step == "final_output":
    st.header("Step 6b: Final Response")

    # Format with citations (no verification)
    final_result = orchestrator.format_final_response(
        draft=st.session_state.draft_response,
        sources=st.session_state.selected_file_contents
    )

    st.subheader("KPMG Tax Memorandum")
    st.markdown(final_result.get("response", ""))

    # Show source documents used
    st.subheader("Source Documents Referenced")
    for filename, content in st.session_state.selected_file_contents.items():
        with st.expander(filename):
            st.text(content[:500] + "..." if len(content) > 500 else content)
```

---

## Phase 5: Update Workflow States in tax_app.py

### Current States:
```python
workflow_steps = ["input", "categories", "past_responses", "recommendations", "synthesis"]
```

### New States:
```python
workflow_steps = [
    "input",           # User enters question
    "categories",      # Confirm tax categories
    "past_responses",  # Search & select past responses (Step 2-3)
    "recommendations", # Search & select tax docs (Step 4-5)
    "draft_review",    # NEW: Review draft before final (Step 6a)
    "final_output"     # Final formatted response (Step 6b)
]
```

---

## Implementation Order

1. **Phase 1**: Fix search prompts to include query (both agents)
2. **Phase 2**: Implement semantic extraction in prompts
3. **Phase 3**: Update summary/preview field creation
4. **Phase 4A**: Remove/disable verifier auto-rejection
5. **Phase 4B**: Add draft review step in UI
6. **Phase 5**: Update workflow states

---

## Files to Modify Summary

| File | Changes |
|------|---------|
| `tax_searcher_agent.py` | Lines 158-183: New semantic prompt with query; Lines 238-248: Update extraction |
| `tax_recommender_agent.py` | Lines 167-193: New semantic prompt with query; Lines 229-240: Update extraction |
| `tax_app.py` | Add draft_review step; Remove verification display; Update workflow states |
| `tax_orchestrator.py` | Remove verifier import and calls; Simplify Step 6 |
| `tax_verifier_agent.py` | **DELETE ENTIRELY** |
| `tax_tracker_agent.py` | Keep for citations (optional, may simplify later) |

---

## Expected Outcome After Fixes

1. **Search returns results**: Agent knows what to search for (receives query)
2. **Content is relevant**: Agent extracts query-matching sections (not first N chars)
3. **Preview shows content**: No YAML in preview, actual relevant text shown
4. **Synthesis works**: Compiler receives actual content (not empty)
5. **Human in control**: Draft shown before final, no auto-rejection, user verifies

---

## Testing Plan

After implementation:
1. Run same query: "What conditions must be satisfied to apply 0% VAT on exported software services?"
2. Verify: Past responses found (not 0)
3. Verify: Preview shows relevant content (not YAML)
4. Verify: Draft shown before final synthesis
5. Verify: No auto-rejection messages
6. Verify: Final output is a proper KPMG memo with citations
