"""
TaxResponseSearcher - Step 2 Agent

Searches past approved tax responses using MemAgent.
Returns similar cases that might directly answer the current request.

CONSTRAINT BOUNDARIES (CRITICAL):
- Search source: past_responses directory ONLY
- NO autonomous search: Requires confirmed_categories from user
- Query constraint: CONSTRAINT text in query enforces category filtering
- Result filtering: Only returns results matching user-selected categories
- Metadata tracking: Return search scope, category_boundary, results_filtered_count

If categories is empty → returns empty (no fallback to broad search)
If no matches found → returns empty list (not error)
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator.base import BaseAgent, AgentResult
from pjj_tax_legal.agent.logging_config import get_logger, log_search_query, log_search_results

logger = get_logger(__name__)


class TaxResponseSearcher(BaseAgent):
    """
    Searches past tax responses via HYBRID approach:
    - Deterministic file reading (reliable, no truncation)
    - Gemini for semantic understanding (keyword extraction) with a deterministic fallback.

    CONSTRAINT BOUNDARIES:
    - Search Scope: ONLY past_responses/ directory
    - Filter: ONLY responses matching confirmed_categories from user
    - Fallback: If categories empty, return empty (no autonomous search)
    - No Autonomy: Cannot search beyond past responses, cannot search without categories

    HYBRID ARCHITECTURE:
    1. Deterministic: Read all files in category directories.
    2. Semantic: Use Gemini to extract keywords from query (with deterministic fallback).
    3. Deterministic: Filter files containing keywords (in content or filename).
    4. Deterministic: Extract relevant paragraphs from matching files.
    """

    # Search constraints
    MAX_RESULTS = 15

    # Category to directory mapping (numbered prefixes in actual filesystem)
    CATEGORY_DIR_MAP = {
        "CIT": "01_CIT",
        "VAT": "02_VAT",
        "Customs": "03_Customs",
        "PIT": "04_PIT",
        "DTA": "05_DTA",
        "Transfer Pricing": "06_Transfer_Pricing",
        "FCT": "07_FCT",
        "Tax Administration": "08_Tax_Administration",
        "Excise Tax": "09_Excise_Tax_SST",
        "Natural Resources": "10_Natural_Resources_SHUI",
        "Draft Regulations": "11_Draft_Regulations",
        "Capital Gains": "12_Capital_Gains_Tax_CGT",
        "Environmental Tax": "13_Environmental_Protection_EPT",
        "Immigration": "14_Immigration_Work_Permits",
        "E-Commerce": "15_E_Commerce",
        "Business Support": "16_Business_Support_Measures",
        "General Policies": "17_General_Policies",
        "Miscellaneous": "18_Miscellaneous"
    }

    def __init__(self, agent: Agent, memory_path: Path):
        """
        Initialize TaxResponseSearcher

        Args:
            agent: Agent instance for memory navigation
            memory_path: Path to PRIMARY DATA directory (data/tax_legal/)
        """
        super().__init__(agent, memory_path)
        self.agent = agent
        self.memory_path = Path(memory_path) if isinstance(memory_path, str) else memory_path

        # Log initialization with explicit path information
        logger.info("=" * 80)
        logger.info("STEP 2: TaxResponseSearcher Initialized (HYBRID MODE)")
        logger.info(f"  PRIMARY DATA DIRECTORY: {self.memory_path}")
        logger.info(f"  Search Source: {self.memory_path / 'past_responses'}")
        logger.info(f"  Search Scope: past_responses/ (approved tax responses)")
        logger.info(f"  Mode: HYBRID (deterministic file I/O + Gemini semantic extraction)")
        logger.info("=" * 80)

    # =========================================================================
    # HYBRID HELPER METHODS
    # =========================================================================

    def _read_file_content(self, file_path: str) -> str:
        """
        Read file content and skip YAML frontmatter.

        Args:
            file_path: Path to the file to read

        Returns:
            File content with YAML frontmatter removed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip YAML frontmatter (content between first '---' and second '---')
            if content.startswith('---'):
                second_marker = content.find('---', 3)
                if second_marker > 0:
                    content = content[second_marker + 3:].strip()

            return content
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            return ""

    def _get_semantic_keywords_with_gemini(self, query: str) -> List[str]:
        """
        Use Gemini to extract semantic search keywords from the user's query.
        """
        try:
            prompt = (
                f"Extract the most relevant and specific search keywords from the following tax-related query. "
                f"Focus on tax types (e.g., VAT, CIT), actions (e.g., export, import, transfer), and key subjects (e.g., software, services, royalties). "
                f"Return a comma-separated list of keywords.\n\nQuery: \"{query}\""
            )
            
            # Use the agent's generate_text method for a direct LLM call
            response = self.agent.generate_text(prompt)
            
            if response:
                keywords = [kw.strip() for kw in response.split(',') if kw.strip()]
                logger.info(f"Extracted semantic keywords from Gemini: {keywords}")
                return keywords
            else:
                logger.warning("Gemini returned an empty response for keyword extraction.")
                return []
        except Exception as e:
            logger.error(f"Error during Gemini keyword extraction: {e}")
            return []

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract search keywords from the user's query.
        Uses simple heuristics + common tax terms detection.

        Args:
            query: The user's search query

        Returns:
            List of keywords to search for
        """
        # Common words to exclude
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but',
            'if', 'or', 'because', 'until', 'while', 'what', 'which', 'who',
            'this', 'that', 'these', 'those', 'am', 'it', 'its', 'my', 'your',
            'our', 'their', 'his', 'her', 'we', 'you', 'they', 'i', 'me', 'him',
            'us', 'them', 'apply', 'applied', 'conditions', 'must', 'satisfied',
            'clients', 'services', 'company', 'companies'
        }

        # Important tax-related terms to always include if present
        tax_terms = {
            'vat', 'cit', 'pit', 'fct', 'dta', 'tax', 'customs', 'excise',
            'transfer', 'pricing', 'withholding', 'exemption', 'deduction',
            'invoice', 'declaration', 'refund', 'rate', 'exported', 'export',
            'import', 'imported', 'software', 'digital', 'e-commerce',
            '0%', '5%', '10%', '20%', 'zero', 'reduced'
        }

        # Extract words from query
        import re
        words = re.findall(r'\b[\w%]+\b', query.lower())

        # Filter and prioritize
        keywords = []

        # First add tax terms found in query
        for word in words:
            if word in tax_terms and word not in keywords:
                keywords.append(word)

        # Then add other significant words (length > 3, not stop words)
        for word in words:
            if len(word) > 3 and word not in stop_words and word not in keywords:
                keywords.append(word)

        # Also check for multi-word terms
        query_lower = query.lower()
        multi_word_terms = ['transfer pricing', 'foreign contractor', 'value added',
                          'corporate income', 'personal income', 'double taxation']
        for term in multi_word_terms:
            if term in query_lower:
                keywords.append(term)

        logger.info(f"Extracted keywords from query: {keywords}")
        return keywords[:15]  # Limit to 15 keywords

    def _extract_relevant_paragraphs(self, content: str, keywords: List[str], max_chars: int = 3000) -> str:
        """
        Extract paragraphs from content that contain any of the keywords.

        Args:
            content: The full file content
            keywords: List of keywords to search for
            max_chars: Maximum characters to return

        Returns:
            Extracted relevant paragraphs concatenated
        """
        if not content or not keywords:
            return content[:max_chars] if content else ""

        # Split into paragraphs
        paragraphs = content.split('\n\n')

        relevant_paragraphs = []
        total_chars = 0

        content_lower = content.lower()

        for para in paragraphs:
            para = para.strip()
            if not para or len(para) < 20:
                continue

            para_lower = para.lower()

            # Check if paragraph contains any keyword
            contains_keyword = any(kw.lower() in para_lower for kw in keywords)

            if contains_keyword:
                if total_chars + len(para) <= max_chars:
                    relevant_paragraphs.append(para)
                    total_chars += len(para) + 2  # +2 for newlines
                else:
                    # Add partial paragraph if we have room
                    remaining = max_chars - total_chars
                    if remaining > 100:
                        relevant_paragraphs.append(para[:remaining] + "...")
                    break

        if relevant_paragraphs:
            return '\n\n'.join(relevant_paragraphs)
        else:
            # Fallback: return first max_chars if no keyword matches
            return content[:max_chars]

    def _read_all_files_in_directories(self, directories: List[str]) -> List[Dict[str, Any]]:
        """
        Deterministically read all .md files in the specified directories.

        Args:
            directories: List of directory paths to search

        Returns:
            List of dicts with file info and content
        """
        import os
        all_files = []

        for dir_path in directories:
            if not os.path.isdir(dir_path):
                logger.warning(f"Directory does not exist: {dir_path}")
                continue

            dir_name = os.path.basename(dir_path)

            for filename in os.listdir(dir_path):
                if not filename.endswith('.md'):
                    continue

                file_path = os.path.join(dir_path, filename)
                content = self._read_file_content(file_path)

                if content:
                    all_files.append({
                        'filename': filename,
                        'directory': dir_name,
                        'full_path': file_path,
                        'content': content
                    })

        logger.info(f"Read {len(all_files)} .md files from {len(directories)} directories")
        return all_files

    # =========================================================================
    # MAIN GENERATE METHOD
    # =========================================================================

    def generate(
        self,
        request: str,
        categories: Optional[List[str]] = None
    ) -> AgentResult:
        """
        Search past tax responses using HYBRID approach.

        HYBRID ARCHITECTURE:
        1. Deterministic: Read all files in category directories.
        2. Semantic: Use Gemini to extract keywords from query (with deterministic fallback).
        3. Deterministic: Filter files containing keywords (in content or filename).
        4. Deterministic: Extract relevant paragraphs from matching files.

        Args:
            request: The tax question/request
            categories: User-confirmed tax categories (REQUIRED for search)

        Returns:
            AgentResult with:
            - success: True if search completed (even if no results)
            - output: List of past responses with relevant content
            - metadata: Search scope, categories boundary, results info
            - error: Empty string on success
        """
        try:
            logger.info("=== TaxResponseSearcher.generate() STARTED (HYBRID MODE) ===")
            logger.info(f"Input request: '{request[:100]}...' (length: {len(request)})")
            logger.info(f"Categories: {categories}")
            start_time = time.time()

            # CONSTRAINT ENFORCEMENT: Categories required
            if not categories:
                logger.warning("Categories parameter is missing - cannot perform constrained search")
                return AgentResult(
                    success=False,
                    output=[],
                    metadata={
                        "error": "Categories required for constrained search",
                        "search_scope": "past_responses",
                        "required_parameter": "categories"
                    },
                    timestamp=datetime.now().isoformat(),
                    error="Categories parameter is required"
                )

            logger.info(f"Constraint boundary: Search ONLY in past_responses/")
            logger.info(f"Category constraint: ONLY results matching {categories}")

            # Map categories to actual directory names
            category_dirs = [str(Path("past_responses") / self.CATEGORY_DIR_MAP.get(cat, cat)) for cat in categories]
            logger.info(f"Mapped category directories: {category_dirs}")

            # Build absolute paths
            memory_base = Path(self.memory_path)
            absolute_category_dirs = [str(memory_base / d) for d in category_dirs]

            # =====================================================================
            # STEP 1: DETERMINISTIC FILE READING
            # =====================================================================
            logger.info("=== HYBRID STEP 1: Reading all files (deterministic) ===")
            all_files = self._read_all_files_in_directories(absolute_category_dirs)
            logger.info(f"Total files read: {len(all_files)}")

            if not all_files:
                logger.warning("No files found in specified directories")
                return AgentResult(
                    success=True,
                    output=[],
                    metadata={
                        "total_found": 0,
                        "search_time_ms": int((time.time() - start_time) * 1000),
                        "search_scope": "past_responses",
                        "search_method": "HYBRID (deterministic file I/O + keyword extraction)",
                        "categories_searched": categories,
                    },
                    timestamp=datetime.now().isoformat(),
                    error=""
                )

            # =====================================================================
            # STEP 2: EXTRACT KEYWORDS FROM QUERY
            # =====================================================================
            logger.info("=== HYBRID STEP 2: Extracting keywords (semantic + deterministic) ===")
            # Try semantic keyword extraction with Gemini first
            keywords = self._get_semantic_keywords_with_gemini(request)
            if not keywords:
                # Fallback to deterministic keyword extraction
                logger.info("Semantic keyword extraction failed, falling back to deterministic method.")
                keywords = self._extract_keywords(request)
            logger.info(f"Keywords for search: {keywords}")

            # =====================================================================
            # STEP 3: FILTER FILES CONTAINING KEYWORDS
            # =====================================================================
            logger.info("=== HYBRID STEP 3: Filtering files by keywords ===")
            matching_files = []
            for file_info in all_files:
                content_lower = file_info['content'].lower()
                # Check if any keyword is in the content
                if any(kw.lower() in content_lower for kw in keywords):
                    matching_files.append(file_info)

            logger.info(f"Files matching keywords in content: {len(matching_files)} out of {len(all_files)}")

            # If no keyword matches in content, fall back to searching filenames
            if not matching_files:
                logger.info("No keyword matches in content, falling back to searching filenames.")
                for file_info in all_files:
                    filename_lower = file_info['filename'].lower()
                    if any(kw.lower() in filename_lower for kw in keywords):
                        matching_files.append(file_info)

            # If still no matches, use all files as a final fallback
            if not matching_files:
                logger.info("No keyword matches in filenames, using all files as a final fallback.")
                matching_files = sorted(all_files, key=lambda x: len(x['content']), reverse=True)

            # =====================================================================
            # STEP 4: EXTRACT RELEVANT PARAGRAPHS
            # =====================================================================
            logger.info("=== HYBRID STEP 4: Extracting relevant paragraphs ===")
            past_responses = []

            for file_info in matching_files[:self.MAX_RESULTS]:
                # Extract relevant paragraphs containing keywords
                relevant_content = self._extract_relevant_paragraphs(
                    file_info['content'],
                    keywords,
                    max_chars=3000
                )

                if relevant_content:
                    past_responses.append({
                        "filename": file_info['filename'],
                        "full_path": file_info['full_path'],
                        "content": relevant_content,
                        "summary": relevant_content[:250] if relevant_content else "No relevant content found",
                        "categories": categories,
                        "files_used": [file_info['filename']],
                        "date_created": "Unknown"
                    })

            search_time_ms = (time.time() - start_time) * 1000

            logger.info(f"=== HYBRID SEARCH COMPLETED ===")
            logger.info(f"Search time: {search_time_ms:.1f}ms")
            logger.info(f"Results found: {len(past_responses)} past responses")

            # Format output
            formatted_results = []
            for result in past_responses:
                formatted_results.append({
                    "filename": result.get("filename", "Unknown"),
                    "content": result.get("content", ""),
                    "summary": result.get("summary", ""),
                    "categories": result.get("categories", []),
                    "files_used": result.get("files_used", []),
                    "date_created": result.get("date_created", "Unknown")
                })

            logger.info(f"Final formatted output: {len(formatted_results)} past responses")
            logger.info(f"=== TaxResponseSearcher.generate() COMPLETED SUCCESSFULLY ===")

            return AgentResult(
                success=True,
                output=formatted_results,
                metadata={
                    "total_found": len(formatted_results),
                    "search_time_ms": int(search_time_ms),
                    "search_scope": "past_responses",
                    "search_method": "HYBRID (deterministic file I/O + keyword extraction)",
                    "categories_searched": categories,
                    "keywords_used": keywords,
                    "files_scanned": len(all_files),
                    "files_matched": len(matching_files),
                },
                timestamp=datetime.now().isoformat(),
                error=""
            )

        except Exception as e:
            logger.error(f"=== TaxResponseSearcher.generate() FAILED ===")
            logger.error(f"Exception: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                output=[],
                metadata={"error_type": "search_error"},
                timestamp=datetime.now().isoformat(),
                error=f"Search failed: {str(e)}"
            )

    def _parse_agent_response(
        self,
        response_text: str,
        requested_categories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Parse Agent's Python code execution response to extract past responses.

        Agent executes Python code that creates a 'results' variable containing:
        [
            {
                "source_file": "filename.md",
                "section_title": "Section Title",
                "relevance": "Why this is relevant",
                "content": "actual extracted text",
                "directory": "past_responses/XX_Category/"
            },
            ...
        ]

        Args:
            response_text: Agent's response after Python code execution
            requested_categories: Categories the user requested

        Returns:
            List of structured past response objects with full content
        """
        past_responses = []

        if not response_text or len(response_text.strip()) == 0:
            logger.warning("Agent returned empty response - likely no files found in directories")
            return past_responses

        try:
            response_text = response_text.strip()
            logger.debug(f"=== PARSING AGENT RESPONSE ===")
            logger.debug(f"Full response length: {len(response_text)} chars")
            logger.debug(f"Response preview: {response_text[:500]}...")

            # Try to parse as JSON first (Agent may return structured JSON)
            import json
            try:
                # Check if response contains a JSON list
                if '[' in response_text and ']' in response_text:
                    # Extract FIRST complete JSON array from response
                    # This handles cases where JSON is printed multiple times
                    start_idx = response_text.find('[')
                    if start_idx >= 0:
                        # Find the matching closing bracket for this JSON array
                        bracket_count = 0
                        end_idx = start_idx
                        for i in range(start_idx, len(response_text)):
                            if response_text[i] == '[':
                                bracket_count += 1
                            elif response_text[i] == ']':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    end_idx = i + 1
                                    break

                        if end_idx > start_idx:
                            json_str = response_text[start_idx:end_idx]
                            logger.debug(f"Attempting to parse JSON: {json_str[:200]}...")
                            results = json.loads(json_str)

                            if isinstance(results, list):
                                logger.info(f"Parsed {len(results)} results from JSON")
                                for item in results:
                                    if isinstance(item, dict) and "source_file" in item and "content" in item:
                                        response = {
                                            "filename": item.get("source_file", "Unknown"),
                                            "section_title": item.get("section_title", "General"),
                                            "relevance": item.get("relevance", "Matching category"),
                                            "summary": item.get("content", ""),
                                            "categories": requested_categories,
                                            "files_used": [item.get("source_file", "Unknown")],
                                            "date_created": "Unknown"
                                        }
                                        past_responses.append(response)
                                        logger.debug(f"Extracted: {response['filename']} - {response['section_title']}")

                                logger.info(f"Parsed {len(past_responses)} past responses from JSON")
                                if len(past_responses) > 0:
                                    return past_responses
            except (json.JSONDecodeError, Exception) as e:
                logger.debug(f"JSON parsing failed ({str(e)}), trying alternative parsing methods")

            # Parse plain text structured format
            # Look for patterns like "Source File: name.md", "Section Title: title", etc.
            logger.info("Agent likely returned plain text structured response - parsing fields...")

            import re
            sections = re.split(r'\n\s*-{3,}\s*\n|\n\s*\n', response_text)

            for section in sections:
                if not section.strip() or len(section.strip()) < 20:
                    continue

                # Extract structured fields using patterns (case-insensitive)
                source_file_match = re.search(r'(?:Source\s+File|source_file|^\s*File)\s*:\s*([^\n]+\.md)', section, re.IGNORECASE | re.MULTILINE)
                title_match = re.search(r'(?:Section\s+Title|Section|Title)\s*:\s*([^\n]+)', section, re.IGNORECASE)
                relevance_match = re.search(r'(?:Relevance|Relevant|Directory)\s*:\s*([^\n]+)', section, re.IGNORECASE)
                content_match = re.search(r'(?:Content|Section\s+Content)\s*:\s*(.+?)(?:\n(?:\*|Source|Section|Directory|File)|$)', section, re.IGNORECASE | re.DOTALL)

                source_file = source_file_match.group(1).strip() if source_file_match else None
                section_title = title_match.group(1).strip() if title_match else "Extracted Section"
                relevance = relevance_match.group(1).strip() if relevance_match else "Matching query"

                # Get content
                if content_match:
                    content = content_match.group(1).strip()[:3000]
                else:
                    content = section.strip()[:1000]

                if source_file:
                    response = {
                        "filename": source_file,
                        "section_title": section_title,
                        "relevance": relevance,
                        "content": content,  # Full 3000 chars for synthesis
                        "summary": content[:250],  # First 250 chars for display
                        "categories": requested_categories,
                        "files_used": [source_file],
                        "date_created": "Unknown"
                    }
                    past_responses.append(response)
                    logger.debug(f"Extracted: {source_file} - {section_title}")

            if past_responses:
                logger.info(f"Parsed {len(past_responses)} past responses from structured text")
                return past_responses

            # Fallback: look for any .md file mentions
            logger.info("Fallback: searching for .md file mentions...")
            md_pattern = r'([^\s:/\\]+\.md)'
            md_files = re.findall(md_pattern, response_text)

            if md_files:
                logger.info(f"Found {len(set(md_files))} .md file mentions")
                for filename in list(set(md_files))[:self.MAX_RESULTS]:
                    response = {
                        "filename": filename,
                        "section_title": "Extracted Section",
                        "relevance": "Matching query",
                        "summary": response_text[:1000],
                        "categories": requested_categories,
                        "files_used": [filename],
                        "date_created": "Unknown"
                    }
                    past_responses.append(response)

            if not past_responses:
                logger.warning(f"Could not parse any past responses from Agent output")

            logger.info(f"Parsed {len(past_responses)} past responses from Agent response")
            return past_responses

        except Exception as e:
            logger.error(f"Error parsing Agent response: {e}", exc_info=True)
            logger.warning(f"Response text was: {response_text[:500]}...")
            return past_responses
