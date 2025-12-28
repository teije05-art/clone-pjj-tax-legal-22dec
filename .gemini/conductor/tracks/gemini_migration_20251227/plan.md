# Track Plan: Migrate from Fireworks AI to Google Gemini 3.0

This plan outlines the steps to migrate the backend LLM from Fireworks AI to Google Gemini 3.0, following the specification defined in `spec.md`.

## Phase 1: Implementation

This phase focuses on updating project dependencies, refactoring the LLM client, and adapting the API call logic to use Google Gemini 3.0.

- [ ] Task: Dependency Management
    - [ ] Sub-task: Remove `fireworks-ai` from `requirements.txt`.
    - [ ] Sub-task: Add `google-genai` (latest version) to `requirements.txt`.
    - [ ] Sub-task: Update `pyproject.toml` to reflect dependency changes.
- [ ] Task: Refactor LLM Client Initialization
    - [ ] Sub-task: Locate and remove all instances of `fireworks` client initialization.
    - [ ] Sub-task: Implement `google-genai` client initialization using `genai.Client(api_key=os.getenv('GEMINI_API_KEY'), http_options={'api_version': 'v1beta'})`.
    - [ ] Sub-task: Update `src/pjj_tax_legal/agent/settings.py` to use `GEMINI_API_KEY` and define `GEMINI_MODEL = "gemini-3-flash"`.
- [ ] Task: Refactor LLM Call Logic
    - [ ] Sub-task: Change any explicit model mentions from the old model to `gemini-3-flash`.
    - [ ] Sub-task: Adapt existing LLM API calls to use the new `google-genai` client methods.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 2: Verification

This phase ensures that the migration was successful, and the application functions correctly with the new Gemini 3.0 backend.

- [ ] Task: Test Application Functionality
    - [ ] Sub-task: Run all existing unit and integration tests to ensure no regressions.
    - [ ] Sub-task: Manually test the agent's core LLM interaction workflows (e.g., asking a tax question) to confirm correct operation with Gemini 3.0.
- [ ] Task: Validate Dependency Removal
    - [ ] Sub-task: Confirm that `fireworks-ai` and related packages are no longer installed or required by the project.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
