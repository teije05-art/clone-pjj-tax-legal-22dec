# Track Plan: Fix NameError in `src/pjj_tax_legal/agent/model.py`

This plan outlines the steps to fix the `NameError` related to `GEMINI_API_KEY` in `src/pjj_tax_legal/agent/model.py`, following the specification in `spec.md`.

## Phase 1: Implementation

This phase focuses on removing the problematic code and ensuring correct client initialization.

- [ ] Task: Fix NameError
    - [ ] Sub-task: Remove the line `genai.configure(api_key=GEMINI_API_KEY)` from `src/pjj_tax_legal/agent/model.py`.
    - [ ] Sub-task: Ensure the `create_gemini_client` function and `get_model_response` do not rely on `GEMINI_API_KEY` for global configuration.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 2: Verification

This phase ensures that the `NameError` is resolved and the application functions correctly with Vertex AI authentication.

- [ ] Task: Test Application Functionality
    - [ ] Sub-task: Run basic import tests to ensure no regressions.
    - [ ] Sub-task: Manually test the agent's core LLM interaction to confirm correct operation with Vertex AI authentication.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
