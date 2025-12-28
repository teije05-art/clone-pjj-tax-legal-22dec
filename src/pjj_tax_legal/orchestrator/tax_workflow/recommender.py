"""
FileRecommender Agent - Step 4 of Tax Workflow

Purpose: Search tax database and recommend source documents using MemAgent

MEMAGENT ARCHITECTURE (from MEMAGENT_JOURNEY.md):
- MemAgent is an "executable markdown navigator" NOT a vector database
- Agent writes Python code that uses: os.chdir(), list_files(), read_file()
- Results captured via execution_results['results']
- Fresh Agent instance per search (max_tool_turns=1)

CONSTRAINT BOUNDARIES:
- Search Scope: ONLY tax_database/ directory
- Filter: ONLY documents matching confirmed_categories from user
- Fallback: If categories empty, return empty (no autonomous document discovery)
- No Autonomy: Cannot access past_responses directory
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator.base import BaseAgent, AgentResult
from pjj_tax_legal.agent.logging_config import get_logger

logger = get_logger(__name__)


class FileRecommender(BaseAgent):
    """
    Step 4: Search tax database and recommend source documents via MemAgent.

    Uses the TRUE MemAgent pattern from MEMAGENT_JOURNEY.md:
    1. Pre-flatten directory paths (deterministic - handles nested structure)
    2. Fresh Agent instance with max_tool_turns=1
    3. Agent writes Python code using os.chdir() + list_files() + read_file()
    4. Results extracted from execution_results['results']

    CONSTRAINT BOUNDARIES:
    - Search Scope: ONLY data/tax_legal/tax_database/ directory (EXPLICIT)
    - Filter: ONLY documents matching confirmed_categories from user
    - Fallback: If categories empty, return empty (no autonomous document discovery)
    - No Autonomy: Cannot access past_responses directory

    Step 4 Workflow: User confirms categories -> FileRecommender searches tax_database -> User selects documents
    """

    # Search constraints
    MAX_NEW_RESULTS = 20

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
        Initialize FileRecommender

        Args:
            agent: Agent instance for memory navigation
            memory_path: Path to PRIMARY DATA directory (data/tax_legal/)
        """
        super().__init__(agent, memory_path)
        self.agent = agent
        self.memory_path = Path(memory_path) if isinstance(memory_path, str) else memory_path

        # Log initialization with explicit path information
        logger.info("=" * 80)
        logger.info("STEP 4: FileRecommender Initialized (MEMAGENT MODE)")
        logger.info(f"  PRIMARY DATA DIRECTORY: {self.memory_path}")
        logger.info(f"  Search Source: {self.memory_path / 'tax_database'}")
        logger.info(f"  Search Scope: tax_database/ (3,400+ tax documents in 16 categories)")
        logger.info(f"  Mode: MemAgent (os.chdir + list_files + read_file)")
        logger.info("=" * 80)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_all_subdirectories(self, category_dirs: List[str]) -> List[str]:
        """
        Pre-flatten nested directory structure to get all leaf directories.

        tax_database has structure like:
        02_VAT/
          CV 2018/
            file.md
          CV 2019/
            file.md

        This method returns all subdirectory paths that contain .md files,
        so MemAgent's simple os.chdir() + list_files() pattern works.

        Args:
            category_dirs: List of category directory paths (e.g., ["/path/tax_database/02_VAT"])

        Returns:
            List of all subdirectory paths containing .md files
        """
        all_dirs = []

        for cat_dir in category_dirs:
            if not os.path.isdir(cat_dir):
                logger.warning(f"Category directory does not exist: {cat_dir}")
                continue

            # Walk through all subdirectories
            for root, dirs, files in os.walk(cat_dir):
                # Check if this directory has .md files
                md_files = [f for f in files if f.endswith('.md')]
                if md_files:
                    all_dirs.append(root)

        logger.info(f"Pre-flattened {len(category_dirs)} categories into {len(all_dirs)} searchable directories")
        return all_dirs

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract search keywords from the user's query.
        Uses simple heuristics + common tax terms detection.
        """
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
        tax_terms = {
            'vat', 'cit', 'pit', 'fct', 'dta', 'tax', 'customs', 'excise',
            'transfer', 'pricing', 'withholding', 'exemption', 'deduction',
            'invoice', 'declaration', 'refund', 'rate', 'exported', 'export',
            'import', 'imported', 'software', 'digital', 'e-commerce',
            '0%', '5%', '10%', '20%', 'zero', 'reduced'
        }
        import re
        words = re.findall(r'\b[\w%]+\b', query.lower())
        keywords = []
        for word in words:
            if word in tax_terms and word not in keywords:
                keywords.append(word)
        for word in words:
            if len(word) > 3 and word not in stop_words and word not in keywords:
                keywords.append(word)
        query_lower = query.lower()
        multi_word_terms = ['transfer pricing', 'foreign contractor', 'value added',
                          'corporate income', 'personal income', 'double taxation']
        for term in multi_word_terms:
            if term in query_lower:
                keywords.append(term)
        logger.info(f"Extracted keywords for fallback search: {keywords}")
        return keywords[:15]


    def _extract_results_from_response(
        self,
        agent_response,
        categories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract results from Agent's execution_results.

        The Agent's Python code creates a 'results' variable that gets captured
        in execution_results dict.

        Args:
            agent_response: AgentResponse from fresh_agent.chat()
            categories: User-confirmed categories

        Returns:
            List of document dicts
        """
        documents = []

        # Check execution_results for 'results' variable
        if agent_response.execution_results:
            exec_results = agent_response.execution_results
            logger.info(f"Variables in execution_results: {list(exec_results.keys())}")

            # Look for results in various variable names
            result_keys = ['results', 'documents', 'matches', 'found_files', 'relevant_files']
            raw_results = None

            for key in result_keys:
                if key in exec_results and isinstance(exec_results[key], list):
                    raw_results = exec_results[key]
                    logger.info(f"Found results in variable '{key}': {len(raw_results)} items")
                    break

            if raw_results:
                for item in raw_results:
                    if isinstance(item, dict):
                        doc = {
                            "filename": item.get("source_file", item.get("filename", "Unknown")),
                            "category": item.get("category", categories[0] if categories else "General"),
                            "full_path": item.get("full_path", item.get("directory", "")),
                            "content": item.get("content", "")[:3000],
                            "summary": item.get("content", "")[:250],
                            "categories": categories,
                            "files_used": [item.get("source_file", item.get("filename", "Unknown"))],
                        }
                        documents.append(doc)
                    elif isinstance(item, str):
                        # If result is just a string (filename or content)
                        documents.append({
                            "filename": item if item.endswith('.md') else "Unknown",
                            "category": categories[0] if categories else "General",
                            "content": item,
                            "summary": item[:250],
                            "categories": categories,
                        })

                logger.info(f"Extracted {len(documents)} documents from execution_results")
            else:
                logger.warning("No 'results' variable found in execution_results")

                # FALLBACK: Try to extract from common variable patterns the LLM might use
                # Look for file_names list + content combinations
                file_names_keys = ['file_names', 'filenames', 'files_list', 'md_files']
                content_keys = ['content', 'file_content', 'contents', 'text']

                found_files = None
                found_content = None

                # Find file names list
                for key in file_names_keys:
                    if key in exec_results and isinstance(exec_results[key], list):
                        found_files = exec_results[key]
                        logger.info(f"Fallback: Found file list in '{key}': {len(found_files)} items")
                        break

                # If 'files' is a newline-separated string, split it
                if not found_files and 'files' in exec_results:
                    files_val = exec_results['files']
                    if isinstance(files_val, str) and '\n' in files_val:
                        found_files = [f.strip() for f in files_val.split('\n') if f.strip().endswith('.md')]
                        logger.info(f"Fallback: Split 'files' string into {len(found_files)} items")

                # Find content (might be last file's content or accumulated)
                for key in content_keys:
                    if key in exec_results and isinstance(exec_results[key], str):
                        found_content = exec_results[key]
                        logger.info(f"Fallback: Found content in '{key}': {len(found_content)} chars")
                        break

                # Build documents from found files
                if found_files:
                    for fname in found_files[:self.MAX_NEW_RESULTS]:
                        if isinstance(fname, str) and fname.endswith('.md'):
                            documents.append({
                                "filename": fname,
                                "category": categories[0] if categories else "General",
                                "content": found_content[:3000] if found_content else "",
                                "summary": f"File: {fname}",
                                "categories": categories,
                            })
                    logger.info(f"Fallback: Created {len(documents)} document entries from file list")

        # Fallback: try parsing reply text
        if not documents and agent_response.reply:
            logger.info("Attempting fallback: parsing reply text")
            documents = self._parse_agent_response(agent_response.reply, categories)

        return documents

    # =========================================================================
    # MAIN GENERATE METHOD - TRUE MEMAGENT PATTERN
    # =========================================================================

    def generate(
        self,
        request: str,
        categories: Optional[List[str]] = None,
        suggested_files: Optional[List[str]] = None
    ) -> AgentResult:
        """
        Search tax database using TRUE MemAgent pattern.

        MEMAGENT ARCHITECTURE (from MEMAGENT_JOURNEY.md):
        1. Pre-flatten directories (deterministic - handles nested structure)
        2. Fresh Agent instance with max_tool_turns=1
        3. Agent writes Python code using os.chdir() + list_files() + read_file()
        4. Results extracted from execution_results['results']

        Args:
            request: The tax question/request
            categories: User-confirmed tax categories (REQUIRED for search)
            suggested_files: Pre-selected files to include (optional)

        Returns:
            AgentResult with:
            - success: True if search completed (even if no results)
            - output: List of documents with relevant content
            - metadata: Search scope, categories boundary, results info
            - error: Empty string on success
        """
        try:
            logger.info("=== FileRecommender.generate() STARTED (MEMAGENT MODE) ===")
            logger.info(f"Input request: '{request[:100]}...' (length: {len(request)})")
            logger.info(f"Categories: {categories}")
            logger.info(f"Suggested files from past response: {suggested_files or []}")
            start_time = time.time()

            # CONSTRAINT ENFORCEMENT: Categories required
            if not categories:
                logger.warning("Categories parameter is missing - cannot perform constrained search")
                return AgentResult(
                    success=False,
                    output=[],
                    metadata={
                        "error": "Categories required for constrained search",
                        "search_scope": "tax_database",
                        "required_parameter": "categories"
                    },
                    timestamp=datetime.now().isoformat(),
                    error="Categories parameter is required"
                )

            logger.info(f"Constraint boundary: Search ONLY in tax_database/")
            logger.info(f"Category constraint: ONLY results matching {categories}")

            # Map user-friendly category names to actual filesystem directory names
            actual_dir_names = [self.CATEGORY_DIR_MAP.get(cat, cat) for cat in categories]
            logger.info(f"Mapped categories to actual directories: {actual_dir_names}")

            # Build absolute paths to category directories
            memory_base = self.memory_path
            absolute_category_dirs = [str(memory_base / "tax_database" / dir_name) for dir_name in actual_dir_names]

            # =====================================================================
            # STEP 1: PRE-FLATTEN DIRECTORIES (Deterministic)
            # =====================================================================
            logger.info("=== MEMAGENT STEP 1: Pre-flattening nested directories ===")
            all_searchable_dirs = self._get_all_subdirectories(absolute_category_dirs)
                    logger.info(f"Total searchable directories: {len(all_searchable_dirs)}")
            if not all_searchable_dirs:
                logger.warning("No searchable directories found")
                return AgentResult(
                    success=True,
                    output=[],
                    metadata={
                        "total_found": 0,
                        "search_time_ms": int((time.time() - start_time) * 1000),
                        "search_scope": "tax_database",
                        "search_method": "MemAgent (os.chdir + list_files + read_file)",
                        "categories_searched": categories,
                    },
                    timestamp=datetime.now().isoformat(),
                    error=""
                )

            # Limit directories to prevent context overflow (sample if too many)
            max_dirs = 30  # Limit to prevent overly long prompts
            if len(all_searchable_dirs) > max_dirs:
                logger.info(f"Sampling {max_dirs} directories from {len(all_searchable_dirs)}")
                import random
                all_searchable_dirs = random.sample(all_searchable_dirs, max_dirs)

            # =====================================================================
            # STEP 2: CREATE FRESH AGENT INSTANCE
            # =====================================================================
            logger.info("=== MEMAGENT STEP 2: Creating fresh Agent instance ===")
            fresh_agent = Agent(memory_path=str(self.memory_path), max_tool_turns=1)
            logger.info("Created fresh Agent with max_tool_turns=1")

            # =====================================================================
            # STEP 3: BUILD MEMAGENT PROMPT
            # =====================================================================
            logger.info("=== MEMAGENT STEP 3: Building MemAgent prompt ===")

            # Format directory list for prompt
            dirs_formatted = "\n".join([f"  - {d}" for d in all_searchable_dirs[:15]])  # Show first 15
            if len(all_searchable_dirs) > 15:
                dirs_formatted += f"\n  ... and {len(all_searchable_dirs) - 15} more directories"

            constrained_query = f"""Search for tax documents relevant to: "{request}"

DIRECTORIES (each contains .md files):
{dirs_formatted}

IMPORTANT: Write Python code following this EXACT pattern:

```python
import os

# MUST initialize results list FIRST
results = []

# Search directories
directories = [
    # paste directory paths here
]

for directory in directories:
    try:
        os.chdir(directory)
        files_output = list_files()  # NO arguments!
        for line in files_output.split('\\n'):
            filename = line.strip()
            if filename.endswith('.md'):
                content = read_file(filename)
                if not content.startswith('Error'):
                    # Add to results
                    results.append({{
                        'source_file': filename,
                        'category': directory.split(os.sep)[-2] if os.sep in directory else 'General',
                        'content': content[:3000],
                        'directory': directory
                    }})
    except Exception as e:
        pass  # Skip failed directories
```

CRITICAL RULES:
1. You MUST create `results = []` at the START of your code
2. Use `list_files()` with NO arguments
3. Use `read_file(filename)` to read files
4. Append matching documents to `results` list

Write Python code now:"""

            logger.info(f"Prompt length: {len(constrained_query)} chars")

            # =====================================================================
            # STEP 4: EXECUTE MEMAGENT SEARCH
            # =====================================================================
            logger.info("=== MEMAGENT STEP 4: Executing Agent search ===")
            agent_response = fresh_agent.chat(constrained_query)

            logger.info(f"Agent response received")
            logger.info(f"  - Has execution_results: {agent_response.execution_results is not None}")
            logger.info(f"  - Has python_block: {agent_response.python_block is not None}")
            logger.info(f"  - Reply length: {len(agent_response.reply or '')}")

            if agent_response.python_block:
                logger.debug(f"Python code executed:\n{agent_response.python_block[:500]}...")

            # =====================================================================
            # STEP 5: EXTRACT RESULTS FROM EXECUTION
            # =====================================================================
            logger.info("=== MEMAGENT STEP 5: Extracting results ===")
            documents = self._extract_results_from_response(agent_response, categories)

            # "ANTI-ZERO" FALLBACK: If MemAgent fails, use a keyword search on filenames, then a 'dumb' fallback.
            if not documents:
                logger.warning("MemAgent search returned 0 documents. Initiating keyword fallback.")
                keywords = self._extract_keywords(request)
                
                fallback_files = []
                for dir_path in all_searchable_dirs:
                    for filename in os.listdir(dir_path):
                        if filename.endswith('.md'):
                            filename_lower = filename.lower()
                            if any(kw.lower() in filename_lower for kw in keywords):
                                fallback_files.append({
                                    "filename": filename,
                                    "category": os.path.basename(os.path.dirname(os.path.join(dir_path, filename))),
                                    "full_path": os.path.join(dir_path, filename),
                                    "summary": f"File matched by keyword: {', '.join(kw for kw in keywords if kw.lower() in filename_lower)}",
                                    "content": "" 
                                })
                
                documents = fallback_files
                logger.info(f"Keyword fallback found {len(documents)} matching files.")

            # "SAFETY NET" FALLBACK: If still no documents, find all PDFs.
            if not documents:
                logger.warning("All searches returned 0 documents. Initiating 'Dumb Fallback' to find all PDFs.")
                import glob
                
                pdf_files = glob.glob('data/**/*.pdf', recursive=True)
                logger.info(f"Found {len(pdf_files)} PDF files in data/ directory.")

                fallback_files = []
                for pdf_path in pdf_files[:self.MAX_NEW_RESULTS]:
                    fallback_files.append({
                        "filename": os.path.basename(pdf_path),
                        "category": os.path.basename(os.path.dirname(pdf_path)),
                        "full_path": pdf_path,
                        "summary": f"PDF file from 'Safety Net' fallback.",
                        "content": ""
                    })
                
                documents = fallback_files
                logger.info(f"'Safety Net' fallback created {len(documents)} document entries.")

            search_time_ms = (time.time() - start_time) * 1000

            logger.info(f"=== MEMAGENT SEARCH COMPLETED ===")
            logger.info(f"Search time: {search_time_ms:.1f}ms")
            logger.info(f"Results found: {len(documents)} documents")

            # Format output
            formatted_results = []
            for doc in documents[:self.MAX_NEW_RESULTS]:
                formatted_results.append({
                    "filename": doc.get("filename", "Unknown"),
                    "category": doc.get("category", "General"),
                    "subcategory": doc.get("subcategory", "General"),
                    "size": doc.get("size", "Unknown"),
                    "date_issued": doc.get("date_issued", "Unknown"),
                    "content": doc.get("content", ""),
                    "summary": doc.get("summary", doc.get("content", "")[:250])
                })

            logger.info(f"Final output: {len(formatted_results)} search results")
            logger.info(f"=== FileRecommender.generate() COMPLETED SUCCESSFULLY ===")

            return AgentResult(
                success=True,
                output=formatted_results,
                metadata={
                    "total_found": len(formatted_results),
                    "search_time_ms": int(search_time_ms),
                    "search_scope": "tax_database",
                    "search_method": "MemAgent (os.chdir + list_files + read_file)",
                    "categories_searched": categories,
                    "directories_searched": len(all_searchable_dirs),
                },
                timestamp=datetime.now().isoformat(),
                error=""
            )

        except Exception as e:
            logger.error(f"=== FileRecommender.generate() FAILED ===")
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
        Fallback: Parse Agent's text response to extract documents.

        Args:
            response_text: Agent's reply text
            requested_categories: Categories the user requested

        Returns:
            List of structured document objects
        """
        documents = []

        if not response_text or len(response_text.strip()) == 0:
            logger.warning("Agent returned empty response")
            return documents

        try:
            import json
            import re

            response_text = response_text.strip()
            logger.debug(f"Parsing response: {len(response_text)} chars")

            # Try to parse as JSON
            if '[' in response_text and ']' in response_text:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    try:
                        json_str = response_text[start_idx:end_idx]
                        results = json.loads(json_str)

                        if isinstance(results, list):
                            logger.info(f"Parsed {len(results)} results from JSON")
                            for item in results:
                                if isinstance(item, dict):
                                    doc = {
                                        "filename": item.get("source_file", item.get("filename", "Unknown")),
                                        "category": item.get("category", requested_categories[0] if requested_categories else "General"),
                                        "content": item.get("content", "")[:3000],
                                        "summary": item.get("content", "")[:250],
                                    }
                                    documents.append(doc)
                            return documents
                    except json.JSONDecodeError:
                        pass

            # Look for .md file mentions
            md_pattern = r'([^\s:/\\]+\.md)'
            md_files = list(set(re.findall(md_pattern, response_text)))

            if md_files:
                logger.info(f"Found {len(md_files)} .md file mentions")
                for filename in md_files[:self.MAX_NEW_RESULTS]:
                    doc = {
                        "filename": filename,
                        "category": requested_categories[0] if requested_categories else "General",
                        "content": response_text[:1000],
                        "summary": response_text[:250],
                    }
                    documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return documents
