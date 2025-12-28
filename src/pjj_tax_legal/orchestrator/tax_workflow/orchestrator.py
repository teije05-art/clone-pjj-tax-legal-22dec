"""
TaxOrchestrator - Days 5-6 Implementation

Master coordinator for 6-step tax/legal workflow.
Wires all 6 agents together with proper constraint boundary passing.

CRITICAL: Prevents past failures where selections were lost mid-workflow.
- Single source of truth: TaxPlanningSession holds all boundaries
- Explicit parameter passing: Every agent receives needed boundaries
- Constraint enforcement: Every agent validates boundaries before use
- Single save point: Only _save_approved_response() saves to memory
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import time
import json

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent
from pjj_tax_legal.orchestrator.base import BaseAgent, AgentResult
from pjj_tax_legal.orchestrator.tax_workflow.planner import RequestCategorizer
from pjj_tax_legal.orchestrator.tax_workflow.searcher import TaxResponseSearcher
from pjj_tax_legal.orchestrator.tax_workflow.recommender import FileRecommender
from pjj_tax_legal.orchestrator.tax_workflow.compiler import TaxResponseCompiler
# DocumentVerifier REMOVED - User does manual verification
from pjj_tax_legal.orchestrator.tax_workflow.tracker import CitationTracker
from pjj_tax_legal.agent.logging_config import get_logger

logger = get_logger(__name__)

# NOTE: SegmentedMemory has been removed. All memory searches now use Agent.chat()
# with intelligent navigation (vanilla MemAgent pattern), not semantic similarity scoring.


class TaxPlanningSession:
    """
    Session state holder for tax workflow.

    SINGLE SOURCE OF TRUTH for all boundaries throughout workflow.
    Persisted to disk after each step for recovery if Streamlit resets.
    """

    def __init__(self, session_id: str, user_id: str, request: str):
        # Session identifiers
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.now().isoformat()

        # Original request (immutable)
        self.original_request = request

        # Step 1: RequestCategorizer output
        self.suggested_categories: List[str] = []

        # USER BOUNDARY: Step 1 confirmation
        self.confirmed_categories: List[str] = []

        # Step 2: TaxResponseSearcher output
        self.past_responses_found: List[Dict] = []

        # USER BOUNDARY: Step 3 selection
        self.selected_past_response: Optional[Dict] = None
        self.past_responses_suggested_files: List[str] = []

        # Step 4: FileRecommender output
        self.documents_found: List[Dict] = []

        # USER BOUNDARY: Step 5 selection
        self.selected_documents: List[str] = []
        self.selected_file_contents: Dict[str, str] = {}

        # Step 6a: TaxResponseCompiler output
        self.synthesized_response: str = ""

        # Step 6a: DocumentVerifier output
        self.verification_report: Dict = {}

        # Step 6b: CitationTracker output
        self.response_with_citations: str = ""
        self.citations: List[Dict] = []

        # USER BOUNDARY: Step 6d approval
        self.approval_status: str = "pending"  # pending | approved | rejected

        # Tracking
        self.current_step: int = 0
        self.completion_time: Optional[str] = None


class TaxOrchestrator(BaseAgent):
    """
    Orchestrator for complete 6-step tax/legal workflow.

    Coordinates all 6 agents while ensuring:
    1. User boundaries (categories, selections) flow through entire system
    2. Constraint enforcement at every stage (no autonomous searches)
    3. Session state persisted to disk (recovery from Streamlit resets)
    4. Single save point only (prevents truncation)
    5. Comprehensive metadata tracking (audit trail)

    SEARCH STRATEGY: Vanilla MemAgent Pattern
    - All searches use Agent.chat() with intelligent memory navigation
    - Agent reads from past_responses/ and tax_database/ automatically
    - Constraints enforced via CONSTRAINT text in queries
    - No semantic similarity scoring - uses LLM understanding of query

    CONSTRAINT BOUNDARIES ENFORCED:
    - Step 1: Categories derived from request (suggested via Llama classification)
    - Step 2: Agent searches past_responses/ with category constraint via query text
    - Step 3: User confirms categories (USER BOUNDARY)
    - Step 4: Agent searches tax_database/ with category constraint via query text
    - Step 5: User selects documents (USER BOUNDARY)
    - Steps 6: All synthesis/verification uses ONLY selected documents
    """

    def __init__(
        self,
        agent: Agent,
        memory_path: Path,
        runtime_path: Optional[Path] = None
    ):
        super().__init__(agent, memory_path)
        self.agent = agent

        # PRIMARY DATA DIRECTORY: data/tax_legal/
        # Contains: past_responses/ and tax_database/ (READ-ONLY for searches)
        # Agent navigates these directories intelligently using vanilla MemAgent pattern
        self.memory_path = memory_path

        # SECONDARY RUNTIME DIRECTORY: /streamlit_instance_info/
        # Contains: user sessions, logs, entity data (WRITE for storing sessions)
        # Falls back to memory_path if runtime_path not provided
        self.runtime_path = runtime_path or memory_path

        logger.info("=== INITIALIZING TAXORCHESTRATOR ===")
        logger.info(f"Memory path (past_responses + tax_database): {self.memory_path}")
        logger.info(f"Runtime path (sessions + logs): {self.runtime_path}")
        logger.info("Search strategy: Agent.chat() with intelligent MemAgent navigation")

        # Initialize 5 agents with Agent instance (DocumentVerifier REMOVED)
        # All agents use Agent.chat() for memory navigation (vanilla MemAgent pattern)
        # No SegmentedMemory - all searches go through Agent's understanding of memory
        logger.info("Initializing 5 tax workflow agents...")
        self.request_categorizer = RequestCategorizer(agent, memory_path)
        self.response_searcher = TaxResponseSearcher(agent, memory_path)
        self.file_recommender = FileRecommender(agent, memory_path)
        self.response_compiler = TaxResponseCompiler(agent, memory_path)
        # DocumentVerifier REMOVED - User does manual verification
        self.citation_tracker = CitationTracker(agent, memory_path)
        logger.info("✅ All 5 agents initialized")

        # Session storage in SECONDARY runtime directory
        self.sessions_dir = self.runtime_path / "users"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def run_workflow(
        self,
        request: str,
        session_id: str,
        user_id: str,
        step: int = 1,
        confirmed_categories: Optional[List[str]] = None,
        selected_documents: Optional[List[str]] = None,
        selected_file_contents: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute tax workflow step by step.

        Args:
            request: Client's tax request
            session_id: Unique session identifier
            user_id: User identifier
            step: Which step to execute (1-6)
            confirmed_categories: User-confirmed categories (from Step 1)
            selected_documents: User-selected documents (from Step 5)
            selected_file_contents: Document contents (from Step 5)

        Returns:
            {
                "success": bool,
                "step": int,
                "output": Any,  # Step-specific output
                "session_state": Dict,  # Current session state
                "metadata": Dict,  # Processing metadata
                "next_step": int,  # Next step to execute
                "error": str (if failed)
            }
        """
        try:
            # Load or create session
            session = self._load_or_create_session(session_id, user_id, request)

            # Execute appropriate step
            if step == 1:
                return self._execute_step_1_categorize(session)
            elif step == 2:
                # Requires confirmed_categories from Step 1
                if not confirmed_categories:
                    return {
                        "success": False,
                        "step": 2,
                        "output": [],
                        "session_state": self._serialize_session(session),
                        "metadata": {},
                        "next_step": 2,
                        "error": "Step 1 not complete: categories not confirmed"
                    }
                session.confirmed_categories = confirmed_categories
                return self._execute_step_2_search_past(session)
            elif step == 3:
                # User selects past response (handled by UI, we just wait)
                return {
                    "success": True,
                    "step": 3,
                    "output": {"message": "Awaiting user document selection"},
                    "session_state": self._serialize_session(session),
                    "metadata": {},
                    "next_step": 4
                }
            elif step == 4:
                return self._execute_step_4_search_documents(session)
            elif step == 5:
                # User selects documents (handled by UI, we just wait)
                return {
                    "success": True,
                    "step": 5,
                    "output": {"message": "Awaiting user approval for synthesis"},
                    "session_state": self._serialize_session(session),
                    "metadata": {},
                    "next_step": 6
                }
            elif step == 6:
                # Requires selected documents from Step 5
                if not selected_documents or not selected_file_contents:
                    return {
                        "success": False,
                        "step": 6,
                        "output": "",
                        "session_state": self._serialize_session(session),
                        "metadata": {},
                        "next_step": 6,
                        "error": "Step 5 not complete: documents not selected"
                    }
                session.selected_documents = selected_documents
                session.selected_file_contents = selected_file_contents
                return self._execute_step_6_synthesis_verification_citation(session)
            else:
                return {
                    "success": False,
                    "step": step,
                    "output": {},
                    "session_state": self._serialize_session(session),
                    "metadata": {},
                    "next_step": step,
                    "error": f"Invalid step: {step} (must be 1-6)"
                }

        except Exception as e:
            return {
                "success": False,
                "step": step,
                "output": {},
                "session_state": {},
                "metadata": {},
                "next_step": step,
                "error": f"Workflow error: {str(e)}"
            }

    def _execute_step_1_categorize(self, session: TaxPlanningSession) -> Dict[str, Any]:
        """Step 1: Request categorization"""
        start_time = time.time()

        # STEP 1: RequestCategorizer (no MemAgent, no constraints needed)
        result = self.request_categorizer.generate(request=session.original_request)

        # Store output
        if result.success:
            session.suggested_categories = result.output.get("suggested_categories", [])
            session.current_step = 1

        processing_time = int((time.time() - start_time) * 1000)

        # Save session state
        self._save_session(session)

        return {
            "success": result.success,
            "step": 1,
            "output": {
                "suggested_categories": session.suggested_categories,
                "reasoning": result.output.get("reasoning", ""),
                "confidence": result.output.get("confidence", 0.0)
            },
            "session_state": self._serialize_session(session),
            "metadata": {
                "processing_time_ms": processing_time,
                "categories_suggested": len(session.suggested_categories)
            },
            "next_step": 2,
            "error": result.error if not result.success else ""
        }

    def _execute_step_2_search_past(self, session: TaxPlanningSession) -> Dict[str, Any]:
        """Step 2: Search past responses with confirmed categories"""
        start_time = time.time()

        # STEP 2: TaxResponseSearcher
        # CONSTRAINT: Uses confirmed_categories from Step 1
        # CONSTRAINT: Searches ONLY segments [0-3]
        result = self.response_searcher.generate(
            request=session.original_request,
            categories=session.confirmed_categories
        )

        # Store output
        if result.success:
            session.past_responses_found = result.output
            session.current_step = 2

        processing_time = int((time.time() - start_time) * 1000)

        # Save session state
        self._save_session(session)

        return {
            "success": result.success,
            "step": 2,
            "output": {
                "past_responses": session.past_responses_found,
                "total_found": len(session.past_responses_found)
            },
            "session_state": self._serialize_session(session),
            "metadata": {
                "processing_time_ms": processing_time,
                "segments_accessed": result.metadata.get("segments_accessed", []),
                "category_constraint_boundary": session.confirmed_categories,
                "search_scope": "past_responses [0-3]"
            },
            "next_step": 3,
            "error": result.error if not result.success else ""
        }

    def _execute_step_4_search_documents(self, session: TaxPlanningSession) -> Dict[str, Any]:
        """Step 4: Search tax documents with confirmed categories"""
        start_time = time.time()

        # Extract suggested files from past response if selected
        suggested_files = []
        if session.selected_past_response:
            suggested_files = session.selected_past_response.get("suggested_files", [])
            session.past_responses_suggested_files = suggested_files

        # STEP 4: FileRecommender
        # CONSTRAINT: Uses confirmed_categories from Step 1
        # CONSTRAINT: Searches ONLY segments [4-11]
        result = self.file_recommender.generate(
            request=session.original_request,
            categories=session.confirmed_categories,
            suggested_files=suggested_files
        )

        # Store output
        if result.success:
            session.documents_found = result.output  # FileRecommender returns list directly
            session.current_step = 4

        processing_time = int((time.time() - start_time) * 1000)

        # Save session state
        self._save_session(session)

        return {
            "success": result.success,
            "step": 4,
            "output": {
                "suggested_files": suggested_files,
                "search_results": session.documents_found,
                "total_found": len(session.documents_found)
            },
            "session_state": self._serialize_session(session),
            "metadata": {
                "processing_time_ms": processing_time,
                "segments_accessed": result.metadata.get("segments_accessed", []),
                "category_constraint_boundary": session.confirmed_categories,
                "search_scope": "tax_database [4-11]"
            },
            "next_step": 5,
            "error": result.error if not result.success else ""
        }

    def _execute_step_6_synthesis_verification_citation(
        self,
        session: TaxPlanningSession
    ) -> Dict[str, Any]:
        """Steps 6a-6c: Response synthesis, verification, and citation"""
        start_time = time.time()

        # CONSTRAINT ENFORCEMENT: All following steps use ONLY selected documents
        # (no MemAgent searches, no external knowledge)

        # STEP 6a: TaxResponseCompiler
        # CONSTRAINT: Uses ONLY selected_file_contents (source-only)
        compiler_result = self.response_compiler.generate(
            request=session.original_request,
            selected_files=session.selected_documents,
            selected_file_contents=session.selected_file_contents,
            categories=session.confirmed_categories
        )

        if not compiler_result.success:
            return {
                "success": False,
                "step": 6,
                "output": "",
                "session_state": self._serialize_session(session),
                "metadata": {},
                "next_step": 6,
                "error": f"Response synthesis failed: {compiler_result.error}"
            }

        session.synthesized_response = compiler_result.output
        session.current_step = 6

        # NOTE: DocumentVerifier REMOVED - User does manual verification
        # The human reviews the response and decides if it's acceptable

        # STEP 6b: CitationTracker
        # CONSTRAINT: Cites ONLY from selected_file_contents
        tracker_result = self.citation_tracker.generate(
            response=session.synthesized_response,
            selected_file_contents=session.selected_file_contents
        )

        if tracker_result.success:
            session.response_with_citations = tracker_result.output.get("response_text", "")
            session.citations = tracker_result.output.get("citations", [])

        processing_time = int((time.time() - start_time) * 1000)

        # Save session state
        self._save_session(session)

        return {
            "success": True,
            "step": 6,
            "output": {
                "response": session.response_with_citations,
                "synthesized_response": session.synthesized_response,  # Draft for user review
                "citations": session.citations,
                # verification_report REMOVED - User does manual verification
            },
            "session_state": self._serialize_session(session),
            "metadata": {
                "processing_time_ms": processing_time,
                "compilation_status": "synthesized",
                "citation_count": len(session.citations),
                "source_only_constraint": True
            },
            "next_step": 7,  # User approval (handled by UI)
            "error": ""
        }

    def save_approved_response(self, session: TaxPlanningSession) -> bool:
        """
        SINGLE SAVE POINT: Only location that saves approved responses.

        This prevents truncation errors from old system where multiple
        save locations could overwrite each other.
        """
        try:
            if session.approval_status != "approved":
                return False

            # Save to: data/tax_legal/entities/
            # With all constraint metadata
            response_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at,
                "original_request": session.original_request,
                "confirmed_categories": session.confirmed_categories,
                "selected_documents": session.selected_documents,
                "synthesized_response": session.synthesized_response,
                "response_with_citations": session.response_with_citations,
                "citations": session.citations,
                "verification_report": session.verification_report,
                "metadata": {
                    "constraint_boundary": {
                        "confirmed_categories": session.confirmed_categories,
                        "selected_documents": session.selected_documents,
                        "source_only_constraint": True
                    },
                    "segments_used": {
                        "past_responses": [0, 1, 2, 3],
                        "tax_documents": [4, 5, 6, 7, 8, 9, 10, 11]
                    },
                    "approval_status": session.approval_status
                }
            }

            # Create response file (single save point)
            response_file = self.memory_path / "entities" / f"{session.session_id}.json"
            response_file.parent.mkdir(parents=True, exist_ok=True)

            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception:
            return False

    def _load_or_create_session(
        self,
        session_id: str,
        user_id: str,
        request: str
    ) -> TaxPlanningSession:
        """Load existing session or create new one"""
        session_file = self.sessions_dir / user_id / "sessions" / f"{session_id}.json"

        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Reconstruct session from saved state
                session = TaxPlanningSession(session_id, user_id, request)
                for key, value in data.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                return session
            except Exception:
                pass

        # Create new session
        return TaxPlanningSession(session_id, user_id, request)

    def _save_session(self, session: TaxPlanningSession) -> None:
        """Save session state to disk for recovery"""
        session_file = self.sessions_dir / session.user_id / "sessions" / f"{session.session_id}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)

        session_data = self._serialize_session(session)
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

    def _serialize_session(self, session: TaxPlanningSession) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "original_request": session.original_request,
            "suggested_categories": session.suggested_categories,
            "confirmed_categories": session.confirmed_categories,
            "past_responses_found": session.past_responses_found,
            "selected_past_response": session.selected_past_response,
            "past_responses_suggested_files": session.past_responses_suggested_files,
            "documents_found": session.documents_found,
            "selected_documents": session.selected_documents,
            "synthesized_response": session.synthesized_response,
            "verification_report": session.verification_report,
            "response_with_citations": session.response_with_citations,
            "citations": session.citations,
            "approval_status": session.approval_status,
            "current_step": session.current_step
        }

    def generate(self, **kwargs) -> AgentResult:
        """BaseAgent interface (not primary entry point)"""
        # For compatibility with BaseAgent pattern
        result = self.run_workflow(**kwargs)
        return AgentResult(
            success=result.get("success", False),
            output=result.get("output", {}),
            metadata=result.get("metadata", {}),
            timestamp=datetime.now().isoformat(),
            error=result.get("error", "")
        )


# ============================================================================
# UNIT TESTS
# ============================================================================

