# Tech Stack

This document outlines the key technologies and frameworks used in the PJJ Tax & Legal AI System.

## Core Technologies

- **Python 3.10+**: Primary programming language.
- **Llama 3.3 70B Instruct via Fireworks AI**: Large Language Model for AI reasoning.
- **Streamlit**: Web application framework for the user interface.
- **Pydantic**: Data validation and settings management.
- **python-dotenv**: Environment variable management.

## Project-Specific Libraries

- **pjj_tax_legal**: Custom Python package containing agent and orchestrator logic.

## Databases & Storage

- **Local File System**: Used for storing tax databases, past responses, logs, and session data.
  - `data/tax_legal/tax_database/`: Stores 3,400+ Vietnamese tax regulations.
  - `data/tax_legal/past_responses/`: Stores curated advisory memoranda.
  - `logs/tax_app.log`: Application logs.
  - `.gemini/conductor/tracks/`: Stores Conductor track-specific data (spec.md, plan.md, metadata.json).
  - `data/tax_legal/users/user/sessions/`: Stores user session data for the Streamlit app.

## Development Tools

- **Git**: Version control.
- **pip/setuptools**: Python package management.
- **VS Code**: Integrated Development Environment (IDE).

## Future Considerations

- **Database Migration**: Potential migration to a more robust database solution for scalability and performance.
- **Cloud Deployment**: Deployment to cloud platforms (e.g., Azure, AWS, GCP) for production environments.
- **Alternative LLMs**: Exploration of other LLMs (e.g., Google Gemini, OpenAI GPT series) as backend options.
