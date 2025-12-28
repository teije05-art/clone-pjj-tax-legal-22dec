# Gemini Code Assistant Context

## Project: PJJ Tax & Legal AI System

This project is a multi-agent tax advisory system for Vietnamese tax and legal compliance. It uses a 6-step workflow to provide verifiable, citation-backed responses based on a curated database of over 3,400 tax documents and past advisory memoranda.

### Key Technologies

-   **LLM**: Llama 3.3 70B Instruct via Fireworks AI
-   **Frontend**: Streamlit
-   **Backend**: Python
-   **Architecture**: Multi-agent system with a constraint-based search architecture.

### Project Structure

The project is organized into the following main directories:

-   `src/pjj_tax_legal`: The main Python package containing the core logic.
    -   `agent`: The core LLM agent system, including the `Agent` class, Fireworks AI client, and sandboxed code execution engine.
    -   `orchestrator`: The tax workflow system, which coordinates the different agents in the 6-step pipeline.
-   `apps`: Contains the Streamlit web application (`tax_assistant.py`).
-   `data/tax_legal`: Contains the tax database and past responses.
-   `raw-tax-legal-db`: Contains the raw tax and legal documents.
-   `docs`: Project documentation.
-   `logs`: Application logs.

### How to Run the Application

1.  **Install dependencies**:
    ```bash
    pip install -e .
    ```
2.  **Set up environment variables**:
    Create a `.env` file in the project root with your Fireworks AI API key:
    ```
    FIREWORKS_API_KEY=your-api-key
    ```
3.  **Run the Streamlit application**:
    ```bash
    streamlit run apps/tax_assistant.py
    ```
    The application will be available at `http://localhost:8501`.

### Development Conventions

-   The project uses a multi-agent architecture with specialized components for each step of the workflow.
-   Each agent operates within defined constraint boundaries, only searching approved directories and citing real documents to prevent hallucinations.
-   The system uses a vanilla MemAgent pattern for memory navigation, where the agent reads from the `past_responses/` and `tax_database/` directories.
-   All searches are performed using the `Agent.chat()` method, which uses the LLM's understanding of the query to navigate the memory.

### Testing

The `README.md` file provides the following commands for basic testing:

```bash
python -c "from pjj_tax_legal.agent import Agent; print('OK')"
python -c "from pjj_tax_legal.orchestrator import TaxOrchestrator; print('OK')"
```
