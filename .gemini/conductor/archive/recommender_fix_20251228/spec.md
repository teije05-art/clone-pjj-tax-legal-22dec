# Track: Fix "No documents found" in `recommender.py` with "Safety Net"

## Overview

This track addresses the "No documents found" error originating from the `FileRecommender` in `src/pjj_tax_legal/orchestrator/tax_workflow/recommender.py`. The "MemAgent" mode is failing to list files with the new Gemini model. The goal is to debug this process and implement a "Safety Net" fallback to ensure the user always sees a list of documents if any exist.

## Functional Requirements

1.  **Debug MemAgent:**
    *   Add temporary `print()` statements to the `generate()` or `search()` method in `recommender.py` to log:
        *   The absolute paths being scanned.
        *   The raw response from the Gemini model.
        *   The final list of files extracted from the model's response.

2.  **Implement "Safety Net" Fallback:**
    *   A fallback mechanism must be implemented.
    *   If the AI-based MemAgent search fails or returns zero results, a "Dumb Fallback" should be triggered.
    *   This fallback will use standard Python (`glob` or `os.walk`) to find all `.pdf` files within the `data` directory.
    *   The list of found `.pdf` files must be returned to the user, ensuring the "Select Source Documents" screen is never empty if files exist.

## Acceptance Criteria

*   The "No documents found" error is resolved.
*   The "Select Source Documents" screen in the UI is always populated with a list of files.
*   The `recommender.py` module is more robust against AI-based search failures.
