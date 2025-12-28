# Track Plan: Refactor `searcher.py` with Gemini and "Anti-Zero" Fallback

This plan outlines the steps to refactor `searcher.py` to use Gemini for semantic search and add a keyword-based fallback, following the specification in `spec.md`.

## Phase 1: Implementation

This phase focuses on updating the searcher to use Gemini and implementing the fallback mechanism.

- [ ] Task: Refactor `searcher.py`
    - [ ] Sub-task: Update the semantic extraction logic to use the `google-genai` client with the `gemini-3-flash` model.
    - [ ] Sub-task: Remove all references and dependencies related to Llama and Fireworks AI.
    - [ ] Sub-task: Implement a keyword-based search on filenames in `data/tax_legal` as a fallback if the semantic search yields no results, returning the top 20 filenames.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 2: Verification

This phase ensures that the document search functionality is working correctly.

- [ ] Task: Test Application Functionality
    - [ ] Sub-task: Run basic import tests to ensure no regressions.
    - [ ] Sub-task: Manually test the "Select Source Documents" screen to confirm it always populates with a list of files.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
