# Fix Import Structure Plan

**Created:** 2025-12-01
**Issue:** `tax_app.py` fails to start with `No module named 'agent'`
**Priority:** High - blocks UI from running

---

## Problem Summary

The Streamlit UI (`tax_app.py`) cannot start because Python import paths don't match the actual directory structure. The codebase appears to have been reorganized without updating import statements.

---

## Current Directory Structure

```
PJJ-Tax&Legal/
├── orchestrator/
│   ├── tax_workflow/
│   │   ├── __init__.py
│   │   ├── frontend/
│   │   │   └── tax_app.py              ← ENTRY POINT (fails to import)
│   │   ├── logging_config.py           ← EXISTS here
│   │   ├── tax_orchestrator.py
│   │   ├── tax_planner_agent.py
│   │   ├── tax_searcher_agent.py
│   │   ├── tax_recommender_agent.py
│   │   ├── tax_compiler_agent.py
│   │   ├── tax_verifier_agent.py
│   │   └── tax_tracker_agent.py
│   └── (no __init__.py)
│
└── systemsettings_cache/
    └── system-technical-specs/
        └── agent/                       ← Agent module is HERE
            ├── __init__.py
            ├── agent.py
            ├── engine.py
            ├── fireworksscript.py
            ├── model.py
            ├── schemas.py
            ├── tools.py
            └── utils.py
```

---

## Import Problems

### In `tax_app.py` (lines 26-29):

```python
from agent import Agent                    # FAILS - agent not on path
from orchestrator.tax_workflow.tax_orchestrator import TaxOrchestrator
from agent.logging_config import ...       # FAILS - logging_config not in agent/
```

### In `tax_orchestrator.py` (lines 25-33):

```python
from agent import Agent
from orchestrator.agents.base_agent import BaseAgent, AgentResult  # FAILS - doesn't exist
from orchestrator.tax_workflow.tax_planner_agent import RequestCategorizer
# ... etc
from agent.logging_config import get_logger  # FAILS - wrong location
```

---

## Broken Import Map

| Import Statement | Expected Location | Actual Location | Fix Needed |
|-----------------|-------------------|-----------------|------------|
| `from agent import Agent` | `PJJ-Tax&Legal/agent/` | `PJJ-Tax&Legal/systemsettings_cache/system-technical-specs/agent/` | Path fix or move |
| `from agent.logging_config import ...` | `agent/logging_config.py` | `orchestrator/tax_workflow/logging_config.py` | Move file or change import |
| `from orchestrator.agents.base_agent import BaseAgent` | `orchestrator/agents/base_agent.py` | **DOES NOT EXIST** | Create or find missing file |
| `from orchestrator.tax_workflow...` | `orchestrator/__init__.py` | **MISSING** | Create `__init__.py` |

---

## Recommended Fix Options

### Option A: Restructure to Match Imports (Cleanest)

Move/copy files to match what the code expects:

1. Copy `systemsettings_cache/system-technical-specs/agent/` to `PJJ-Tax&Legal/agent/`
2. Copy `orchestrator/tax_workflow/logging_config.py` to `agent/logging_config.py`
3. Create `PJJ-Tax&Legal/orchestrator/__init__.py`
4. Find or create `orchestrator/agents/base_agent.py` with `BaseAgent` and `AgentResult` classes

### Option B: Update All Imports (More Changes)

Modify import statements in all Python files to match current structure:

1. Update `sys.path` in `tax_app.py` to include `systemsettings_cache/system-technical-specs/`
2. Change all `from agent.logging_config` to `from orchestrator.tax_workflow.logging_config`
3. Find where `BaseAgent`/`AgentResult` should come from and fix that import

### Option C: Hybrid (Recommended)

1. Create symlink or copy `agent/` to expected location
2. Move `logging_config.py` into the `agent/` package
3. Create missing `__init__.py` files
4. Investigate `base_agent.py` - may need to find original or create stub

---

## Missing Module: `base_agent.py`

The file `orchestrator/agents/base_agent.py` is imported but doesn't exist. It should define:

```python
class BaseAgent:
    # Base class for all agents
    pass

class AgentResult:
    # Result container for agent operations
    pass
```

**Action:** Search the original codebase or documentation for this file. It may have been accidentally omitted during reorganization.

---

## Quick Verification Steps

After fixing, verify with:

```bash
cd PJJ-Tax&Legal
python -c "from agent import Agent; print('agent OK')"
python -c "from agent.logging_config import get_logger; print('logging OK')"
python -c "from orchestrator.tax_workflow.tax_orchestrator import TaxOrchestrator; print('orchestrator OK')"
```

Then run the UI:

```bash
python -m streamlit run orchestrator/tax_workflow/frontend/tax_app.py --server.headless true
```

---

## Files That Need Changes

1. `PJJ-Tax&Legal/orchestrator/tax_workflow/frontend/tax_app.py` - lines 18-29
2. `PJJ-Tax&Legal/orchestrator/tax_workflow/tax_orchestrator.py` - lines 22-33
3. Possibly all agent files that import from `agent` or `orchestrator.agents`

---

## Notes

- The UI itself (Streamlit + Unicode/emojis) works fine on Windows 11 - verified with test app
- This is purely a Python import path / project structure issue
- The `agent` module at `systemsettings_cache/system-technical-specs/agent/` appears complete
- The knowledge base at `local-memory/tax_legal/` is separate and should be unaffected

---

## Contact

Plan created by Claude Code CLI session on Windows 11 laptop.
