# Track: Refactor `searcher.py` to use Gemini and add fallback

## Overview

This track addresses the "No documents found" error by refactoring the `TaxResponseSearcher` in `src/pjj_tax_legal/orchestrator/tax_workflow/searcher.py`. The current implementation still relies on a Llama-based semantic extraction, which is failing after the migration to Gemini. This will be replaced with a Gemini-based implementation, and a robust keyword-based fallback will be added to ensure documents are always found.

## Functional Requirements

1.  **Refactor Semantic Search:**
    *   The `extract_semantics` method (or a similar method) in `searcher.py` must be updated to use the `google-genai` client.
    *   The model used for semantic understanding should be `gemini-3-flash`.
    *   Any dependencies on Llama or Fireworks AI within `searcher.py` must be removed.

2.  **Add Keyword Fallback:**
    *   A fallback mechanism must be implemented.
    *   If the Gemini-based semantic search fails or returns zero results, a keyword-based search should be performed on the filenames within the `data/tax_legal` directory.
    *   This fallback should guarantee that a list of relevant documents is always presented to the user.

## Acceptance Criteria

*   The "No documents found" error is resolved.
*   The "Select Source Documents" screen in the UI is always populated with a list of files, either from the semantic search or the keyword fallback.
*   `searcher.py` no longer contains references to Llama or Fireworks AI.
