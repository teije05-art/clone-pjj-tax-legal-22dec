# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PJJ Tax & Legal is a multi-agent Vietnamese tax advisory system. It uses constraint-based search over a curated database of 3,400+ tax documents and past advisory memoranda to produce citation-backed KPMG-style professional responses.

**LLM Backend:** Llama 3.3 70B Instruct via Fireworks AI API

## Commands

```bash
# Install (development mode)
pip install -e .

# Run the Streamlit application (stable)
streamlit run apps/tax_assistant.py

# Run the Reflex application (new frontend, WIP)
cd apps/reflex_app && reflex run

# Verify package imports
python -c "from pjj_tax_legal.agent import Agent; print('OK')"
python -c "from pjj_tax_legal.orchestrator import TaxOrchestrator; print('OK')"
```

## Environment

Requires `FIREWORKS_API_KEY` environment variable (or set in `.env` file).

## Frontends

Two UI options in `apps/`:
- **Streamlit** (`apps/tax_assistant.py`): Stable, production-ready
- **Reflex** (`apps/reflex_app/`): New frontend, work-in-progress. Uses Tailwind v4.

## Architecture

### Two-Layer System

1. **Agent Layer** (`src/pjj_tax_legal/agent/`)
   - `Agent` class: Core LLM agent with chat loop and sandboxed Python execution
   - Uses "MemAgent" pattern: LLM navigates files via Python tool calls (`read_file`, `list_files`, etc.)
   - All file operations run in sandbox (`engine.py`) with restricted paths
   - Model calls via `model.py` using Fireworks streaming API

2. **Orchestrator Layer** (`src/pjj_tax_legal/orchestrator/`)
   - `TaxOrchestrator`: Master coordinator for 6-step tax workflow
   - 5 specialized agents, each inheriting from `BaseAgent`:
     - `RequestCategorizer` (Step 1): Maps questions to tax categories (no memory search)
     - `TaxResponseSearcher` (Step 2): Searches `past_responses/` directory
     - `FileRecommender` (Step 4): Searches `tax_database/` directory
     - `TaxResponseCompiler` (Step 6a): Synthesizes professional memorandum
     - `CitationTracker` (Step 6b): Embeds source citations

### Constraint Boundary Pattern

The system enforces "constraint boundaries" to prevent hallucinations:
- Each agent operates within defined directory boundaries
- User approves categories (Step 1) and document selections (Step 5) before synthesis
- Final responses cite ONLY from user-selected documents
- `TaxPlanningSession` is the single source of truth for all workflow state

### Data Structure

```
data/tax_legal/
├── past_responses/    # Curated advisory memoranda (segments 0-3)
├── tax_database/      # 3,400+ Vietnamese tax regulations (segments 4-11)
├── tax-database-index.json
└── users/             # Session storage
```

### Package Imports

```python
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator import TaxOrchestrator
```

## Key Design Patterns

- **Vanilla MemAgent**: All searches use `Agent.chat()` with intelligent file navigation, not semantic similarity
- **Human-in-the-loop**: User confirms categories (Step 1→2) and documents (Step 5→6) before synthesis
- **Single save point**: Only `TaxOrchestrator.save_approved_response()` persists approved responses
- **Session recovery**: `TaxPlanningSession` serialized to disk after each step for Streamlit reset recovery

## Tax Categories

CIT, VAT, Transfer Pricing, PIT, FCT, DTA, Customs, Excise Tax, Environmental Tax, Capital Gains (18 total)
