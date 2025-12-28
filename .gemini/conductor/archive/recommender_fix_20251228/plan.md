# Track Plan: Fix "No documents found" in `recommender.py` with "Safety Net"

This plan outlines the steps to debug `recommender.py` and implement a "Safety Net" fallback, following the specification in `spec.md`.

## Phase 1: Implementation

This phase focuses on debugging the MemAgent and implementing the fallback mechanism.

- [ ] Task: Debug `recommender.py`
    - [ ] Sub-task: Add temporary `print()` statements to the `generate()` method to log the absolute paths being scanned, the raw response from the Gemini model, and the final list of files found.
- [ ] Task: Implement "Safety Net" Fallback
    - [ ] Sub-task: Modify the `generate()` method to trigger a "Dumb Fallback" if the AI-based search returns 0 documents.
    - [ ] Sub-task: The fallback should use `glob` or `os.walk` to find all `.pdf` files in the `data` directory and return them.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 2: Verification

This phase ensures that the document search functionality is robust and always returns documents if they exist.

- [ ] Task: Test Application Functionality
    - [ ] Sub-task: Manually test the "Select Source Documents" screen to confirm it always populates with a list of files, even if the AI search fails.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
