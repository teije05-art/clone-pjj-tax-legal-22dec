# Frontend Migration: Streamlit to Reflex

**Date:** December 17, 2025
**Updated:** December 18, 2025
**Status:** Implementation In Progress
**Goal:** Replace Streamlit UI with professional-looking Reflex frontend

---

## Background

The current Streamlit frontend (`apps/tax_assistant.py`) works but:
- Looks generic/unprofessional
- Limited customization options
- Not suitable for client-facing demos
- Confusing step numbering (steps 2/3, 4/5 combined oddly)

---

## Clean 6-Step Workflow

The tax workflow has been reorganized into **6 clear, sequential steps**:

| Step | Name | User Action | System Action | Stage Key |
|------|------|-------------|---------------|-----------|
| **1** | Enter Question | Type tax question, click Submit | AI categorizes request | `step_1` |
| **2** | Confirm Categories | Review & confirm tax categories | - | `step_2` |
| **3** | Past Responses | Select relevant past memoranda | Search past_responses/ | `step_3` |
| **4** | Source Documents | Select relevant regulations | Search tax_database/ | `step_4` |
| **5** | Review Draft | Review & approve synthesized memo | Synthesize KPMG response | `step_5` |
| **6** | Complete | View/export final response | - | `step_6` |

### Workflow State Machine

```
step_1 (Enter Question)
    ↓ submit_question()
step_2 (Confirm Categories)
    ↓ confirm_categories()
step_3 (Past Responses) ← auto-search on entry
    ↓ proceed_to_documents()
step_4 (Source Documents) ← auto-search on entry
    ↓ synthesize_response()
step_5 (Review Draft)
    ↓ approve_draft()
step_6 (Complete)
    ↓ reset_workflow()
step_1 (back to start)
```

### Mapping from Old Streamlit Stages

| Old Stage (Streamlit) | New Step (Reflex) |
|-----------------------|-------------------|
| `step_1_request` | `step_1` |
| `step_1_review` | `step_2` |
| `step_2_search` | `step_3` (loading) |
| `step_2_review` | `step_3` |
| `step_4_recommend` | `step_4` (loading) |
| `step_4_review` | `step_4` |
| `step_5_compile` | `step_5` (loading) |
| `draft_review` | `step_5` |
| `complete` | `step_6` |

---

## Framework Selection

### Considered Frameworks

| Framework | Description | Verdict |
|-----------|-------------|---------|
| **NiceGUI** | FastAPI + Vue.js, Material Design | Too utilitarian, not professional enough |
| **Reflex** | Compiles to React/Next.js, Radix UI | **SELECTED** - Professional SaaS look |
| **Rio** | Pure Python, modern design | Still in beta, breaking changes possible |
| **FastHTML** | HTMX-based, raw HTML control | Too low-level for rapid prototyping |

### Why Reflex Won

1. **Maturity**: 20k+ GitHub stars, production-ready since 2022
2. **Professional Look**: Radix UI components (industry standard for SaaS)
3. **Tailwind CSS Support**: Full styling customization
4. **State Management**: Automatic frontend/backend sync via WebSockets
5. **No JavaScript Errors**: State defined in Python, no fetch() debugging
6. **FastAPI Backend**: Existing orchestrator code ports directly

---

## Project Structure

```
pjj-tax-legal/
├── src/pjj_tax_legal/              # UNCHANGED - Backend
│   ├── agent/                      # LLM agent code
│   └── orchestrator/               # Workflow orchestrator
├── apps/
│   ├── tax_assistant.py            # OLD - Streamlit (backup)
│   └── reflex_app/                 # NEW - Reflex project
│       ├── rxconfig.py             # Reflex configuration
│       └── reflex_app/
│           ├── __init__.py
│           ├── reflex_app.py       # Main app entry point
│           ├── state.py            # TaxState class
│           └── components/
│               ├── __init__.py
│               ├── header.py       # KPMG header component
│               ├── sidebar.py      # Session info & controls
│               ├── step_1.py       # Enter Question
│               ├── step_2.py       # Confirm Categories
│               ├── step_3.py       # Past Responses
│               ├── step_4.py       # Source Documents
│               ├── step_5.py       # Review Draft
│               └── step_6.py       # Complete
├── data/tax_legal/                 # UNCHANGED - Data
└── docs/planning/                  # Documentation
```

---

## State Design

### TaxState Class

```python
import reflex as rx

class TaxState(rx.State):
    """Centralized state for the 6-step tax workflow."""

    # Current step (1-6)
    current_step: int = 1
    is_loading: bool = False
    error_message: str = ""

    # Step 1: Enter Question
    request_text: str = ""

    # Step 2: Confirm Categories
    suggested_categories: list[str] = []
    confirmed_categories: list[str] = []

    # Step 3: Past Responses
    past_responses: list[dict] = []
    selected_past_responses: list[str] = []

    # Step 4: Source Documents
    recommended_files: list[dict] = []
    selected_files: list[str] = []

    # Step 5: Review Draft
    draft_response: str = ""

    # Step 6: Complete
    final_response: str = ""

    # Event handlers for each step transition
    async def submit_question(self): ...      # 1 → 2
    async def confirm_categories(self): ...   # 2 → 3
    async def proceed_to_documents(self): ... # 3 → 4
    async def synthesize_response(self): ...  # 4 → 5
    def approve_draft(self): ...              # 5 → 6
    def reset_workflow(self): ...             # 6 → 1
```

### Orchestrator Integration

The backend `TaxOrchestrator.run_workflow()` maps to steps as follows:

| TaxState Method | Orchestrator Step | Description |
|-----------------|-------------------|-------------|
| `submit_question()` | `step=1` | Categorize request |
| `confirm_categories()` | - | No backend call |
| `search_past_responses()` | `step=2` | Search past_responses/ |
| `search_documents()` | `step=4` | Search tax_database/ |
| `synthesize_response()` | `step=6` | Compile + cite response |

---

## Component Design

### Step 1: Enter Question

```python
def step_1() -> rx.Component:
    return rx.vstack(
        rx.heading("Step 1: Enter Tax Question", size="7"),
        rx.text("Submit your tax question for analysis."),
        rx.text_area(
            placeholder="E.g., What are the transfer pricing considerations for pharmaceutical imports to Vietnam?",
            value=TaxState.request_text,
            on_change=TaxState.set_request_text,
            min_height="150px",
            width="100%",
        ),
        rx.button(
            "Submit & Analyze",
            on_click=TaxState.submit_question,
            loading=TaxState.is_loading,
            size="3",
        ),
        spacing="4",
        width="100%",
    )
```

### Step 2: Confirm Categories

```python
def step_2() -> rx.Component:
    return rx.vstack(
        rx.heading("Step 2: Confirm Categories", size="7"),
        rx.text("Review the suggested tax categories."),
        rx.hstack(
            rx.foreach(
                TaxState.suggested_categories,
                lambda cat: rx.badge(cat, color_scheme="blue", size="2")
            ),
            wrap="wrap",
        ),
        rx.checkbox_group(
            TaxState.suggested_categories,
            default_value=TaxState.confirmed_categories,
            on_change=TaxState.set_confirmed_categories,
        ),
        rx.hstack(
            rx.button("Back", on_click=TaxState.go_to_step_1, variant="outline"),
            rx.button("Confirm & Search", on_click=TaxState.confirm_categories),
        ),
        spacing="4",
    )
```

### Steps 3-6

Similar patterns for remaining steps, with:
- Loading states during searches
- Selection interfaces for documents
- Preview expandable sections
- Navigation buttons (back/forward)

---

## Running the App

```bash
# From project root
cd apps/reflex_app
reflex run

# Opens at http://localhost:3000
```

---

## What Stays the Same

- `src/pjj_tax_legal/agent/` - All agent code unchanged
- `src/pjj_tax_legal/orchestrator/` - All orchestrator code unchanged
- `data/tax_legal/` - All data unchanged
- `TaxOrchestrator.run_workflow()` API - No changes needed

---

## Implementation Checklist

- [x] Install Reflex
- [x] Initialize project structure
- [ ] Create TaxState class with clean 6-step numbering
- [ ] Build Step 1: Enter Question
- [ ] Build Step 2: Confirm Categories
- [ ] Build Step 3: Past Responses
- [ ] Build Step 4: Source Documents
- [ ] Build Step 5: Review Draft
- [ ] Build Step 6: Complete
- [ ] Add header and sidebar components
- [ ] Apply professional Tailwind styling
- [ ] Test full workflow end-to-end

---

## Resources

- [Reflex Documentation](https://reflex.dev/docs/getting-started/introduction/)
- [Reflex GitHub](https://github.com/reflex-dev/reflex) - 20k+ stars
- [Reflex Templates](https://reflex.dev/templates/) - Dashboard examples
- [Reflex Components](https://reflex.dev/docs/library/) - All available components
