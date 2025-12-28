# Codebase Refactor Plan: Option 1 (Standard Src Layout)

**Status**: PLANNED (Not Yet Implemented)
**Risk Level**: HIGH
**Estimated Time**: 6-8 hours
**Created**: December 8, 2025

---

## Proposed Directory Structure (With Descriptions)

```
pjj-tax-legal/                              # Root directory (kebab-case, professional naming)
│
├── src/                                    # Source code directory (Python packaging standard)
│   └── pjj_tax_legal/                      # Main Python package (snake_case for imports)
│       ├── __init__.py                     # Package initializer, exports main classes
│       │
│       ├── agent/                          # Core MemAgent system (LLM-powered file navigator)
│       │   ├── __init__.py                 # Exports: Agent class
│       │   ├── agent.py                    # Main Agent class - orchestrates LLM interactions
│       │   ├── engine.py                   # Sandboxed Python code execution engine
│       │   ├── model.py                    # Fireworks API client for Llama 3.3 70B
│       │   ├── schemas.py                  # Pydantic models: AgentResponse, ChatMessage, etc.
│       │   ├── settings.py                 # Configuration: API keys, model settings, paths
│       │   ├── tools.py                    # File I/O tools: read_file, list_files, etc.
│       │   ├── utils.py                    # Helper functions: memory creation, prompts
│       │   └── logging_config.py           # Centralized logging setup with rotation
│       │
│       └── orchestrator/                   # Tax workflow orchestration system
│           ├── __init__.py                 # Exports: TaxOrchestrator, all agents
│           │
│           ├── base/                       # Base classes for all agents
│           │   ├── __init__.py             # Exports: BaseAgent, AgentResult
│           │   └── base_agent.py           # Abstract base class with shared agent logic
│           │
│           └── tax_workflow/               # Tax-specific workflow agents
│               ├── __init__.py             # Exports: All 6 tax workflow agents
│               ├── orchestrator.py         # Main workflow controller (6-step pipeline)
│               ├── planner.py              # Step 1: Categorize tax requests (RequestCategorizer)
│               ├── searcher.py             # Step 2: Search past responses (TaxResponseSearcher)
│               ├── recommender.py          # Step 4: Search tax database (FileRecommender)
│               ├── compiler.py             # Step 5: Synthesize KPMG-format response
│               └── tracker.py              # Step 6: Track citations and sources
│
├── apps/                                   # Application entry points
│   └── tax_assistant.py                    # Streamlit web UI for tax advisory system
│
├── data/                                   # Data files (gitignored except structure)
│   └── tax_legal/                          # Primary data directory for tax system
│       ├── tax_database/                   # 3,400+ Vietnamese tax regulation documents
│       │   ├── 01_CIT/                     # Corporate Income Tax regulations
│       │   ├── 02_VAT/                     # Value Added Tax regulations
│       │   ├── 03_Customs/                 # Customs regulations
│       │   ├── 04_PIT/                     # Personal Income Tax regulations
│       │   ├── 05_DTA/                     # Double Taxation Agreements
│       │   ├── 06_Transfer_Pricing/        # Transfer Pricing regulations
│       │   ├── 07_FCT/                     # Foreign Contractor Tax regulations
│       │   ├── 08_Tax_Administration/      # Tax Administration procedures
│       │   └── ... (18 categories total)   # See CATEGORY_DIR_MAP in recommender.py
│       │
│       ├── past_responses/                 # 27 approved KPMG tax advisory memos
│       │   ├── 01_CIT/                     # Past CIT responses
│       │   ├── 02_VAT/                     # Past VAT responses
│       │   └── ... (18 categories)         # Organized by tax category
│       │
│       └── entities/                       # Runtime data (sessions, coordination logs)
│           ├── sessions/                   # User session state (JSON files)
│           └── agent_coordination.md       # Agent activity log
│
├── docs/                                   # Documentation
│   ├── current/                            # Active planning documents
│   │   ├── MEMAGENT_JOURNEY.md             # Architecture discovery documentation
│   │   ├── REFACTOR_PLAN_OPTION1.md        # This file
│   │   └── ...
│   ├── archive/                            # Historical/resolved documentation
│   └── technical/                          # Technical specifications
│
├── logs/                                   # Application logs
│   └── tax_app.log                         # Rotating log file (10MB max, 7 backups)
│
├── tests/                                  # Test suite (future)
│   ├── __init__.py
│   ├── test_agent.py                       # Agent unit tests
│   └── test_orchestrator.py                # Orchestrator integration tests
│
├── .archive/                               # Archived/deprecated code (gitignored)
│   ├── old_planning_system/                # Previous planning implementation
│   └── extraction_scripts/                 # Database extraction tools
│
├── .streamlit/                             # Streamlit configuration
│   └── config.toml                         # Theme, server settings
│
├── .env.example                            # Environment variables template
├── .gitignore                              # Git ignore rules
├── pyproject.toml                          # Python package configuration (PEP 517/518)
├── requirements.txt                        # Dependencies (or use pyproject.toml only)
└── README.md                               # Project overview and setup instructions
```

---

## Current Directory Structure (For Reference)

```
memagent-modular-fixed/                     # Current root (non-descriptive name)
│
├── PJJ-Tax-Legal/                          # Main code directory
│   ├── agent/                              # Core MemAgent system
│   │   ├── __init__.py
│   │   ├── agent.py                        # Main Agent class
│   │   ├── engine.py                       # Code execution engine
│   │   ├── fireworksscript.py              # Standalone Fireworks test (can be deleted)
│   │   ├── logging_config.py               # Logging setup
│   │   ├── model.py                        # LLM API client
│   │   ├── schemas.py                      # Data models
│   │   ├── settings.py                     # Configuration
│   │   ├── tools.py                        # File I/O tools
│   │   └── utils.py                        # Helper functions
│   │
│   ├── orchestrator/                       # Workflow system
│   │   ├── __init__.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   └── base_agent.py               # Base class
│   │   │
│   │   └── tax_workflow/
│   │       ├── __init__.py
│   │       ├── frontend/
│   │       │   └── tax_app.py              # Streamlit UI (buried deep!)
│   │       ├── tax_compiler_agent.py
│   │       ├── tax_orchestrator.py
│   │       ├── tax_planner_agent.py
│   │       ├── tax_recommender_agent.py
│   │       ├── tax_searcher_agent.py
│   │       └── tax_tracker_agent.py
│   │
│   ├── streamlit_instance_info/            # Runtime logs (poorly named)
│   │   └── logs/
│   │       └── tax_app.log
│   │
│   └── systemsettings_cache/               # Contains .venv (should not be here!)
│       └── system-technical-specs/
│           └── .venv/                      # Virtual env should be at root
│
├── local-memory/                           # Data directory (non-standard name)
│   └── tax_legal/
│       ├── tax_database/                   # 3,400+ documents
│       ├── past_responses/                 # 27 memos
│       └── entities/                       # Runtime data
│
├── claudecodedocs_MD/                      # Documentation (awkward name)
│   ├── planningcurrent/
│   ├── pasterrors/
│   └── technical/
│
├── Old/                                    # Archived code (visible, should be hidden)
│
├── database-extraction-old/                # More archived code
│
├── .git/                                   # Git repository
├── README.md
├── Codebasecleanup.md
└── WINDOWS-COMPATIBILITY-FIXES.md
```

---

## Side-by-Side Comparison

```
CURRENT                                    PROPOSED
═══════════════════════════════════════    ═══════════════════════════════════════

memagent-modular-fixed/                    pjj-tax-legal/
├── PJJ-Tax-Legal/                         ├── src/
│   ├── agent/                 ─────────►  │   └── pjj_tax_legal/
│   │   └── [9 files]                      │       ├── agent/
│   │                                      │       │   └── [9 files]
│   └── orchestrator/          ─────────►  │       │
│       ├── agents/                        │       └── orchestrator/
│       │   └── base_agent.py              │           ├── base/
│       │                                  │           │   └── base_agent.py
│       └── tax_workflow/                  │           │
│           ├── frontend/                  │           └── tax_workflow/
│           │   └── tax_app.py ─────────►  │               └── [6 renamed files]
│           └── [6 agent files]            │
│                                          ├── apps/
│                                          │   └── tax_assistant.py ◄── (from frontend/)
│                                          │
├── local-memory/              ─────────►  ├── data/
│   └── tax_legal/                         │   └── tax_legal/
│       ├── tax_database/                  │       ├── tax_database/
│       ├── past_responses/                │       ├── past_responses/
│       └── entities/                      │       └── entities/
│                                          │
├── claudecodedocs_MD/         ─────────►  ├── docs/
│   ├── planningcurrent/                   │   ├── current/
│   ├── pasterrors/                        │   ├── archive/
│   └── technical/                         │   └── technical/
│                                          │
├── Old/                       ─────────►  ├── .archive/  (hidden)
├── database-extraction-old/   ─────────►  │
│                                          │
│                                          ├── logs/
│                                          │   └── tax_app.log
│                                          │
│                                          ├── tests/
│                                          │
├── (no pyproject.toml)        ─────────►  ├── pyproject.toml
├── README.md                              ├── README.md
└── ...                                    └── ...
```

---

## Key Improvements Summary

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Root name** | `memagent-modular-fixed` | `pjj-tax-legal` |
| **Package location** | `PJJ-Tax-Legal/` (not installable) | `src/pjj_tax_legal/` (pip installable) |
| **Data folder** | `local-memory/` | `data/` |
| **Docs folder** | `claudecodedocs_MD/` | `docs/` |
| **App location** | `orchestrator/tax_workflow/frontend/` | `apps/` |
| **Archive visibility** | `Old/` (visible) | `.archive/` (hidden) |
| **Logs location** | `PJJ-Tax-Legal/streamlit_instance_info/logs/` | `logs/` |
| **Import style** | `sys.path` hacks | Proper package imports |
| **Package config** | None | `pyproject.toml` |

---

## File Renames

| Current Name | Proposed Name | Reason |
|--------------|---------------|--------|
| `tax_orchestrator.py` | `orchestrator.py` | Remove redundant `tax_` prefix |
| `tax_planner_agent.py` | `planner.py` | Cleaner, in `tax_workflow/` context |
| `tax_searcher_agent.py` | `searcher.py` | Cleaner, in `tax_workflow/` context |
| `tax_recommender_agent.py` | `recommender.py` | Cleaner, in `tax_workflow/` context |
| `tax_compiler_agent.py` | `compiler.py` | Cleaner, in `tax_workflow/` context |
| `tax_tracker_agent.py` | `tracker.py` | Cleaner, in `tax_workflow/` context |
| `tax_app.py` | `tax_assistant.py` | More descriptive of purpose |

---

## Import Changes Required

### Current Style (with sys.path hacks)
```python
# Every file needs this boilerplate:
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Then imports:
from agent import Agent
from agent.logging_config import get_logger
from orchestrator.agents.base_agent import BaseAgent
```

### Proposed Style (clean package imports)
```python
# No boilerplate needed after: pip install -e .

# Clean imports:
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.agent.logging_config import get_logger
from pjj_tax_legal.orchestrator.base.base_agent import BaseAgent
from pjj_tax_legal.orchestrator.tax_workflow.searcher import TaxResponseSearcher
```

---

## Risk Analysis

### CRITICAL Risks
1. **Streamlit startup command changes** - All scripts must update
2. **Package must be installed** - `pip install -e .` required before testing
3. **Data path resolution** - If wrong, Agent can't find documents

### HIGH Risks
4. **Import chain dependencies** - One wrong import breaks everything
5. **8 files have sys.path hacks** - All must be removed

### MEDIUM Risks
6. **Logging path changes** - May need new `logs/` directory
7. **REPO_ROOT recalculations** - Several files need updating

---

## Migration Steps

### Phase 1: Preparation
```bash
git init && git add . && git commit -m "Checkpoint before refactor"
git checkout -b backup-before-refactor && git checkout main
```

### Phase 2: Create Structure
- Create new directories
- Create `pyproject.toml`
- Create all `__init__.py` files

### Phase 3: Copy Files
- COPY (not move) all source files
- Keep originals until tests pass

### Phase 4: Update Code (BREAKING)
- Update all imports
- Update all path references
- Remove sys.path hacks
- Run `pip install -e .`

### Phase 5: Test
```bash
python -c "from pjj_tax_legal.agent import Agent; print('OK')"
streamlit run apps/tax_assistant.py
```

### Phase 6: Cleanup
- Delete old directories after tests pass

---

## Rollback Plan

```bash
git checkout backup-before-refactor
pip uninstall pjj-tax-legal
```

---

## Recommendation

**DO NOT proceed until:**
1. Current system is fully stable
2. Git backup is in place
3. You have 6-8 hours available
4. You're comfortable with the risks
