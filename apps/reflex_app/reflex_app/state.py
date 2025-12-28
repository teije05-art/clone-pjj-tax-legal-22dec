"""
TaxState - Centralized state management for the 6-step Tax Workflow System.

Clean 6-Step Workflow:
    Step 1: Enter Question      - User submits tax question, AI categorizes
    Step 2: Confirm Categories  - User confirms/adjusts categories
    Step 3: Past Responses      - System searches, user selects past memoranda
    Step 4: Source Documents    - System searches, user selects regulations
    Step 5: Review Draft        - System synthesizes, user reviews/approves
    Step 6: Complete            - Final response displayed
"""

import reflex as rx
import uuid
from pathlib import Path


class TaxState(rx.State):
    """Centralized state for the 6-step tax workflow."""

    # =========================================================================
    # WORKFLOW STATE
    # =========================================================================
    current_step: int = 1  # 1-6
    is_loading: bool = False
    error_message: str = ""
    session_id: str = ""

    # =========================================================================
    # STEP 1: ENTER QUESTION
    # =========================================================================
    request_text: str = ""

    @rx.event
    def set_request_text(self, value: str):
        """Set the request text."""
        self.request_text = value

    # =========================================================================
    # STEP 2: CONFIRM CATEGORIES
    # =========================================================================
    suggested_categories: list[str] = []
    confirmed_categories: list[str] = []

    # =========================================================================
    # STEP 3: PAST RESPONSES
    # =========================================================================
    past_responses: list[dict] = []
    selected_past_response_names: list[str] = []

    # =========================================================================
    # STEP 4: SOURCE DOCUMENTS
    # =========================================================================
    recommended_files: list[dict] = []
    selected_file_names: list[str] = []

    # =========================================================================
    # STEP 5: REVIEW DRAFT
    # =========================================================================
    draft_response: str = ""

    # =========================================================================
    # STEP 6: COMPLETE
    # =========================================================================
    final_response: str = ""

    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    def _ensure_session(self):
        """Ensure session_id is set."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())

    def _get_orchestrator(self):
        """Lazy-load the orchestrator to avoid import issues at module level."""
        from pjj_tax_legal.agent import Agent
        from pjj_tax_legal.orchestrator import TaxOrchestrator

        project_root = Path(__file__).resolve().parent.parent.parent.parent
        data_path = project_root / "data" / "tax_legal"

        agent = Agent(memory_path=str(data_path))
        return TaxOrchestrator(agent, data_path)

    # =========================================================================
    # STEP 1 → 2: SUBMIT QUESTION
    # =========================================================================
    @rx.event
    async def submit_question(self):
        """Submit tax request and get category suggestions. Moves 1 → 2."""
        self._ensure_session()

        if not self.request_text.strip():
            self.error_message = "Please enter a tax request"
            return

        if len(self.request_text.strip()) < 10:
            self.error_message = "Please enter a more detailed question (at least 10 characters)"
            return

        self.is_loading = True
        self.error_message = ""
        yield  # Update UI to show loading

        try:
            orchestrator = self._get_orchestrator()
            result = orchestrator.run_workflow(
                self.request_text,
                self.session_id,
                "user",
                step=1
            )

            if result.get("success"):
                self.suggested_categories = result.get("output", {}).get("suggested_categories", [])
                self.confirmed_categories = self.suggested_categories.copy()
                self.current_step = 2
            else:
                self.error_message = f"Categorization failed: {result.get('error', 'Unknown error')}"

        except Exception as e:
            self.error_message = f"Error: {str(e)}"

        finally:
            self.is_loading = False

    # =========================================================================
    # STEP 2 → 3: CONFIRM CATEGORIES
    # =========================================================================
    @rx.event
    def set_confirmed_categories(self, categories: list[str]):
        """Update the confirmed categories selection."""
        self.confirmed_categories = categories

    @rx.event
    def toggle_category(self, category: str):
        """Toggle a category in the confirmed list."""
        if category in self.confirmed_categories:
            self.confirmed_categories = [c for c in self.confirmed_categories if c != category]
        else:
            self.confirmed_categories = self.confirmed_categories + [category]

    @rx.event
    async def confirm_categories(self):
        """Confirm selected categories and search past responses. Moves 2 → 3."""
        if not self.confirmed_categories:
            self.error_message = "Please select at least one category"
            return

        self.error_message = ""
        self.current_step = 3
        self.is_loading = True
        yield

        # Auto-search past responses
        try:
            orchestrator = self._get_orchestrator()
            result = orchestrator.run_workflow(
                self.request_text,
                self.session_id,
                "user",
                step=2,
                confirmed_categories=self.confirmed_categories
            )

            if result.get("success"):
                self.past_responses = result.get("output", {}).get("past_responses", [])
            else:
                self.past_responses = []

        except Exception as e:
            self.error_message = f"Error searching: {str(e)}"
            self.past_responses = []

        finally:
            self.is_loading = False

    # =========================================================================
    # STEP 3 → 4: PROCEED TO DOCUMENTS
    # =========================================================================
    @rx.event
    def set_selected_past_responses(self, names: list[str]):
        """Update selected past responses."""
        self.selected_past_response_names = names

    @rx.event
    def toggle_past_response(self, name: str):
        """Toggle a past response in the selected list."""
        if name in self.selected_past_response_names:
            self.selected_past_response_names = [n for n in self.selected_past_response_names if n != name]
        else:
            self.selected_past_response_names = self.selected_past_response_names + [name]

    @rx.event
    async def proceed_to_documents(self):
        """Search tax database for documents. Moves 3 → 4."""
        self.error_message = ""
        self.current_step = 4
        self.is_loading = True
        yield

        try:
            orchestrator = self._get_orchestrator()
            result = orchestrator.run_workflow(
                self.request_text,
                self.session_id,
                "user",
                step=4,
                confirmed_categories=self.confirmed_categories
            )

            if result.get("success"):
                self.recommended_files = result.get("output", {}).get("search_results", [])
            else:
                self.error_message = f"Search failed: {result.get('error', '')}"
                self.recommended_files = []

        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            self.recommended_files = []

        finally:
            self.is_loading = False

    # =========================================================================
    # STEP 4 → 5: SYNTHESIZE RESPONSE
    # =========================================================================
    @rx.event
    def set_selected_files(self, names: list[str]):
        """Update selected document files."""
        self.selected_file_names = names

    @rx.event
    def toggle_file(self, name: str):
        """Toggle a file in the selected list."""
        if name in self.selected_file_names:
            self.selected_file_names = [n for n in self.selected_file_names if n != name]
        else:
            self.selected_file_names = self.selected_file_names + [name]

    @rx.event
    async def synthesize_response(self):
        """Synthesize KPMG response from selected documents. Moves 4 → 5."""
        if not self.selected_file_names:
            self.error_message = "Please select at least one document"
            return

        self.error_message = ""
        self.current_step = 5
        self.is_loading = True
        yield

        try:
            # Build file contents dict from selected files
            file_contents = {}
            for doc in self.recommended_files:
                filename = doc.get("filename", "")
                if filename in self.selected_file_names:
                    file_contents[filename] = doc.get("content", "")

            orchestrator = self._get_orchestrator()
            result = orchestrator.run_workflow(
                self.request_text,
                self.session_id,
                "user",
                step=6,
                confirmed_categories=self.confirmed_categories,
                selected_documents=self.selected_file_names,
                selected_file_contents=file_contents
            )

            if result.get("success"):
                self.draft_response = result.get("output", {}).get("response", "")
                if not self.draft_response:
                    self.draft_response = result.get("output", {}).get("synthesized_response", "")
            else:
                self.error_message = f"Synthesis failed: {result.get('error', '')}"

        except Exception as e:
            self.error_message = f"Error: {str(e)}"

        finally:
            self.is_loading = False

    # =========================================================================
    # STEP 5 → 6: APPROVE DRAFT
    # =========================================================================
    @rx.event
    def approve_draft(self):
        """Approve the draft and finalize. Moves 5 → 6."""
        self.final_response = self.draft_response
        self.current_step = 6

    @rx.event
    async def regenerate_draft(self):
        """Regenerate the draft response. Stays on 5."""
        self.draft_response = ""
        self.current_step = 4  # Go back to trigger re-synthesis
        yield
        await self.synthesize_response()

    # =========================================================================
    # NAVIGATION (BACK BUTTONS)
    # =========================================================================
    @rx.event
    def go_to_step_1(self):
        """Go back to Step 1: Enter Question."""
        self.current_step = 1
        self.error_message = ""

    @rx.event
    def go_to_step_2(self):
        """Go back to Step 2: Confirm Categories."""
        self.current_step = 2
        self.error_message = ""

    @rx.event
    def go_to_step_3(self):
        """Go back to Step 3: Past Responses."""
        self.current_step = 3
        self.error_message = ""

    @rx.event
    def go_to_step_4(self):
        """Go back to Step 4: Source Documents."""
        self.current_step = 4
        self.error_message = ""

    # =========================================================================
    # RESET WORKFLOW
    # =========================================================================
    @rx.event
    def reset_workflow(self):
        """Reset the entire workflow. Moves 6 → 1."""
        self.current_step = 1
        self.request_text = ""
        self.suggested_categories = []
        self.confirmed_categories = []
        self.past_responses = []
        self.selected_past_response_names = []
        self.recommended_files = []
        self.selected_file_names = []
        self.draft_response = ""
        self.final_response = ""
        self.error_message = ""
        self.is_loading = False
        self.session_id = str(uuid.uuid4())

    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================
    @rx.var
    def selected_past_responses(self) -> list[dict]:
        """Get full dict objects for selected past responses."""
        return [
            r for r in self.past_responses
            if r.get("filename", "") in self.selected_past_response_names
        ]

    @rx.var
    def selected_files(self) -> list[dict]:
        """Get full dict objects for selected files."""
        return [
            f for f in self.recommended_files
            if f.get("filename", "") in self.selected_file_names
        ]

    @rx.var
    def past_response_options(self) -> list[str]:
        """Get list of past response filenames for selection."""
        return [r.get("filename", f"Response {i}") for i, r in enumerate(self.past_responses)]

    @rx.var
    def document_options(self) -> list[str]:
        """Get list of document filenames for selection."""
        return [d.get("filename", f"Document {i}") for i, d in enumerate(self.recommended_files)]

    @rx.var
    def short_session_id(self) -> str:
        """Truncated session ID for display."""
        return f"{self.session_id[:8]}..." if self.session_id else "---"

    @rx.var
    def step_names(self) -> dict[int, str]:
        """Map step numbers to names."""
        return {
            1: "Enter Question",
            2: "Confirm Categories",
            3: "Past Responses",
            4: "Source Documents",
            5: "Review Draft",
            6: "Complete",
        }

    @rx.var
    def current_step_name(self) -> str:
        """Get the name of the current step."""
        names = {
            1: "Enter Question",
            2: "Confirm Categories",
            3: "Past Responses",
            4: "Source Documents",
            5: "Review Draft",
            6: "Complete",
        }
        return names.get(self.current_step, "Unknown")
