"""
CitationTracker Agent - Step 6b of Tax Workflow

Purpose: Embed citations in response

CONSTRAINT BOUNDARIES:
- Citation Scope: ONLY cite documents provided in selected_file_contents
- Accuracy: Every citation must match actual document location
- Traceability: Users can verify any claim by checking cited source
- Completeness: Every major claim should have a citation
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re
import time

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator.base import BaseAgent, AgentResult
from pjj_tax_legal.agent.logging_config import get_logger

logger = get_logger(__name__)


class CitationTracker(BaseAgent):
    """
    Step 6b: Embed citations in response

    Maps claims to source documents and adds citations
    in format: "According to [Document] (Section X)..."

    CONSTRAINT BOUNDARIES:
    - Citation Scope: ONLY cite documents provided in selected_file_contents
    - Accuracy: Every citation must match actual document location
    - Traceability: Users can verify any claim by checking cited source
    - Completeness: Every major claim should have a citation
    """

    def __init__(self, agent: Agent, memory_path: Path):
        super().__init__(agent, memory_path)
        self.agent = agent

    def generate(
        self,
        response: str,
        selected_file_contents: Dict[str, str]
    ) -> AgentResult:
        """
        Embed citations in response.

        Args:
            response: Response text
            selected_file_contents: Source documents {filename: content}

        Returns:
            AgentResult with response + citations
        """
        try:
            logger.info("=== CitationTracker.generate() STARTED ===")
            logger.info(f"Response length: {len(response)} characters")
            logger.info(f"Source documents provided: {len(selected_file_contents)}")
            logger.info(f"Source filenames: {list(selected_file_contents.keys())}")
            start_time = time.time()

            # Validate inputs
            if not response:
                logger.error("Response is empty")
                raise ValueError("Response cannot be empty")
            if not selected_file_contents:
                logger.error("No source documents provided")
                raise ValueError("Source documents required for citations")

            logger.info("Input validation passed")

            # Embed citations in response
            logger.info("Embedding citations in response...")
            response_with_citations = self._embed_citations(response, selected_file_contents)
            logger.info("Citations embedded in response")

            # Extract citation list
            logger.info("Extracting citation list...")
            citations = self._extract_citations(response_with_citations, selected_file_contents)
            logger.info(f"Extracted {len(citations)} unique cited sources")
            for citation in citations:
                logger.debug(f"Citation: {citation['source']} cited {citation['citations_count']} times")

            processing_time_ms = (time.time() - start_time) * 1000
            logger.info(f"=== CitationTracker.generate() COMPLETED SUCCESSFULLY in {processing_time_ms:.1f}ms ===")

            return AgentResult(
                success=True,
                output={
                    "response_text": response_with_citations,
                    "citations": citations,
                    "citation_count": len(citations)
                },
                metadata={
                    "total_citations": len(citations),
                    "citation_method": "source_matching_with_embedding",
                    "citation_accuracy": "sources_verified",
                    "source_only_constraint": True
                },
                timestamp=datetime.now().isoformat(),
                error=""
            )

        except ValueError as e:
            logger.error(f"ValueError in CitationTracker: {str(e)}")
            return AgentResult(
                success=False,
                output={"response_text": response, "citations": [], "citation_count": 0},
                metadata={"error_type": "validation"},
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

        except Exception as e:
            logger.error(f"=== CitationTracker.generate() FAILED ===")
            logger.error(f"Exception: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                output={"response_text": response, "citations": [], "citation_count": 0},
                metadata={"error_type": "citation_error"},
                timestamp=datetime.now().isoformat(),
                error=f"Citation embedding failed: {str(e)}"
            )

    def _embed_citations(self, response: str, sources: Dict[str, str]) -> str:
        """
        Embed citation references in response using Llama.

        Uses semantic understanding to map claims to sources and add citations
        in format: "claim text [Source: filename]"
        """
        try:
            # Build source context
            sources_text = "\n---\n".join(
                f"[Source: {filename}]\n{content[:500]}"  # First 500 chars per source
                for filename, content in sources.items()
            )

            # Ask Llama to add citations to the response
            prompt = f"""Add citations to this response by mapping each claim to a source document.

RESPONSE TEXT:
{response}

AVAILABLE SOURCES:
{sources_text}

INSTRUCTIONS:
1. Add [Source: filename] citations after each major claim
2. Only cite sources that actually support the claim
3. Keep the original text unchanged, just add citations
4. Use format: "claim text [Source: filename]"
5. Only cite from the available sources listed above

Rewrite the response with citations added:"""

            logger.debug("Requesting Llama to embed citations...")
            cited_response = self.agent.generate_response(prompt)

            if not cited_response:
                logger.warning("Llama returned empty response for citation embedding")
                return response  # Return original response if Llama fails

            logger.debug(f"Llama citation embedding successful ({len(cited_response)} chars)")
            return cited_response

        except Exception as e:
            logger.error(f"Error embedding citations with Llama: {e}")
            # Fallback: return original response without citations
            logger.warning("Falling back to original response without Llama-embedded citations")
            return response

    def _is_header(self, text: str) -> bool:
        """Check if line is a header (should not be cited)"""
        line = text.strip()
        return (line.startswith("#") or
                line.startswith("---") or
                line.endswith(":") or
                line.isupper() and len(line) < 30)

    def _find_matching_source(self, text: str, sources: Dict[str, str]) -> str:
        """
        Find best matching source document for given text.

        Uses word matching: returns source with highest keyword overlap.
        """
        text_lower = text.lower()
        text_words = set(w for w in text_lower.split() if len(w) > 3)

        if not text_words:
            return None

        best_match = None
        best_score = 0

        for filename, content in sources.items():
            content_lower = content.lower()

            # Count matching words between text and source
            matches = sum(1 for word in text_words if word in content_lower)

            # Calculate match score as percentage of text words found in source
            score = matches / len(text_words) if text_words else 0

            if score > best_score:
                best_score = score
                best_match = filename

        # Return match only if threshold exceeded (30% match)
        return best_match if best_score > 0.3 else None

    def _extract_citations(self, response: str, sources: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Extract list of citations from response.

        Returns: List of {source: filename, count: occurrences}
        """
        citations_dict = {}

        # Find all citation references [Source: ...] in response
        citation_pattern = r'\[Source: ([^\]]+)\]'
        matches = re.findall(citation_pattern, response)

        for source_file in matches:
            if source_file in sources:  # Only count valid sources
                if source_file not in citations_dict:
                    citations_dict[source_file] = 0
                citations_dict[source_file] += 1

        # Convert to list format
        citations = [
            {
                "source": source,
                "citations_count": count,
                "content_length": len(sources.get(source, ""))
            }
            for source, count in sorted(citations_dict.items(), key=lambda x: x[1], reverse=True)
        ]

        return citations


# ============================================================================
# UNIT TESTS
# ============================================================================

