# PJJ Tax & Legal AI System

A multi-agent tax advisory system for Vietnamese tax and legal compliance. Built with Llama 3.3 70B, Streamlit, and a constraint-based search architecture.

## Overview

This system provides AI-powered Vietnamese tax advisory through a 6-step workflow. Rather than generating answers from general knowledge, it searches a curated database of 3,400+ tax documents and past advisory memoranda to produce verifiable, citation-backed responses.

**Key Features:**
- Constraint-based search prevents hallucinations - responses cite real documents only
- Human-in-the-loop approval at key workflow stages
- Professional KPMG-style memorandum output
- Supports 18 Vietnamese tax categories (CIT, VAT, DTA, Transfer Pricing, etc.)

## Project Structure

```
pjj-tax-legal/
├── src/
│   └── pjj_tax_legal/              # Main Python package
│       ├── agent/                  # Core LLM agent system
│       │   ├── agent.py            # Agent class with chat & tool execution
│       │   ├── engine.py           # Sandboxed Python execution
│       │   ├── model.py            # Fireworks API client
│       │   ├── tools.py            # File navigation tools
│       │   └── settings.py         # Configuration
│       │
│       └── orchestrator/           # Tax workflow system
│           ├── base/               # Base agent classes
│           └── tax_workflow/       # 6-step tax pipeline
│               ├── orchestrator.py # Master workflow coordinator
│               ├── planner.py      # Step 1: Request categorization
│               ├── searcher.py     # Step 2: Past response search
│               ├── recommender.py  # Step 4: Tax database search
│               ├── compiler.py     # Step 5: Response synthesis
│               └── tracker.py      # Step 6: Citation tracking
│
├── apps/
│   └── tax_assistant.py            # Streamlit web application
│
├── data/
│   └── tax_legal/
│       ├── tax_database/           # 3,400+ Vietnamese tax regulations
│       └── past_responses/         # Curated advisory memoranda
│
├── docs/                           # Documentation
├── logs/                           # Application logs
├── pyproject.toml                  # Package configuration
└── requirements.txt                # Dependencies
```

## Installation

### Prerequisites
- Python 3.10+
- Fireworks AI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pjj-tax-legal
```

2. Install the package:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
export FIREWORKS_API_KEY="your-api-key"
```

Or create a `.env` file in the project root:
```
FIREWORKS_API_KEY=your-api-key
```

## Usage

### Running the Application

```bash
cd pjj-tax-legal
streamlit run apps/tax_assistant.py
```

The application will open at `http://localhost:8501`

### Workflow

1. **Enter a tax question** - e.g., "What conditions must be satisfied to apply 0% VAT on exported software services?"

2. **Review categorization** - System suggests relevant tax categories (VAT, CIT, DTA, etc.)

3. **Select past responses** - Browse and select relevant advisory memoranda

4. **Select tax documents** - Browse and select relevant regulations

5. **Generate response** - System synthesizes a professional memorandum with citations

## Architecture

The system uses a multi-agent architecture with specialized components:

| Agent | Purpose |
|-------|---------|
| RequestCategorizer | Maps questions to tax categories |
| TaxResponseSearcher | Searches past advisory memoranda |
| FileRecommender | Searches tax regulation database |
| TaxResponseCompiler | Synthesizes professional responses |
| CitationTracker | Embeds source citations |

**Constraint Boundaries**: Each agent operates within defined boundaries - they can only search approved directories and must cite real documents. This eliminates hallucinations by design.

## Technical Details

- **LLM**: Llama 3.3 70B Instruct via Fireworks AI
- **Framework**: Streamlit for web UI
- **Pattern**: MemAgent (memory-based file navigation)
- **Execution**: Sandboxed Python for safe code execution

## Data Sources

### Tax Database
- 3,400+ Vietnamese tax regulations
- Organized into 18 categories (CIT, VAT, Customs, PIT, DTA, Transfer Pricing, FCT, etc.)
- Includes official circulars, decrees, and legal documents

### Past Responses
- Curated advisory memoranda
- Professional analysis and recommendations
- Same 18-category taxonomy

## Development

### Package Imports

The codebase uses standard Python package imports:

```python
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator import TaxOrchestrator
```

### Running Tests

```bash
python -c "from pjj_tax_legal.agent import Agent; print('OK')"
python -c "from pjj_tax_legal.orchestrator import TaxOrchestrator; print('OK')"
```

## License

Internal use only.

## Last Updated

December 2025
