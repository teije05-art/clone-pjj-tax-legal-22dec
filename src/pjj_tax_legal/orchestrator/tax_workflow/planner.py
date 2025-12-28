"""
RequestCategorizer - Step 1 Agent

Analyzes client tax requests and suggests relevant tax domains/categories.
Used to establish user-selected constraint boundary for downstream searches.

CONSTRAINT BOUNDARIES:
- NO MemAgent search (classification only, uses keyword detection + Llama)
- Input: request string (minimum 10 characters)
- Output: suggested_categories list with confidence scores
- User confirms these categories before any MemAgent searches happen

This agent does NOT access memory. It only performs request classification.
Output categories become the user boundary for Steps 2 and 4 searches.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator.base import BaseAgent, AgentResult
from pjj_tax_legal.agent.logging_config import get_logger, log_agent_call, log_agent_response, log_agent_error, log_json_parsing

logger = get_logger(__name__)


class RequestCategorizer(BaseAgent):
    """
    Categorizes incoming tax requests into relevant tax domains.

    Uses keyword-based detection + Llama classification to suggest
    tax categories that the user will confirm before searches.

    CONSTRAINT BOUNDARIES:
    - NO MemAgent search (classification only)
    - Input validation: request must be >= 10 characters
    - Output: suggested_categories list with confidence
    - Output becomes user boundary for downstream searches

    Categories Available:
    - CIT: Corporate Income Tax
    - VAT: Value Added Tax
    - Transfer Pricing: Intercompany pricing
    - PIT: Personal Income Tax
    - FCT: Foreign Contractor Tax
    - DTA: Double Taxation Agreements
    - Customs: Import/Export duties
    - Excise Tax: Special goods taxation
    - Environmental Tax: Pollution/resource taxes
    - Capital Gains: Investment income
    """

    # Tax domain keywords for initial classification
    DOMAIN_KEYWORDS = {
        "CIT": ["corporate", "company", "cit", "profit", "business", "income", "enterprise", "corporation"],
        "VAT": ["vat", "value added", "tax invoice", "output tax", "input tax", "gst", "iva"],
        "Transfer Pricing": ["transfer pricing", "tp", "arm's length", "intercompany", "related party", "pricing", "comparable"],
        "PIT": ["personal income", "pit", "individual", "salary", "wage", "freelancer", "self-employed"],
        "FCT": ["foreign contractor", "fct", "service provider", "expatriate", "foreign worker", "withholding"],
        "DTA": ["double taxation", "dta", "tax treaty", "treaty", "vietnam treaty", "agreement"],
        "Customs": ["customs", "import", "export", "tariff", "duty", "border", "clearance"],
        "Excise Tax": ["excise", "special excise", "alcohol", "tobacco", "petrol", "fuel"],
        "Environmental Tax": ["environmental", "eco tax", "water", "waste", "forest", "environment"],
        "Capital Gains": ["capital gains", "investment", "stock", "capital", "asset sale", "profit on sale"]
    }

    def __init__(self, agent: Agent, memory_path: Path):
        """
        Initialize RequestCategorizer

        Args:
            agent: MemAgent instance (used for Llama, not for memory search)
            memory_path: Path to memory directory
        """
        super().__init__(agent, memory_path)
        self.agent = agent
        self.memory_path = Path(memory_path) if isinstance(memory_path, str) else memory_path

    def generate(self, request: str) -> AgentResult:
        """
        Classify tax request and suggest relevant categories

        Args:
            request: The client's tax question/request

        Returns:
            AgentResult with:
            - success: True if classification succeeded
            - output: {"suggested_categories": [...], "confidence": float}
            - metadata: Classification details
            - error: Empty string on success
        """
        try:
            logger.info(f"=== RequestCategorizer.generate() STARTED ===")
            logger.info(f"Input request: '{request[:100]}...' (length: {len(request)})")

            # Validate input
            if not request or len(request.strip()) < 10:
                logger.warning(f"Input validation failed: request too short (length: {len(request) if request else 0})")
                return AgentResult(
                    success=False,
                    output={},
                    metadata={
                        "error": "Request too short",
                        "min_length": 10,
                        "actual_length": len(request) if request else 0
                    },
                    timestamp=datetime.now().isoformat(),
                    error="Request must be at least 10 characters"
                )

            logger.info("Input validation passed")

            # Step 1: Keyword-based detection
            logger.info("Step 1: Running keyword-based classification...")
            request_lower = request.lower()
            keyword_scores = self._keyword_classification(request_lower)
            logger.debug(f"Keyword classification results: {keyword_scores}")

            # Step 2: Llama-based classification (for verification/nuance)
            logger.info("Step 2: Running Llama-based classification...")
            llama_scores = self._llama_classification(request)
            logger.debug(f"Llama classification results: {llama_scores}")

            # Step 3: Combine scores (weighted average)
            logger.info("Step 3: Combining keyword and Llama scores...")
            combined_scores = self._combine_scores(keyword_scores, llama_scores)
            logger.debug(f"Combined scores: {combined_scores}")

            # Step 4: Select top categories (threshold: >0.3)
            logger.info("Step 4: Selecting top categories (threshold > 0.3)...")
            suggested_categories = [
                cat for cat, score in combined_scores.items()
                if score > 0.3
            ]
            logger.info(f"Found {len(suggested_categories)} categories above threshold: {suggested_categories}")

            # If no categories found, return all with lower confidence
            if not suggested_categories:
                logger.warning("No categories above threshold, selecting top 3 by score...")
                suggested_categories = sorted(
                    combined_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]  # Return top 3
                suggested_categories = [cat for cat, _ in suggested_categories]
                logger.info(f"Selected fallback categories: {suggested_categories}")

            # Calculate overall confidence
            scores = [combined_scores.get(cat, 0) for cat in suggested_categories]
            avg_confidence = sum(scores) / len(scores) if scores else 0.5
            logger.info(f"Overall confidence score: {round(avg_confidence, 2)}")

            # Sort by confidence (highest first)
            suggested_categories.sort(
                key=lambda x: combined_scores.get(x, 0),
                reverse=True
            )
            logger.debug(f"Categories sorted by confidence: {suggested_categories}")

            # Format output
            output = {
                "suggested_categories": suggested_categories,
                "confidence": round(avg_confidence, 2),
                "confidence_by_category": {
                    cat: round(combined_scores.get(cat, 0), 2)
                    for cat in suggested_categories
                }
            }

            # Metadata for audit trail
            metadata = {
                "classification_method": "keyword + Llama (weighted)",
                "keyword_matches": {
                    cat: score for cat, score in keyword_scores.items()
                    if score > 0
                },
                "llama_scores": llama_scores,
                "combined_scores": {
                    cat: round(score, 2)
                    for cat, score in combined_scores.items()
                },
                "threshold": 0.3,
                "request_length": len(request),
                "categories_count": len(suggested_categories)
            }

            logger.info(f"=== RequestCategorizer.generate() COMPLETED SUCCESSFULLY ===")
            logger.info(f"Final output: {output}")
            logger.debug(f"Metadata: {metadata}")

            return AgentResult(
                success=True,
                output=output,
                metadata=metadata,
                timestamp=datetime.now().isoformat(),
                error=""
            )

        except Exception as e:
            logger.error(f"=== RequestCategorizer.generate() FAILED ===")
            log_agent_error(logger, "RequestCategorizer", "generate", e)
            return self._handle_error("RequestCategorizer classification", e)

    def _keyword_classification(self, request_lower: str) -> Dict[str, float]:
        """
        Classify request using keyword matching

        Args:
            request_lower: Request text in lowercase

        Returns:
            Dict mapping domain -> confidence score (0-1)
        """
        scores = {}

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            # Count keyword matches
            matches = sum(
                request_lower.count(keyword)
                for keyword in keywords
            )

            # Normalize to 0-1 range (cap at 5 matches = score 1.0)
            score = min(matches / 5, 1.0)
            scores[domain] = score

        return scores

    def _llama_classification(self, request: str) -> Dict[str, float]:
        """
        Use Llama to classify request and identify relevant domains.
        Llama responds in natural language, we extract domain mentions.

        Args:
            request: Original request text

        Returns:
            Dict mapping domain -> confidence score (0-1)
        """
        try:
            # Change 1A: Simplified natural language prompt (no JSON requirement)
            prompt = f"""Analyze this tax request and identify the relevant regulatory domains.

Tax Domains Available:
- CIT (Corporate Income Tax)
- VAT (Value Added Tax)
- Transfer Pricing (Intercompany pricing)
- PIT (Personal Income Tax)
- FCT (Foreign Contractor Tax)
- DTA (Double Taxation Agreements)
- Customs (Import/Export duties)
- Excise Tax (Special goods taxation)
- Environmental Tax (Pollution/resource taxes)
- Capital Gains (Investment income)

Request: {request}

For each relevant domain, briefly explain why it applies to this request.
List the domains in order of relevance."""

            logger.debug(f"Sending natural language prompt to Agent.generate_response()")
            response = self.agent.generate_response(prompt)
            logger.debug(f"Received response from Agent (length: {len(response)})")

            if not response:
                logger.error("Agent.generate_response() returned empty response")
                logger.info("Falling back to keyword-only classification")
                return {domain: 0.0 for domain in self.DOMAIN_KEYWORDS}

            logger.debug(f"Raw response (first 500 chars): {response[:500]}...")

            # Change 1B: Extract domains from natural language response
            domains_found = self._extract_domains_from_response(response)
            logger.info(f"Llama classification found domains: {domains_found}")
            return domains_found

        except Exception as e:
            logger.error(f"Llama classification error: {e}", exc_info=True)
            # Change 1C: Return error properly instead of neutral scores
            logger.info("Falling back to keyword-only classification")
            return {domain: 0.0 for domain in self.DOMAIN_KEYWORDS}

    def _extract_domains_from_response(self, llama_response: str) -> Dict[str, float]:
        """
        Extract domain scores from natural language Llama response.

        Llama mentions domains in the response. We count mentions and
        normalize to 0-1 score:
        - Mentioned once = 0.7
        - Mentioned twice+ = 0.9
        - Not mentioned = 0.0

        Args:
            llama_response: Natural language response from Llama

        Returns:
            Dict mapping domain -> confidence score (0-1)
        """
        response_lower = llama_response.lower()
        domains_found = {}

        for domain in self.DOMAIN_KEYWORDS.keys():
            # Count mentions of domain name
            domain_lower = domain.lower()
            count = response_lower.count(domain_lower)

            if count >= 2:
                # Domain mentioned multiple times - high relevance
                domains_found[domain] = 0.9
            elif count == 1:
                # Domain mentioned once - medium relevance
                domains_found[domain] = 0.7
            else:
                # Domain not mentioned - low relevance
                domains_found[domain] = 0.0

        logger.debug(f"Extracted domains from Llama response: {domains_found}")
        return domains_found

    def _combine_scores(
        self,
        keyword_scores: Dict[str, float],
        llama_scores: Dict[str, float],
        keyword_weight: float = 0.6,
        llama_weight: float = 0.4
    ) -> Dict[str, float]:
        """
        Combine keyword and Llama scores using weighted average

        Args:
            keyword_scores: Scores from keyword matching
            llama_scores: Scores from Llama classification
            keyword_weight: Weight for keyword scores (default 0.6)
            llama_weight: Weight for Llama scores (default 0.4)

        Returns:
            Dict mapping domain -> combined confidence score
        """
        combined = {}

        for domain in self.DOMAIN_KEYWORDS.keys():
            kw_score = keyword_scores.get(domain, 0)
            llama_score = llama_scores.get(domain, 0.5)

            # Weighted average
            combined_score = (kw_score * keyword_weight) + (llama_score * llama_weight)
            combined[domain] = max(0, min(combined_score, 1.0))

        return combined
