# Track: Refactor `searcher.py` with Gemini and "Anti-Zero" Fallback

## Overview

This track addresses the "No documents found" error by refactoring the `TaxResponseSearcher` in `src/pjj_tax_legal/orchestrator/tax_workflow/searcher.py`. The current implementation still relies on a Llama-based semantic extraction, which is failing after the migration to Gemini. This will be replaced with a Gemini-based implementation, and a robust keyword-based fallback will be added to ensure documents are always found.

## Functional Requirements

1.  **Refactor Semantic Search:**
    *   The semantic extraction logic in `searcher.py` must be updated to use the `google-genai` client.
    *   Any dependencies on Llama or Fireworks AI within `searcher.py` must be removed.

2.  **Implement "Anti-Zero" Fallback:**
    *   A fallback mechanism must be implemented in the `search()` method (or equivalent).
    *   If the Gemini-based semantic search fails or returns zero results, a keyword-based search should be performed on the filenames within the `data/tax_legal` directory.
    *   This fallback must return the top 20 filenames that match the keywords.
    *   This is to ensure that the user never sees a "No documents found" message if files exist.

## Acceptance Criteria

*   The "No documents found" error is resolved.
*   The "Select Source Documents" screen in the UI is always populated with a list of files.
*   `searcher.py` no longer contains references to Llama or Fireworks AI.
