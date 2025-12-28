"""
KPMG Tax Workflow System - Streamlit UI
Phase 2 Step 3: Tax/Legal Request Analysis and Response Generation

Run with:
  cd pjj-tax-legal
  streamlit run apps/tax_assistant.py
"""

import streamlit as st
from pathlib import Path
import uuid
import json
from datetime import datetime

# ============================================================================
# IMPORTS - Clean package imports (no sys.path hacks needed)
# ============================================================================

try:
    from pjj_tax_legal.agent import Agent
    from pjj_tax_legal.orchestrator import TaxOrchestrator
    from pjj_tax_legal.agent.logging_config import setup_logging, get_logger, tail_log_file, get_log_statistics, clear_logs
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.error("Make sure you've run: pip install -e . from the pjj-tax-legal directory")
    st.stop()

# Initialize logging system
setup_logging()
logger = get_logger(__name__)

# Data path: pjj-tax-legal/data/tax_legal/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "tax_legal"

# Verify data path exists
if not DATA_PATH.exists():
    st.error(f"Data directory not found: {DATA_PATH}")
    st.error("Make sure the data/tax_legal/ directory exists with tax_database/ and past_responses/")
    st.stop()

try:
    agent = Agent(memory_path=str(DATA_PATH))
    logger.info("Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Agent: {e}")
    st.error(f"Failed to initialize Agent: {e}")
    st.stop()

try:
    orchestrator = TaxOrchestrator(agent, DATA_PATH)
    logger.info("TaxOrchestrator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize TaxOrchestrator: {e}")
    st.error(f"Failed to initialize TaxOrchestrator: {e}")
    st.stop()


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="KPMG Tax Workflow System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    .step-header {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }

    .user-boundary {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
        margin: 10px 0;
    }

    .category-pill {
        display: inline-block;
        padding: 8px 12px;
        margin: 5px;
        border-radius: 20px;
        background-color: #e8f4f8;
        border: 1px solid #1f77b4;
        font-weight: 500;
    }

    .error-box {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }

    .success-box {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "workflow_stage" not in st.session_state:
    st.session_state.workflow_stage = "step_1_request"

if "request_text" not in st.session_state:
    st.session_state.request_text = ""

if "suggested_categories" not in st.session_state:
    st.session_state.suggested_categories = []

if "confirmed_categories" not in st.session_state:
    st.session_state.confirmed_categories = []

if "past_responses" not in st.session_state:
    st.session_state.past_responses = []

if "selected_past_responses" not in st.session_state:
    st.session_state.selected_past_responses = []

if "recommended_files" not in st.session_state:
    st.session_state.recommended_files = []

if "selected_files" not in st.session_state:
    st.session_state.selected_files = []

if "compiled_response" not in st.session_state:
    st.session_state.compiled_response = ""

if "draft_response" not in st.session_state:
    st.session_state.draft_response = ""

if "cited_response" not in st.session_state:
    st.session_state.cited_response = ""

# ============================================================================
# TITLE
# ============================================================================

col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/KPMG.svg/1200px-KPMG.svg.png", width=80)
with col2:
    st.title("Tax Workflow System")
    st.markdown("*Intelligent tax analysis and response generation*")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("⚙️ System Control")
    
    # Session info
    st.markdown(f"**Session ID**: `{st.session_state.session_id[:8]}...`")
    st.markdown(f"**Current Stage**: {st.session_state.workflow_stage}")
    
    # Clear session
    if st.button("🔄 Reset Workflow"):
        for key in st.session_state.keys():
            if key != "session_id":
                del st.session_state[key]
        st.rerun()
    
    # View logs
    st.markdown("---")
    if st.checkbox("📊 Show Logs"):
        log_file = REPO_ROOT / "orchestrator" / "tax_workflow" / "frontend" / "streamlit_instance_info" / "logs" / "tax_app.log"
        if log_file.exists():
            try:
                recent_logs = tail_log_file(str(log_file), lines=20)
                st.markdown("**Recent Logs**:")
                st.code(recent_logs, language="text")
            except Exception as e:
                st.warning(f"Could not load logs: {e}")

# ============================================================================
# STEP 1: REQUEST SUBMISSION & CATEGORIZATION
# ============================================================================

if st.session_state.workflow_stage in ["step_1_request", "start"]:
    st.markdown("## Step 1: Submit Tax Request & Get Categories")
    st.markdown("""
    <div class="user-boundary">
    <strong>User Input Needed:</strong> Submit your tax question or request. The system will analyze it and suggest relevant tax domains.
    </div>
    """, unsafe_allow_html=True)
    
    request_input = st.text_area(
        "Enter your tax request:",
        value=st.session_state.request_text,
        height=150,
        placeholder="E.g., 'We have a Vietnam subsidiary that imports pharmaceutical products. What are the key transfer pricing considerations...'"
    )
    
    if st.button("📝 Submit Request & Analyze", key="btn_step1"):
        if not request_input.strip():
            st.error("Please enter a tax request")
        else:
            with st.spinner("Analyzing request..."):
                try:
                    # Initialize orchestrator                    
                    # Step 1: Categorize request
                    logger.info(f"Step 1: Categorizing request (length: {len(request_input)})")
                    categorization_result = orchestrator.run_workflow(request_input, st.session_state.session_id, 'user', step=1)
                    
                    if categorization_result.get('success'):
                        st.session_state.request_text = request_input
                        st.session_state.suggested_categories = categorization_result.get('output').get("suggested_categories", [])
                        st.session_state.workflow_stage = "step_1_review"
                        st.success("✓ Request categorized successfully")
                        st.rerun()
                    else:
                        st.error(f"Categorization failed: {categorization_result.get('error', '')}")
                        logger.error(f"Categorization error: {categorization_result.get('error', '')}")
                
                except Exception as e:
                    st.error(f"Error during categorization: {str(e)}")
                    logger.error(f"Exception: {str(e)}", exc_info=True)

# ============================================================================
# STEP 1: CATEGORY REVIEW & CONFIRMATION
# ============================================================================

if st.session_state.workflow_stage == "step_1_review":
    st.markdown("## Step 1: Review Suggested Categories")
    st.markdown("""
    <div class="user-boundary">
    <strong>User Review Needed:</strong> The system has identified these relevant tax categories. Confirm the ones you want to search with.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Suggested Categories:**")
    for cat in st.session_state.suggested_categories:
        st.markdown(f"<span class='category-pill'>{cat}</span>", unsafe_allow_html=True)
    
    confirmed = st.multiselect(
        "Select categories to use (or leave empty to use suggestions):",
        options=st.session_state.suggested_categories,
        default=st.session_state.suggested_categories,
        key="category_multiselect"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Categories", key="btn_confirm_cats"):
            if not confirmed and not st.session_state.suggested_categories:
                st.error("No categories selected")
            else:
                final_cats = confirmed if confirmed else st.session_state.suggested_categories
                st.session_state.confirmed_categories = final_cats
                st.session_state.workflow_stage = "step_2_search"
                st.rerun()
    
    with col2:
        if st.button("← Back", key="btn_back_to_request"):
            st.session_state.workflow_stage = "step_1_request"
            st.rerun()

# ============================================================================
# STEP 2: PAST RESPONSE SEARCH
# ============================================================================

if st.session_state.workflow_stage == "step_2_search":
    st.markdown("## Step 2: Search Past Tax Responses")
    st.markdown("""
    <div class="user-boundary">
    <strong>Automatic Search:</strong> The system is searching for similar past tax advice cases in your approved categories.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Searching past responses..."):
        try:            
            search_result = orchestrator.run_workflow(st.session_state.request_text, st.session_state.session_id, 'user', step=2, confirmed_categories=st.session_state.confirmed_categories)

            if search_result.get('success'):
                st.session_state.past_responses = search_result.get('output', {}).get('past_responses', [])
                st.success(f"✓ Found {len(st.session_state.past_responses)} past responses")
                st.session_state.workflow_stage = "step_2_review"
                st.rerun()
            else:
                st.warning(f"No past responses found: {search_result.get('error', '')}")
                st.session_state.past_responses = []
                st.session_state.workflow_stage = "step_4_recommend"
                st.rerun()
        
        except Exception as e:
            st.error(f"Error searching past responses: {str(e)}")
            logger.error(f"Search error: {str(e)}", exc_info=True)

# ============================================================================
# STEP 2/3: PAST RESPONSE REVIEW & SELECTION
# ============================================================================

if st.session_state.workflow_stage == "step_2_review":
    st.markdown("## Step 2/3: Review Past Responses")
    st.markdown("""
    <div class="user-boundary">
    <strong>User Review Needed:</strong> Select which past responses to use as reference for the current request.
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.past_responses:
        # === CONTENT PREVIEW SECTION ===
        st.markdown("### 📄 Past Response Previews")
        st.markdown("*Preview the content of each past response before selecting*")

        for i, r in enumerate(st.session_state.past_responses):
            filename = r.get("filename", f"Response {i}")
            with st.expander(f"📄 {filename}", expanded=False):
                # Show full extracted content (up to 3000 chars from semantic extraction)
                content = r.get("content", r.get("summary", "No content available"))
                content_len = len(content) if content else 0
                st.markdown(f"**Relevant Content Extracted ({content_len} characters):**")
                st.text(content)  # Clean text display, not JSON

                # Show metadata
                st.markdown("---")
                st.markdown(f"**Categories:** {', '.join(r.get('categories', []))}")
                st.markdown(f"**Date Created:** {r.get('date_created', 'Unknown')}")
                st.markdown(f"**Files Used:** {', '.join(r.get('files_used', []))}")

        st.markdown("---")
        # === END CONTENT PREVIEW SECTION ===

        selected = st.multiselect(
            "Select past responses to use:",
            options=[r.get("filename", f"Response {i}") for i, r in enumerate(st.session_state.past_responses)],
            key="past_responses_select"
        )
        
        st.session_state.selected_past_responses = [
            st.session_state.past_responses[i]
            for i, r in enumerate(st.session_state.past_responses)
            if r.get("filename") in selected
        ]
    else:
        st.info("No past responses to select from")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("→ Continue to Document Search", key="btn_next_to_docs"):
            st.session_state.workflow_stage = "step_4_recommend"
            st.rerun()
    with col2:
        if st.button("← Back", key="btn_back_to_cats"):
            st.session_state.workflow_stage = "step_1_review"
            st.rerun()

# ============================================================================
# STEP 4: TAX DATABASE SEARCH & RECOMMENDATION
# ============================================================================

if st.session_state.workflow_stage == "step_4_recommend":
    st.markdown("## Step 4: Search Tax Database for Regulations")
    st.markdown("""
    <div class="user-boundary">
    <strong>Automatic Search:</strong> The system is searching for relevant tax regulations and source documents.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Searching tax database..."):
        try:            
            # Pass selected past response filenames as suggested files
            suggested_files = [r.get("filename") for r in st.session_state.selected_past_responses] if st.session_state.selected_past_responses else None
            
            recommend_result = orchestrator.run_workflow(st.session_state.request_text, st.session_state.session_id, 'user', step=4, confirmed_categories=st.session_state.confirmed_categories)

            if recommend_result.get('success'):
                st.session_state.recommended_files = recommend_result.get('output', {}).get('search_results', [])
                st.success(f"✓ Found {len(st.session_state.recommended_files)} recommended documents")
                st.session_state.workflow_stage = "step_4_review"
                st.rerun()
            else:
                st.error(f"Document search failed: {recommend_result.get('error', '')}")
        
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            logger.error(f"Recommend error: {str(e)}", exc_info=True)

# ============================================================================
# STEP 4/5: DOCUMENT REVIEW & SELECTION
# ============================================================================

if st.session_state.workflow_stage == "step_4_review":
    st.markdown("## Step 4/5: Select Source Documents")
    st.markdown("""
    <div class="user-boundary">
    <strong>User Selection Needed:</strong> Select which documents to use for synthesizing the response.
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.recommended_files:
        # === CONTENT PREVIEW SECTION ===
        st.markdown("### 📋 Document Previews")
        st.markdown("*Preview the content of each document before selecting*")

        for i, d in enumerate(st.session_state.recommended_files):
            filename = d.get("filename", f"Document {i}")
            with st.expander(f"📋 {filename}", expanded=False):
                # Show full extracted content (up to 3000 chars from semantic extraction)
                content = d.get("content", d.get("summary", "No content available"))
                content_len = len(content) if content else 0
                st.markdown(f"**Relevant Content Extracted ({content_len} characters):**")
                st.text(content)  # Clean text display, not JSON

                # Show metadata
                st.markdown("---")
                st.markdown(f"**Category:** {d.get('category', 'Unknown')}")
                st.markdown(f"**Date Issued:** {d.get('date_issued', 'Unknown')}")

        st.markdown("---")
        # === END CONTENT PREVIEW SECTION ===

        selected_docs = st.multiselect(
            "Select documents to use:",
            options=[d.get("filename", f"Document {i}") for i, d in enumerate(st.session_state.recommended_files)],
            key="docs_select"
        )
        
        st.session_state.selected_files = [
            st.session_state.recommended_files[i]
            for i, d in enumerate(st.session_state.recommended_files)
            if d.get("filename") in selected_docs
        ]
    else:
        st.warning("No documents found")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("→ Synthesize Response", key="btn_synthesize"):
            if not st.session_state.selected_files:
                st.error("Please select at least one document")
            else:
                st.session_state.workflow_stage = "step_5_compile"
                st.rerun()
    with col2:
        if st.button("← Back", key="btn_back_to_search"):
            st.session_state.workflow_stage = "step_4_recommend"
            st.rerun()

# ============================================================================
# STEP 5: RESPONSE COMPILATION
# ============================================================================

if st.session_state.workflow_stage == "step_5_compile":
    st.markdown("## Step 5: Synthesize KPMG Response")
    st.markdown("""
    <div class="user-boundary">
    <strong>Automatic Synthesis:</strong> The system is generating a professional tax memorandum based on your selected documents.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Synthesizing response..."):
        try:
            # Build file contents dict
            file_contents = {}
            for doc in st.session_state.selected_files:
                filename = doc.get("filename")
                # Use full content (3000 chars) for synthesis, not summary
                file_contents[filename] = doc.get("content", "")
            
            compile_result = orchestrator.run_workflow(st.session_state.request_text, st.session_state.session_id, 'user', step=6, confirmed_categories=st.session_state.confirmed_categories, selected_documents=[d.get('filename') for d in st.session_state.selected_files], selected_file_contents=file_contents)

            if compile_result.get('success'):
                st.session_state.compiled_response = compile_result.get('output', {}).get('response', '')
                st.session_state.draft_response = compile_result.get('output', {}).get('synthesized_response', st.session_state.compiled_response)
                st.success("✓ Response synthesized successfully")
                st.session_state.workflow_stage = "draft_review"
                st.rerun()
            else:
                st.error(f"Response compilation failed: {compile_result.get('error', '')}")
        
        except Exception as e:
            st.error(f"Error synthesizing response: {str(e)}")
            logger.error(f"Compile error: {str(e)}", exc_info=True)

# ============================================================================
# STEP 6: DRAFT REVIEW (Human-in-the-Loop)
# ============================================================================

if st.session_state.workflow_stage == "draft_review":
    st.markdown("## Step 6: Review Draft Response")
    st.markdown("""
    <div class="user-boundary">
    <strong>Human Review Required:</strong> Review the draft response before finalizing. You are responsible for verifying accuracy and completeness.
    </div>
    """, unsafe_allow_html=True)

    # Show the draft response
    st.markdown("### 📝 Draft KPMG Memorandum")
    st.markdown("*Review the synthesized response below. Make sure all claims are accurate and properly sourced.*")

    with st.expander("📄 Draft Response", expanded=True):
        draft_text = st.session_state.draft_response or st.session_state.compiled_response
        st.markdown(draft_text)

    # Show source documents used
    st.markdown("### 📚 Source Documents Used")
    st.markdown("*These documents were used to synthesize the response:*")
    for doc in st.session_state.selected_files:
        filename = doc.get("filename", "Unknown")
        with st.expander(f"📋 {filename}", expanded=False):
            content = doc.get("content", "No content")
            st.text(content[:1000] + "..." if len(content) > 1000 else content)

    st.markdown("---")

    # User approval buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve & Finalize", key="btn_approve_draft"):
            st.session_state.cited_response = st.session_state.draft_response or st.session_state.compiled_response
            st.session_state.workflow_stage = "complete"
            st.rerun()

    with col2:
        if st.button("🔄 Regenerate Draft", key="btn_regenerate"):
            st.session_state.draft_response = ""
            st.session_state.compiled_response = ""
            st.session_state.workflow_stage = "step_5_compile"
            st.rerun()

    with col3:
        if st.button("← Back to Document Selection", key="btn_back_to_docs"):
            st.session_state.workflow_stage = "step_4_review"
            st.rerun()

# ============================================================================
# FINAL RESPONSE
# ============================================================================

if st.session_state.workflow_stage == "complete":
    st.markdown("## ✅ Tax Analysis Complete")

    # Show final response
    with st.expander("📄 Final Response", expanded=True):
        st.markdown(st.session_state.cited_response)

    # Show source documents referenced
    st.markdown("### 📚 Source Documents Referenced")
    for doc in st.session_state.selected_files:
        filename = doc.get("filename", "Unknown")
        with st.expander(f"📋 {filename}", expanded=False):
            content = doc.get("content", "No content")
            st.text(content[:500] + "..." if len(content) > 500 else content)

    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copy to Clipboard"):
            st.write("Response copied to clipboard")

    with col2:
        if st.button("🔄 Start New Analysis"):
            for key in st.session_state.keys():
                if key != "session_id":
                    del st.session_state[key]
            st.rerun()

