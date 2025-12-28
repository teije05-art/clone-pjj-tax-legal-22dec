# Track: Migrate from Fireworks AI to Google Gemini 3.0

## Overview

This track involves migrating the core LLM backend of the agent from the current Fireworks AI implementation to Google's Gemini 3.0 via the `google-genai` Python library. The goal is to completely remove the dependency on `fireworks-ai` and replace it with the new Gemini backend, specifically using the `gemini-3-flash` model.

## Functional Requirements

1.  **Dependency Management:**
    *   The `fireworks-ai` dependency must be removed from all project requirement files (e.g., `requirements.txt`, `pyproject.toml`).
    *   The `google-genai` library must be added as a dependency.

2.  **API Client Refactoring:**
    *   All code responsible for initializing the Fireworks AI client must be located and removed.
    *   A new client for the Google Gemini API must be initialized using the `google-genai` library.
    *   The new client should be configured using an environment variable `GEMINI_API_KEY`.
    *   The client should be initialized like this: `client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'), http_options={'api_version': 'v1beta'})`

3.  **Model Configuration:**
    *   The model identifier used for generation calls must be updated from the current Fireworks model to `gemini-3-flash`.

4.  **API Call Logic:**
    *   The code making the actual API calls to the LLM must be refactored to use the new Gemini client and its methods.

## Acceptance Criteria

*   The application runs successfully after the migration.
*   The agent can successfully make LLM calls to the Gemini 3.0 backend.
*   The `fireworks-ai` library is no longer part of the project's dependencies.
*   API key handling for Gemini is done via environment variables.

## Out of Scope

*   This migration does not include adding a UI for model selection.
*   No changes to the application's frontend or overall workflow, other than the LLM backend.
