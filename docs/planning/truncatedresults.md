# Tax Workflow Content Truncation & Display Fixes

## Problem Summary

**Critical Bug**: Content is truncated from full .md files → 3,000 chars (Agent code) → **200/150 chars** (formatting) → passed to synthesis, causing 100% hallucinations.

**Root Cause**: Lines 261 and 271 truncate to 200/150 characters, then frontend passes these tiny summaries to Llama instead of full content.

---

## Solution Overview

**Strategy**: Dual-field architecture
- `content`: Full 3,000 chars for synthesis (fixes hallucinations)
- `summary`: Short 250 chars for UI preview (clean user experience)

**Fixes Required**: 4 files, 5 phases, ~5-6 hours total

---

## Implementation Order

### Phase 1: Backend Data Structure (2-3 hours)

#### File 1: `orchestrator/tax_workflow/tax_searcher_agent.py`

**Line 188** - Agent code template:
```python
# Change from:
results.append({'source_file': filename, 'content': content[:3000], 'directory': root})

# To:
results.append({'source_file': filename, 'full_content': content[:3000], 'directory': root})
```

**Line 235** - Build results dict:
```python
# Change from:
"summary": result.get("content", "")[:3000],  # Redundant truncation

# To:
"content": result.get("full_content", ""),           # Full 3000 for synthesis
"summary": result.get("full_content", "")[:250],    # First 250 for display
```

**Line 261** - ⚠️ CRITICAL FIX (removes catastrophic truncation):
```python
# Change from:
"summary": result.get("summary", "")[:200],  # ← KILLS CONTENT

# To:
"content": result.get("content", ""),  # ← Full 3000 chars preserved
"summary": result.get("summary", ""),  # ← Already 250 from line 235
```

**Lines 410-415** - Fallback parser:
```python
# Add dual fields:
"content": content,        # Full 3000
"summary": content[:250],  # First 250
```

#### File 2: `orchestrator/tax_workflow/tax_recommender_agent.py`

**Line 197** - Agent code template:
```python
# Change from:
'content': content[:3000]

# To:
'full_content': content[:3000]
```

**Line 241** - Build results dict:
```python
# Change from:
"summary": result.get("content", "")[:3000],

# To:
"content": result.get("full_content", ""),
"summary": result.get("full_content", "")[:250],
```

**Line 271** - ⚠️ CRITICAL FIX:
```python
# Change from:
"summary": doc.get("summary", "")[:150]  # ← KILLS CONTENT

# To:
"content": doc.get("content", ""),  # ← Full 3000 chars
"summary": doc.get("summary", "")   # ← Already 250
```

**Lines 405-416** - Fallback parser:
```python
# Add dual fields:
"content": full_content,        # Full 3000
"summary": full_content[:250],  # First 250
```

**Test Phase 1**: Print `result.output` and verify both `content` (≤3000) and `summary` (≤250) exist

---

### Phase 2: Frontend Synthesis Fix (30 min)

#### File 3: `orchestrator/tax_workflow/frontend/tax_app.py`

**Line 447** - Step 5 compilation:
```python
# Change from:
file_contents[filename] = doc.get("summary", "")  # ← BUG: 250 chars

# To:
file_contents[filename] = doc.get("content", "")  # ← FIX: 3000 chars
```

**Line 481** - Step 6 verification:
```python
# Change from:
file_contents[filename] = doc.get("summary", "")

# To:
file_contents[filename] = doc.get("content", "")
```

**Line 511** - Step 6 citation:
```python
# Change from:
file_contents[filename] = doc.get("summary", "")

# To:
file_contents[filename] = doc.get("content", "")
```

**Test Phase 2**: Run full workflow, verify synthesis receives 3000-char content, hallucinations should reduce dramatically

---

### Phase 3: Frontend Content Display (1-2 hours)

**After Line 330** - Step 2 content preview (insert):
```python
if st.session_state.past_responses:
    # === NEW: CONTENT PREVIEW SECTION ===
    st.markdown("### 📄 Past Response Previews")
    st.markdown("*Preview the content of each past response before selecting*")

    for i, r in enumerate(st.session_state.past_responses):
        filename = r.get("filename", f"Response {i}")
        with st.expander(f"📄 {filename}", expanded=False):
            # Show clean text content (summary field = 250 chars)
            content = r.get("summary", "No content available")
            st.markdown("**Content Preview (first 250 characters):**")
            st.text(content)  # Clean text display, not JSON

            # Show metadata
            st.markdown("---")
            st.markdown(f"**Categories:** {', '.join(r.get('categories', []))}")
            st.markdown(f"**Date Created:** {r.get('date_created', 'Unknown')}")
            st.markdown(f"**Files Used:** {', '.join(r.get('files_used', []))}")
    # === END NEW SECTION ===

    # (Existing multiselect continues below)
```

**After Line 398** - Step 4 content preview (insert):
```python
if st.session_state.recommended_files:
    # === NEW: CONTENT PREVIEW SECTION ===
    st.markdown("### 📋 Document Previews")
    st.markdown("*Preview the content of each document before selecting*")

    for i, d in enumerate(st.session_state.recommended_files):
        filename = d.get("filename", f"Document {i}")
        with st.expander(f"📋 {filename}", expanded=False):
            # Show clean text content (summary field = 250 chars)
            content = d.get("summary", "No content available")
            st.markdown("**Content Preview (first 250 characters):**")
            st.text(content)  # Clean text display, not JSON

            # Show metadata
            st.markdown("---")
            st.markdown(f"**Category:** {d.get('category', 'Unknown')}")
            st.markdown(f"**Date Issued:** {d.get('date_issued', 'Unknown')}")
    # === END NEW SECTION ===

    # (Existing multiselect continues below)
```

**Test Phase 3**: UI shows expandable sections with clean text (not JSON)

---

### Phase 4: Directory Creation Fix (30 min)

#### File 4: `agent/system_prompt.txt`

**Line 90** - Comment out create_dir:
```python
# Change from:
create_dir(dir_path: str) -> bool

# To:
# create_dir(dir_path: str) -> bool  # DISABLED - Agent should only READ files
```

**Find and update available_functions** (search for file that builds this dict):
```bash
grep -r "available_functions" /Users/teije/Desktop/memagent-modular-fixed/PJJ-Tax&Legal/agent/
```

Then remove `create_dir` from the dictionary.

**Test Phase 4**:
```bash
ls -lat /Users/teije/Desktop/memagent-modular-fixed/local-memory/tax_legal/past_responses/ > /tmp/before.txt
# Run workflow
ls -lat /Users/teije/Desktop/memagent-modular-fixed/local-memory/tax_legal/past_responses/ > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
# Should show NO new directories
```

---

### Phase 5: Working Directory Fix (Optional - 30 min)

**Note**: `engine.py` already has working directory restoration at lines 54 and 164. Only add defensive enhancement if issues persist.

#### File 5: `agent/engine.py`

**Line 164-166** - Enhanced finally block:
```python
finally:
    # Restore original working directory
    try:
        os.chdir(original_cwd)
    except Exception as e:
        if log:
            logger.error(f"Failed to restore working directory: {e}")

    # Restore original builtins if they were modified
    if allowed_path:
        try:
            builtins.open = orig_open
            os.remove = orig_remove
            os.rename = orig_rename
        except:
            pass

    # DEFENSIVE: Double-check CWD restoration
    try:
        if os.getcwd() != original_cwd:
            os.chdir(original_cwd)
            if log:
                logger.warning(f"Required secondary CWD restoration to {original_cwd}")
    except Exception as e:
        if log:
            logger.error(f"Secondary CWD restoration failed: {e}")
```

---

## Success Criteria

**Functional**:
- [ ] Step 2 returns both `content` (≤3000) and `summary` (≤250)
- [ ] Step 4 returns both `content` (≤3000) and `summary` (≤250)
- [ ] Synthesis receives 3000-char content (not 150-250 char summary)
- [ ] UI shows expandable content previews after Steps 2 & 4
- [ ] Content previews are clean text (not JSON)

**Quality**:
- [ ] Final synthesis contains ZERO hallucinations
- [ ] Citations point to actual content in source documents
- [ ] Verification passes with >80% claims verified

**Infrastructure**:
- [ ] No Streamlit working directory errors
- [ ] No unwanted directories created in past_responses/
- [ ] Full workflow completes without crashes

---

## Critical Files

1. **`orchestrator/tax_workflow/tax_searcher_agent.py`** - Lines 188, 235, 261, 410-415
2. **`orchestrator/tax_workflow/tax_recommender_agent.py`** - Lines 197, 241, 271, 405-416
3. **`orchestrator/tax_workflow/frontend/tax_app.py`** - Lines 330 (insert), 398 (insert), 447, 481, 511
4. **`agent/system_prompt.txt`** - Line 90 (comment out create_dir)
5. **Find file with `available_functions` dict** - Remove create_dir entry

---

## Troubleshooting

**Issue**: Backend still returns truncated content
→ Check lines 261 & 271 - ensure [:200] and [:150] are completely removed

**Issue**: UI doesn't show previews
→ Check indentation of new expandable sections

**Issue**: Synthesis still hallucinating
→ Check lines 447, 481, 511 use `doc.get("content")` not `doc.get("summary")`

**Issue**: Directories still being created
→ Verify create_dir is removed from both system_prompt.txt and available_functions dict
