# Track Plan: Refactor to use Vertex AI Authentication

This plan outlines the steps to refactor the agent's authentication to use Vertex AI, following the specification in `spec.md`.

## Phase 1: Implementation

This phase focuses on updating the configuration and client initialization to use Vertex AI.

- [ ] Task: Refactor Settings
    - [ ] Sub-task: Remove `GEMINI_API_KEY` variable definition from `src/pjj_tax_legal/agent/settings.py`.
    - [ ] Sub-task: Remove the `GEMINI_API_KEY` validation block from `src/pjj_tax_legal/agent/settings.py`.
    - [ ] Sub-task: Set `GEMINI_MODEL` to `"gemini-3-flash"` in `src/pjj_tax_legal/agent/settings.py`.
- [ ] Task: Refactor Client Initialization
    - [ ] Sub-task: Modify the `create_gemini_client` function in `src/pjj_tax_legal/agent/model.py` to initialize the client with Vertex AI parameters.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 2: Verification

This phase ensures that the migration to Vertex AI authentication was successful.

- [ ] Task: Test Application Functionality
    - [ ] Sub-task: Run basic import tests to ensure no regressions.
    - [ ] Sub-task: Manually test the agent's core LLM interaction to confirm correct operation with Vertex AI authentication.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
