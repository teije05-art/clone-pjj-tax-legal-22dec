# Track: Fix NameError in `src/pjj_tax_legal/agent/model.py`

## Overview

This track addresses a `NameError` in `src/pjj_tax_legal/agent/model.py` that occurred after migrating to Vertex AI authentication. The error is caused by an attempt to call `genai.configure(api_key=GEMINI_API_KEY)` when `GEMINI_API_KEY` has been removed.

## Functional Requirements

1.  **Remove problematic line:**
    *   The line `genai.configure(api_key=GEMINI_API_KEY)` in `src/pjj_tax_legal/agent/model.py` must be removed.

2.  **Ensure proper client usage:**
    *   Verify that `model.py` correctly utilizes the client object passed to its functions, without attempting to configure global API settings locally.

## Acceptance Criteria

*   The `NameError` is resolved, and the application can initialize and make LLM calls without errors related to `GEMINI_API_KEY`.
*   The system uses Vertex AI authentication as intended.
*   No new global API key configuration attempts are made within `model.py`.
