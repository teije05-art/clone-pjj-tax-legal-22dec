"""
Tax/Legal Workflow Module - Project Jupiter Phase 2

Specialized agents for tax advice workflow using Vanilla MemAgent Pattern:
- RequestCategorizer: Classify tax requests into domains using Llama
- TaxResponseSearcher: Search past approved responses via MemAgent
- FileRecommender: Search tax database documents via MemAgent
- TaxResponseCompiler: Synthesize KPMG-format responses using Llama
- CitationTracker: Embed and track citations
(DocumentVerifier removed - human does manual verification)

DUAL-LLM ARCHITECTURE:
- MemAgent (via Agent.chat()): Navigates filesystem and reads memory
  - Performs intelligent LLM-driven file discovery
  - Accesses past_responses/ and tax_database/ directories
  - Returns natural language descriptions of findings
- Gemini (via Google Gemini API): Performs reasoning and synthesis
  - Takes MemAgent findings and synthesizes responses
  - Applies domain expertise for tax/legal advice
  - Enforces constraint boundaries
"""

__version__ = "1.0.0"

# Updated imports to use new file names
from .planner import RequestCategorizer
from .searcher import TaxResponseSearcher
from .recommender import FileRecommender
from .compiler import TaxResponseCompiler
from .tracker import CitationTracker
from .orchestrator import TaxOrchestrator

__all__ = [
    "RequestCategorizer",
    "TaxResponseSearcher",
    "FileRecommender",
    "TaxResponseCompiler",
    "CitationTracker",
    "TaxOrchestrator"
]
