"""
TaxResponseCompiler Agent - Step 5 of Tax Workflow

Purpose: Synthesize KPMG-format response from selected documents

CONSTRAINT BOUNDARIES:
- Input Scope: ONLY documents selected by user (selected_file_contents)
- Synthesis Constraint: ALL statements must cite source documents
- No Autonomy: Cannot use external knowledge or hallucinate beyond provided documents
- Quality Gate: Every claim must reference a source file
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import time

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator.base import BaseAgent, AgentResult
from pjj_tax_legal.agent.logging_config import get_logger

logger = get_logger(__name__)


class TaxResponseCompiler(BaseAgent):
    """
    Step 5: Synthesize KPMG-format response

    Uses Llama to generate professional tax memorandum
    based on selected source documents only (no external knowledge).

    CONSTRAINT BOUNDARIES:
    - Input Scope: ONLY documents selected by user (selected_file_contents)
    - Synthesis Constraint: ALL statements must cite source documents
    - No Autonomy: Cannot use external knowledge or hallucinate beyond provided documents
    - Quality Gate: Every claim must reference a source file
    """

    # KPMG Memo format template (matching actual past responses structure)
    KPMG_MEMO_TEMPLATE = """KPMG TAX MEMORANDUM

RE: {subject}
DATE: {date}

---

## BACKGROUND INFORMATION

Our understanding of the facts and arrangement:

{background}

---

## EXECUTIVE SUMMARY

Key findings and recommendations:

{executive_summary}

---

## LEGAL BASIS

Relevant regulations and framework:

{legal_basis}

---

## OUR COMMENTS

Detailed analysis and findings:

{analysis}

---

## RECOMMENDATIONS

Recommended approach and tax optimization strategies:

{recommendations}

---

## IMPORTANT NOTES

Limitations and disclaimers:

{important_notes}

---

## SOURCE DOCUMENTS CITED

The above advice is based on the following source documents:

{sources}
"""

    def __init__(self, agent: Agent, memory_path: Path):
        super().__init__(agent, memory_path)
        self.agent = agent

    def generate(
        self,
        request: str,
        selected_files: List[str],
        selected_file_contents: Dict[str, str],
        categories: List[str]
    ) -> AgentResult:
        """
        Synthesize KPMG-format response.

        Args:
            request: Original client request
            selected_files: List of selected file names
            selected_file_contents: {filename: content} dict
            categories: Confirmed tax categories

        Returns:
            AgentResult with synthesized response
        """
        try:
            logger.info("=== TaxResponseCompiler.generate() STARTED ===")
            logger.info(f"Request: '{request[:100]}...' (length: {len(request)})")
            logger.info(f"Selected files: {selected_files}")
            logger.info(f"Categories: {categories}")

            # Validate inputs
            if not request:
                logger.error("Request is empty")
                raise ValueError("Request cannot be empty")
            if not selected_files:
                logger.error("No selected files provided")
                raise ValueError("At least one source file must be selected")
            if not selected_file_contents:
                logger.error("No file contents provided")
                raise ValueError("File contents required for synthesis")

            logger.info("All input validations passed")
            logger.info(f"Constraint: ONLY use these {len(selected_files)} selected files, NO external knowledge")

            # Build context from selected files
            logger.info("Building context from selected files...")
            context = self._build_context(selected_files, selected_file_contents)
            logger.info(f"Context built: {len(context.split())} tokens")

            # Create Llama prompt with SOURCE-ONLY constraint
            logger.info("Building synthesis prompt with source-only constraint...")
            prompt = self._build_prompt(request, context, categories)
            logger.debug(f"Prompt: {prompt[:300]}...")

            # REAL LLAMA CALL: Generate response with Fireworks API
            logger.info("=== CALLING LLAMA FOR RESPONSE SYNTHESIS (Step 5) ===")
            logger.info("Using Gemini 3 Flash via Google Gemini API...")
            start_time = time.time()

            # Call Llama with strict source-only constraint
            logger.debug(f"Prompt length: {len(prompt)} characters")
            logger.debug(f"Context length: {len(context)} characters")

            # Use generate_text() for direct LLM call without tool loop
            # This prevents the MemAgent tool loop from interfering with synthesis
            response = self.agent.generate_text(prompt)
            logger.info(f"Llama response received: {len(response)} characters")

            if not response or len(response.strip()) < 100:
                logger.error("CRITICAL: Llama returned empty or too-short response!")
                raise ValueError("Llama synthesis returned no content - unable to generate response")

            processing_time_ms = (time.time() - start_time) * 1000
            logger.info(f"Response synthesis completed in {processing_time_ms:.1f}ms")
            logger.info(f"Generated response: {len(response.split())} tokens")
            logger.info("=== TaxResponseCompiler.generate() COMPLETED SUCCESSFULLY ===")

            return AgentResult(
                success=True,
                output=response,  # Synthesized KPMG memo
                metadata={
                    "llama_model": "llama-3.3-70b",
                    "llama_prompt_tokens": len(prompt.split()),
                    "llama_response_tokens": len(response.split()),
                    "processing_time_ms": int(processing_time_ms),
                    "files_used": len(selected_files),
                    "context_tokens": len(context.split()),
                    "categories": categories,
                    "source_only_constraint": True,
                    "constraint_boundary": "ONLY selected documents, no external knowledge"
                },
                timestamp=datetime.now().isoformat(),
                error=""
            )

        except ValueError as e:
            logger.error(f"ValueError in TaxResponseCompiler: {str(e)}")
            return AgentResult(
                success=False,
                output="",
                metadata={"error_type": "validation"},
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

        except Exception as e:
            logger.error(f"=== TaxResponseCompiler.generate() FAILED ===")
            logger.error(f"Exception: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                output="",
                metadata={"error_type": "compilation_error"},
                timestamp=datetime.now().isoformat(),
                error=f"Response synthesis failed: {str(e)}"
            )

    def _build_context(self, selected_files: List[str], contents: Dict[str, str]) -> str:
        """Build context from selected files (no token limits)"""
        context_parts = []

        for filename in selected_files:
            if filename not in contents:
                continue

            file_content = contents[filename]
            context_parts.append(f"[{filename}]\n{file_content}")

        return "\n\n---\n\n".join(context_parts)

    def _build_prompt(self, request: str, context: str, categories: List[str]) -> str:
        """Build Llama prompt with CRITICAL SOURCE-ONLY constraints"""
        return f"""You are a senior tax advisor at KPMG Vietnam. Generate a professional tax memorandum.

CRITICAL CONSTRAINT BOUNDARIES:
- You MUST ONLY use information from the SOURCE DOCUMENTS provided below
- You MUST NOT use external knowledge or general tax principles not explicitly stated in sources
- EVERY statement must be sourced to a specific document
- If information is not in sources, you must state "Source does not address this issue"
- Violation of these constraints will result in hallucinations and loss of credibility

CLIENT REQUEST:
{request}

TAX CATEGORIES INVOLVED:
{', '.join(categories)}

SOURCE DOCUMENTS (ONLY SOURCE OF TRUTH):
{context}

INSTRUCTIONS:
1. Write as KPMG TAX MEMORANDUM with sections: Background, Regulatory Understanding, Analysis, Recommendations, Risks, Sources
2. EVERY STATEMENT must cite which source document it comes from (CONSTRAINT BOUNDARY)
3. Use format: "According to [Document Name]..."
4. Do not make assumptions or state facts not found in source documents (CONSTRAINT BOUNDARY)
5. Be clear, professional, concise (2-4 pages)
6. Identify Vietnamese regulations by their official names (Luật, Thông tư, Quyết định, etc.)
7. Use source citations liberally - citation shows constraint adherence

Generate the memorandum (respecting ALL constraints):"""

