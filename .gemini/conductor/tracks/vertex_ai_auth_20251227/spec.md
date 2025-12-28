# Track: Refactor to use Vertex AI Authentication

## Overview

This track involves refactoring the agent's authentication method from using an API key to using Vertex AI service-based authentication. This will remove the need for a `GEMINI_API_KEY` environment variable.

## Functional Requirements

1.  **Client Initialization:**
    *   The `genai.Client` initialization in `agent.py` must be updated to use Vertex AI authentication.
    *   The new client initialization should be:
        ```python
        client = genai.Client(
            vertexai=True,
            project="gen-lang-client-0209516002",
            location="us-central1"
        )
        ```

2.  **API Key Removal:**
    *   The `GEMINI_API_KEY` check in `settings.py` must be removed.
    *   The `GEMINI_API_KEY` definition in `settings.py` can also be removed.

3.  **Model Configuration:**
    *   The `GEMINI_MODEL` in `settings.py` must be set to `gemini-3-flash`.

## Acceptance Criteria

*   The application runs successfully after the refactoring.
*   The agent can successfully make LLM calls to the Gemini backend using Vertex AI authentication.
*   The `GEMINI_API_KEY` is no longer required for the application to run.
