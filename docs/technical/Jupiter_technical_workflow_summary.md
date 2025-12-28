# COMPREHENSIVE PLAN: Tax & Legal Jupiter Restructure + MemAgent Integration
## Complete Roadmap for English-Only MVP (Phases 2-4) → Translation Addition (Phase 5+)

---

## OVERVIEW

Transform Jupiter from consultant-centric planning into tax/legal document-centric workflow, powered by MemAgent semantic search (not vectors/RAG). Focus: past response discovery → source document identification → cited response synthesis. **Phases 2-4 focus on English-only core system. Vietnamese support (PhoGPT translation) to be added post-cleanup in Phase 5+.**

**Architectural Foundation**:
- **MemAgent**: All memory/search tasks (past responses, source documents)
- **Llama**: Reasoning, synthesis, PDDL-INSTRUCT verification
- **No FAISS/vectors**: Uses MemAgent's bounded, learnable semantic search
- **Translation Service**: Planned for Phase 5+ (after system cleanup and refactoring)

**Key Strategic Decision**: Build complete English-only system in Phases 2-4. After cleanup, add translation layer at Step 4 in Phase 5+ for Vietnamese support. See PHOGPT_TRANSLATION_DISCOVERY.md for translation architecture planning.

---

## PART 1: TAX DATABASE CONVERSION & ORGANIZATION (✅ COMPLETED - Nov 21)

### 1.1 Database Conversion Complete

**Status**: ✅ **PHASE 1 COMPLETED** (November 21, 2025)

**What Was Delivered**:
- 3,433 documents converted to markdown
- 25 past advices fully extracted
- 568 files with text content (Vietnamese & English)
- 2,842 files with metadata-only (Vietnamese documents, extraction deferred)
- 18 tax categories organized hierarchically
- tax-database-index.json created with complete metadata

**Database Composition** (Current State):
```
local-memory/tax-database/
├── 01_CIT/                     [1,627 files, 47.3%]
├── 02_VAT/                     [474 files, 13.8%]
├── 03_Customs/                 [384 files, 11.2%]
├── 04_PIT/                     [163 files, 4.7%]
├── [14 more categories]
└── past_responses/             [25 fully extracted files]

Content Status:
├── Files with full text:       568 (16.7%) - immediately searchable
├── Metadata-only:              2,842 (83.3%) - category/title browsable, content extraction deferred
└── Past responses:             25 (100% extracted) - core asset
```

**Why This State is OK for MVP**:
- 568 content files cover 200-300 English documents (sufficient for initial deployment)
- 25 past responses are the real system asset (grow with each approval)
- Metadata allows category-based browsing
- Extraction deferred to Phase 5 (only if usage data justifies ROI)

---

## PART 2: JUPITER WORKFLOW RESTRUCTURE (6 STEPS - ENGLISH ONLY FOR MVP)

### 2.1 New Tax-Specific Workflow (English-Only, MVP Phase)

**Step 1: Request Input & Categorization**
```
User Input: "Client is a pharmaceutical distributor in Vietnam with a Singapore
           parent company. They want to understand tax implications around
           transfer pricing."

System:
├─ Suggest topic categories: [CIT] [Transfer Pricing] [VAT]
├─ User confirms/adjusts categories
└─ Categories locked in for search (used in Steps 2 & 4)
```

**Step 2: Past Response Search**
```
MemAgent searches: local-memory/past-responses/

Query: English request text
Return: Top 5 similar past cases
├─ Each shows: Original client situation, advice given, files used, approval status
└─ Ranked by semantic similarity to new request
```

**Step 3: User Review & Acceptance**
```
User reviews top 3-5 past responses:
├─ Sees original request + response
├─ Sees which files were used
├─ Decision: Accept this response OR search for different approach

If Accepted:
└─ System shows: "Files from accepted response:"
```

**Step 4: Source Document Discovery**
```
MemAgent searches: local-memory/tax-database/

English query (from Step 1):
├─ Search MemAgent with English text
├─ Return results ranked by relevance
└─ Show documents (568 content files + metadata searchable)

Expected Coverage:
├─ 568 files with extracted content (semantic search works well)
├─ ~200-300 English files (immediately usable)
└─ 3,433 metadata files (category/title browsable)
```

**Step 5: File Selection & Response Synthesis**
```
User sees recommended documents from past response + additional search results

User can:
├─ ✅ Accept all suggested files
├─ ❌ Reject some files
├─ ➕ Add additional files from search results
├─ 🔍 Run new keyword search within category
└─ 🎯 Mark files as "Critical", "Supporting", "Reference"

Once files selected:
├─ Llama synthesizes KPMG format response
├─ Every claim cited to source document
└─ CitationTracker validates citations (no hallucinations)
```

**Step 6: Approval Gate**
```
Partner reviews response:
├─ Checks: Do citations match sources? Is analysis sound?

Decision:
├─ ✅ Approve → Save as new past response + update learning patterns
└─ ❌ Reject → Go back to file selection OR restart search
```

---

## PART 3: AGENT ARCHITECTURE FOR TAX WORKFLOW

### 3.1 Agents (Remove/Add/Refactor)

**Remove**:
- ❌ PlannerAgent (not needed for tax)
- ❌ ExecutorAgent (web search not central)
- ❌ GeneratorAgent (response generation now Llama-based, not agent-based)

**Refactor**:
- **ProposalAgent** → **RequestCategorizer**
  - Input: Client request text (English)
  - Output: Suggested topic categories
  - Uses: Llama to classify request into tax topics

- **VerifierAgent** → **DocumentVerifier**
  - Input: Synthesized response + source files
  - Output: Verification report (citations accurate, no hallucinations?)
  - Uses: PDDL-INSTRUCT to verify preconditions/effects

**New**:
- **TaxResponseSearcher** (uses MemAgent)
  - Searches past responses for similar client situations
  - Returns top-5 past responses with metadata
  - No translation involved (English-only MVP)

- **FileRecommender** (uses MemAgent)
  - Step 4 source document discovery
  - Searches tax database with English query
  - Returns documents ranked by relevance
  - Expected search coverage: 568 content files + ~200-300 English files + metadata

- **TaxResponseCompiler** (uses Llama)
  - Takes selected files
  - Generates KPMG memo with full citations
  - Ensures every claim points to source document
  - English output

- **CitationTracker** (utility)
  - Maps response text back to source documents
  - Validates: "This statement comes from [Filename, page X]"
  - Ensures citation consistency

### 3.2 Orchestrator Flow

```python
class TaxOrchestrator:
    def run(self, client_request: str):
        # Step 1: Categorize
        categories = RequestCategorizer(client_request)
        user_confirm_categories()

        # Step 2: Search past responses
        past_responses = TaxResponseSearcher.search(
            query=client_request,
            constrained_to=categories
        )
        selected_response = user_selects_response(past_responses)

        # Step 3: Get source files from accepted response
        if selected_response:
            suggested_files = FileRecommender.get_files_from_response(selected_response)
        else:
            suggested_files = []

        # Step 4: Search for additional documents
        additional_files = FileRecommender.search_additional(
            query=client_request,
            constrained_to=categories
        )

        # Step 5: User refines file selection
        final_files = user_refines_file_selection(suggested_files + additional_files)

        # Step 6: Synthesize response
        response = TaxResponseCompiler.compile(
            files=final_files,
            request=client_request,
            categories=categories
        )

        # Step 7: Verify citations
        verification = DocumentVerifier.verify(response, final_files)

        # Step 8: Approval gate
        approved = ApprovalGate.wait_for_approval(response, verification)

        if approved:
            save_as_past_response(response, final_files, client_request)
            update_learning_patterns(final_files, categories)
            return response
```

---

## PART 3.5: LOCAL-MEMORY ARCHITECTURE & RESTRUCTURING

### 3.5.1 New Directory Structure (Critical for Phase 2)

**Purpose**: Separate Project Jupiter planning data (archived) from new Tax/Legal workflow memory

**Directory Structure** (Effective November 25, 2025):

```
memagent-modular-fixed/
└── local-memory/
    ├── PJJ-old/                    # Archive: Project Jupiter data (preserved)
    │   ├── entities/               # Old entity knowledge graph
    │   ├── plans/                  # Old strategic plans
    │   └── users/
    │       ├── entities/           # User-specific entities (Jupiter)
    │       └── plans/              # User-specific plans (Jupiter)
    │
    └── tax_legal/                  # NEW: Tax/Legal workflow memory
        ├── entities/               # Tax case entities & learning
        ├── plans/                  # Tax response plans & history
        ├── users/
        │   ├── entities/           # User-specific tax entities
        │   └── plans/              # User-specific tax plans
        └── tax_database_index.json # Maps 568 tax files to segments
```

### 3.5.2 Why Restructure?

| Reason | Benefit |
|--------|---------|
| **Data Preservation** | Old Jupiter data safe in PJJ-old/ (won't be deleted) |
| **Clean Separation** | Tax workflow has isolated memory namespace (no contamination) |
| **Segment Isolation** | Jupiter uses segments dynamically; Tax uses explicit [0-3] + [4-11] |
| **Learning Isolation** | Jupiter's RL-trained importance scores separate from tax learning |
| **Scalability** | Easy to add future workflows (e.g., `legal_strategy/`, `audit_prep/`) |
| **User Privacy** | Each workflow has independent user isolation |

### 3.5.3 MemAgent Integration with New Structure

**SegmentedMemory Initialization**:
```python
# Tax Workflow (NEW)
from orchestrator.tax_workflow import TaxOrchestrator

orchestrator = TaxOrchestrator(
    agent=llama_client,
    memory_path=Path("local-memory/tax_legal"),  # ← NEW: Explicit path
    segmented_memory=SegmentedMemory(
        max_segments=12,
        memory_path=Path("local-memory/tax_legal"),  # ← Isolated namespace
        segment_allocation={
            'response_segments': [0, 1, 2, 3],
            'document_segments': [4, 5, 6, 7, 8, 9, 10, 11]
        }
    )
)

# Project Jupiter (UNCHANGED)
from orchestrator import IntegratedOrchestrator

orchestrator = IntegratedOrchestrator(
    memory_path=Path("local-memory/PJJ-old"),  # ← Can optionally use PJJ-old
    # Rest of initialization unchanged
)
```

### 3.5.4 Data Flow in New Structure

```
User Request (Tax/Legal)
    ↓
TaxOrchestrator.run()
    ├─ MemAgent searches: local-memory/tax_legal/ (ONLY)
    ├─ Segments [0-3]: Load from tax_legal/entities/responses/
    ├─ Segments [4-11]: Load from tax_legal/tax_database/
    └─ Write approved responses to: tax_legal/entities/
    ↓
Learning Signals (Tax/Legal)
    └─ Store in: tax_legal/plans/learning_signals/

[ISOLATED FROM Project Jupiter]

User Request (Strategic Planning)
    ↓
IntegratedOrchestrator.plan_goal()
    ├─ MemAgent searches: local-memory/PJJ-old/ (or root if symlinked)
    └─ Uses dynamic segment allocation
```

### 3.5.5 Migration Steps (One-time setup)

**Step 1: Archive old data**
```bash
mkdir -p local-memory/PJJ-old
mv local-memory/entities local-memory/PJJ-old/
mv local-memory/plans local-memory/PJJ-old/
mv local-memory/users local-memory/PJJ-old/
```

**Step 2: Create new tax_legal structure**
```bash
mkdir -p local-memory/tax_legal/{entities,plans,users/{entities,plans}}
```

**Step 3: (Optional) Backward compatibility symlink**
```bash
# If Jupiter agents need old data without code changes:
ln -s PJJ-old/entities local-memory/entities
```

### 3.5.6 MemAgent Configuration per Workflow

| Property | Project Jupiter | Tax/Legal |
|----------|---|---|
| Memory Path | `local-memory/PJJ-old/` (optional) | `local-memory/tax_legal/` (required) |
| Segments | 12 (dynamic allocation) | 12 (explicit: [0-3] + [4-11]) |
| Segment Strategy | Outcome-based importance | User-confirmed categories |
| Learning Signals | Stored in PJJ-old/plans/ | Stored in tax_legal/plans/ |
| User Isolation | PJJ-old/users/{id}/ | tax_legal/users/{id}/ |
| Database Access | Read from PJJ-old/entities/ | Read from tax_legal/tax_database/ |

---

## PART 4: MEMAGENT INTEGRATION STRATEGY

### 4.1 How MemAgent Handles Tax Database Search (With Translation)

**MemAgent Memory Allocation**:
```
MemAgent Memory (12 segments total, all for tax/legal workflow):
├─ Segments 0-3: Past responses (25+ docs, mixed Vietnamese/English)
│  └─ Fully extracted, semantic search works perfectly
│
├─ Segments 4-11: Tax documents (568 files with content, metadata + some content)
│  └─ Vietnamese & English, organized by category
│  └─ VAT, CIT, Transfer Pricing, PIT, FCT, DTA, Customs, Excise, Environmental, Capital Gains
│
└─ Compression: RL learns importance from approved responses
   └─ Prioritize files used in approved cases
```

### 4.2 MemAgent Search Process

**Step 2: Past Response Search**
```
Query: "Pharmaceutical distribution agreement transfer pricing"

MemAgent.search(
  query=query,
  memory_segments=[0, 1, 2],  # Past responses
  search_type="semantic",
  return_top_k=5
)

Output: Past responses ranked by semantic similarity
```

**Step 4: Source Document Search**
```
Query: English request text

MemAgent.search(
  query=query,
  memory_segments=[4, 5, 6, 7, 8, 9, 10, 11],  # Tax documents
  search_type="semantic",
  return_top_k=10,
  constraints={"categories": [...]}
)

Output: Tax documents ranked by relevance
```

### 4.3 MemAgent Learning Integration

```
After each approved response:

Learning Signal Captured:
├─ Request: "Pharmaceutical distribution..."
├─ Files_selected: [File_A, File_B, File_C]
├─ Categories_used: [CIT, Transfer_Pricing, VAT]
└─ Approval_status: "Approved"

MemAgent Learns:
1. "These files work for pharmaceutical + transfer pricing"
   → Increase importance score for [File_A, File_B, File_C]

2. "These categories co-occur for pharmaceutical cases"
   → Pattern: Pharmaceutical → CIT + TP + VAT

3. "This combination leads to approved outcomes"
   → Next time similar request: Prioritize this combo

4. Compression Decision:
   → Don't compress files used in approved cases
   → Compress files not yet used in approvals
```

---

## PART 5: CITATION ARCHITECTURE (CRITICAL)

### 5.1 Citation Requirement

**MUST HAVE**: Every statement in response cites source document

**Citation Format**:
```
Document Citation: "According to [Filename] (Section 2.3)..."
Past Advice Citation: "As noted in KPMG's Past Advice [Response ID]..."
```

### 5.2 Citation Tracking System

**CitationTracker Component**:
```python
class CitationTracker:
    def track_response_generation(self,
        response_text: str,
        source_files: List[str]
    ):
        """Map every claim in response back to source"""

        for section in response_text.sections:
            for claim in section.extract_claims():
                # Find which source file contains this claim
                source_found = self.find_source_for_claim(claim, source_files)

                if not source_found:
                    flag_hallucination(claim)
                    return error

                # Extract exact citation from source document
                citation = self.extract_citation(source_found, claim)
                response.add_citation(claim, citation)

        return response_with_citations  # All claims cited
```

---

## PART 6: MULTI-USER ARCHITECTURE (VASTAI)

### 6.1 Multi-User Data Organization

```
VastAI Shared Storage:

local-memory/
├─ tax-database/                    [SHARED - all users]
│  ├─ CIT/, VAT/, [18 categories]
│  └─ tax-database-index.json
│
├─ past-responses/                  [SHARED - growing library]
│  ├─ response_20251121_001_[pharma].md
│  ├─ response_20251120_002_[banking].md
│  └─ [grows with each approval]
│
├─ users/                           [SEPARATE per user]
│  ├─ [user1]/
│  │  ├─ current-draft.md           [Private]
│  │  ├─ search-history.json
│  │  └─ preferences.json           [Language preference: Vietnamese/English]
│  └─ [user2]/, [user3]/, etc.
│
├─ audit-logs/                      [SHARED - tracking]
│  ├─ 2025-11-21_searches.log
│  ├─ 2025-11-21_approvals.log
│  └─ 2025-11-21_responses.log
│
└─ learning-patterns.json           [SHARED - system learns from all]
   ├─ Pattern: "Pharma + Distribution" → [Files A, B, C]
   ├─ Pattern: "Transfer Pricing + Multinational" → [Files D, E]
   └─ [grows from real usage]
```

### 6.2 User Roles & Access

**Roles**:
- **Partner**: Create requests, approve responses, see all history
- **Senior Staff**: Create requests, suggest files, can't approve
- **Junior Staff**: View only, learn from system

### 6.3 VastAI Instance Setup

```
VastAI Instance (GPU-enabled):
├─ Streamlit app.py (multi-user session management)
├─ MemAgent instance (semantic search engine)
├─ Llama model (response synthesis)
├─ FastAPI backend (heavy lifting if needed)
└─ SQLite user/audit database

Network Flow:
├─ User browser → VastAI FastAPI (session management)
├─ FastAPI → MemAgent (query search)
├─ MemAgent → Llama (response synthesis)
└─ Response → User browser
```

---

## PART 7: IMPLEMENTATION ROADMAP

### Phase 1: Database Conversion (Week 1)
**Duration**: ~1 week
**Status**: ✅ **COMPLETED (November 21, 2025)**

**Deliverable**: 3,433 markdown files, 25 past responses, tax-database-index.json ready for MemAgent search

---

### Phase 2: Workflow Refactor - English-Only Core (Weeks 3-4)
**Duration**: 2-3 weeks
**Builds on**: Phase 1 complete
**Approach**: Modular implementation of English-only tax workflow

**Implementation Order**:

**Step 1: Refactor Agents** (Days 1-4)
- [ ] RequestCategorizer (from ProposalAgent)
  - [ ] Accept English input
  - [ ] Return suggested categories

- [ ] TaxResponseSearcher (new)
  - [ ] Search 25 past responses
  - [ ] Return top-5 with metadata

- [ ] FileRecommender (new)
  - [ ] Step 4 document search
  - [ ] Search tax database with English query
  - [ ] Return documents ranked by relevance
  - [ ] Expected coverage: 568 content files + metadata

- [ ] TaxResponseCompiler (new)
  - [ ] Accept files
  - [ ] Synthesize KPMG format response
  - [ ] English output

- [ ] DocumentVerifier (from VerifierAgent)
  - [ ] Validate citations
  - [ ] Check for hallucinations

- [ ] CitationTracker (new)
  - [ ] Map claims to sources
  - [ ] Ensure citation consistency

**Step 2: Update Orchestrator** (Days 5-6)
- [ ] TaxOrchestrator rewrite for tax workflow
  - [ ] 6-step workflow (Steps 1-6 above)
  - [ ] Approval gates integration
  - [ ] Learning pattern updates

**Step 3: Update Streamlit UI** (Days 7-10)
- [ ] 6-step workflow UI flow
  - [ ] Request input
  - [ ] Categorization display
  - [ ] Past response list
  - [ ] File selection
  - [ ] Response preview (with citations)

**Deliverable**: Local Jupiter system with 6-step tax workflow, English-only MVP

---

### Phase 3: MemAgent Integration & Testing (Weeks 5-6)
**Duration**: 2-3 weeks
**Builds on**: Phases 1-2 complete

- [ ] Test MemAgent semantic search on tax database
  - [ ] Can MemAgent find similar past responses? (Target: >80%)
  - [ ] Can MemAgent find relevant source documents? (Target: >70%)

- [ ] Test citation accuracy
  - [ ] Does response cite correct sources? (Target: 100%)
  - [ ] No hallucinations detected? (Target: 0 hallucinations)

- [ ] Test with real KPMG questions
  - [ ] 10-15 test cases (English)
  - [ ] Measure time per request (Target: 15-30 min)
  - [ ] Get KPMG feedback on quality
  - [ ] Fix issues identified

- [ ] Performance measurement
  - [ ] Latency per step
  - [ ] MemAgent search time (Target: <5 sec)
  - [ ] Total workflow time (Target: <30 min)

**Deliverable**: Validated, working English-only system on local machine

---

### Phase 4: Multi-User & VastAI Deployment (Weeks 7-8)
**Duration**: 1-2 weeks
**Builds on**: Phases 1-3 complete

- [ ] Set up VastAI instance
  - [ ] GPU specs: A100-40GB or equivalent for MemAgent + Llama
  - [ ] Mount shared storage (tax database, past responses)
  - [ ] Network config (firewall, API access)

- [ ] Deploy system
  - [ ] Streamlit app.py to VastAI
  - [ ] MemAgent instance initialized
  - [ ] Llama model loaded

- [ ] Multi-user configuration
  - [ ] Session management (3+ concurrent users)
  - [ ] User authentication
  - [ ] Role-based access control (Partner/Senior/Junior)

- [ ] Audit & monitoring
  - [ ] Set up audit logs (all searches, approvals, responses)
  - [ ] Monitor performance
  - [ ] Error tracking

- [ ] Testing
  - [ ] Test concurrent multi-user usage
  - [ ] Test file access/isolation
  - [ ] Test translation service under load
  - [ ] Test data persistence across sessions

**Deliverable**: Multi-user system running on VastAI, ready for KPMG usage

---

### Phase 5: System Cleanup + PhoGPT Translation Integration (POST-MVP)
**Duration**: 3-4 weeks (AFTER Phase 4 MVP complete)
**Builds on**: Phase 4 complete, real usage data collected

**Focus**: Cleanup existing codebase, refactor dead code, then add Vietnamese support

**Part 1: Code Cleanup & Refactoring**
- [ ] Remove unused code from Project Jupiter prototype
- [ ] Consolidate conflicting code paths
- [ ] Refactor agents for clarity
- [ ] Update all markdown documentation
- [ ] Clean up module dependencies

**Part 2: PhoGPT Integration** (See PHOGPT_TRANSLATION_DISCOVERY.md for details)
- [ ] Create TranslationService (isolated, translation-only)
- [ ] Integrate at Step 4 only (FileRecommender)
- [ ] Add language detection
- [ ] Update UI for translation transparency
- [ ] Test with Vietnamese legal terminology

**Part 3: Validation**
- [ ] Test Vietnamese queries end-to-end
- [ ] Validate translation quality (>85% accuracy)
- [ ] Ensure ZERO impact on English workflow
- [ ] Get KPMG bilingual staff feedback

**Deliverable**: Clean, refactored system with Vietnamese translation support via PhoGPT

---

### Phase 6: Vietnamese Document Extraction (OPTIONAL - usage-based decision)
**Duration**: 2-4 weeks (ONLY if Phase 4 usage data justifies ROI)
**Builds on**: Phase 5 complete (if executed), real usage data from Phases 4-5

**Decision Point** (after Phase 4-5):
```
Evaluate usage:
├─ If >50% of Step 4 searches fail to find needed documents
│  └─ Extraction ROI justified → Proceed
│
├─ If 30-50% of Step 4 searches fail
│  └─ Extraction optional → Depends on user feedback
│
└─ If <30% of Step 4 searches fail
   └─ Extraction not needed → Keep growing past_responses instead
```

**If Extraction Approved**:

**Option A: NLLB-200 Fine-Tuning** (Low cost, more development)
- [ ] Create Vietnamese legal document corpus (50-100 pairs)
- [ ] Fine-tune NLLB-200 on Vietnamese tax terminology
- [ ] Cost: ~$0 (VastAI GPU time)
- [ ] Timeline: 2-4 weeks
- [ ] Quality: ~70-85% accuracy post fine-tuning
- [ ] Deliverable: Re-extract 2,842 documents with fine-tuned model

**Option B: Google Translate API** (Higher cost, faster)
- [ ] Integrate Google Translate API as extraction tool
- [ ] Batch-process 2,842 documents
- [ ] Cost: ~$200-300 for full batch
- [ ] Timeline: 1-2 weeks
- [ ] Quality: ~95%+ accuracy
- [ ] Deliverable: Re-extract 2,842 documents with Google API

**Post-Extraction**:
- [ ] Update tax-database-index.json
- [ ] Re-index MemAgent with full-content documents
- [ ] Re-test Step 4 search quality
- [ ] Measure improvement in search hit rate
- [ ] Document lessons learned

**Deliverable** (if executed): 3,433 documents with full text content, semantic search fully optimized

---

## PART 8: MINIMUM VIABLE PRODUCT (MVP)

**For Phase 4 launch, system must have**:

### Core Workflow ✅
- [ ] Client request input interface (English)
- [ ] Automatic topic categorization (dropdown, multi-select)
- [ ] MemAgent search past responses (top 5 results)
- [ ] User accept/reject past response selection
- [ ] File recommendation + manual search
- [ ] Llama-based response synthesis
- [ ] Full citation tracking (every claim cited)
- [ ] Approval gate (partner review before delivery)
- [ ] Save approved response as new past response
- [ ] Multi-user access on VastAI

### Search Quality ✅
- [ ] MemAgent returns relevant past responses (>80% of top 3 relevant)
- [ ] MemAgent returns correct source files (568 content + metadata searchable)
- [ ] Supplementary document search finds additional relevant docs
- [ ] Full workflow completes <30 minutes per request

### Response Quality ✅
- [ ] KPMG memo format (Background, Understanding, Analysis, Recommendations, Risks, Sources)
- [ ] Every claim traced to source document
- [ ] No hallucinations (verified via CitationTracker)
- [ ] Professional tone and structure
- [ ] 2-5 page responses (appropriate length)

### Usability ✅
- [ ] Clear 6-step workflow (obvious user flow)
- [ ] Easy file selection (accept/reject/search interface intuitive)
- [ ] Citation preview (user sees where claims come from)
- [ ] Functional (not beautiful, but works smoothly)

### What's NOT in MVP
- ❌ UI polish/design refinement (add later)
- ❌ Keyboard shortcuts / advanced features
- ❌ Mobile responsive
- ❌ Real-time regulatory updates
- ❌ Vietnamese translation support (deferred to Phase 5)
- ❌ Document extraction (deferred to Phase 6)
- ❌ Natural conversation chat (add later)

---

## PART 9: RISK MITIGATION

| Risk | Severity | Mitigation |
|------|----------|-----------|
| MemAgent doesn't find past responses effectively | High | Early testing in Phase 3 with real KPMG questions; pivot search strategy if needed |
| Citation accuracy drops (hallucinations appear) | Critical | CitationTracker validation in Phase 2; partner review gate catches issues; iterate with Llama prompting |
| Search quality on 568 content files insufficient | Medium | Acceptable for MVP; extraction planned for Phase 6 if usage data justifies; grow past_responses in interim |
| VastAI instance performance is slow | Medium | Generous instance sizing; performance monitoring in Phase 4; optimize MemAgent queries if needed |
| KPMG team finds response quality inadequate | High | Iterate quickly in Phase 3; get feedback early; adjust templates if needed |
| Multi-user data isolation fails | High | Thorough testing in Phase 4; implement audit trail to catch data leaks |

---

## PART 10: SUCCESS METRICS

### Phase 3 Testing Success
- ✅ Citations 100% accurate (CitationTracker shows 0 hallucinations)
- ✅ Response quality acceptable to KPMG partners
- ✅ MemAgent semantic search working well (>70% relevance on past responses)

### Phase 4 Launch Success
- ✅ System finds relevant past response for 12/15 test cases (80%+ success)
- ✅ Response generation includes proper citations for 100% of claims
- ✅ KPMG team can operate system without engineer support
- ✅ At least 3 team members trained and actively using
- ✅ Multi-user access works (no data isolation issues)
- ✅ No critical bugs reported in first week
- ✅ Time per response: Target 15-30 minutes (vs. current 90-150 min)

### Long-term Success (Months 2-6)
- ✅ Time reduction: 90-150 min → 20-40 min (50-70% improvement)
- ✅ Team adoption: 80%+ of requests use Jupiter
- ✅ Response quality: Consistent across team members (learning patterns working)
- ✅ Past responses growing: 25 → 50+ (system becomes more useful)
- ✅ Past responses reused: 30-40% of new requests leveraging past work
- ✅ System learning: Quality of recommendations improves over time
- ✅ Phase 5+ extraction/translation decision: Clear data on ROI and need

---

## SUMMARY

This plan transforms Jupiter into a **tax/legal resource-discovery system** using MemAgent's bounded, learnable semantic search (NOT vectors/RAG), integrated with Llama for reasoning and synthesis. **Phases 2-4 focus on building a complete, working English-only MVP. Vietnamese support (PhoGPT translation) will be added post-cleanup in Phase 5.**

### Key Architecture Changes
1. **MemAgent handles**: Past response search + source document search (both semantic, bounded memory)
2. **Llama handles**: Request classification, response synthesis, logical verification
3. **No vectors**: Uses MemAgent's native memory-based semantic search with RL compression
4. **Two-phase search**: Find similar past responses → Extract files used → Offer additional docs
5. **Citation-critical**: Every claim must point to source document (KPMG compliance requirement)
6. **Multi-user**: VastAI deployment with shared tax DB + shared past responses + private drafts
7. **English-only MVP**: Phases 2-4 build complete system with English interface and workflows

### Phase 2-4: English-Only MVP Focus
- Request input (English)
- Topic categorization
- Past response search (MemAgent)
- File recommendation + search
- Llama-based synthesis with full citations
- Approval gates and learning patterns
- Multi-user deployment on VastAI

### Why This Approach
✅ **Faster delivery**: Get complete system working in 8 weeks (Phases 2-4)
✅ **Cleaner codebase**: Build core without translation complexity
✅ **Easier to maintain**: English-only baseline = fewer edge cases
✅ **Better testing**: Validate core functionality before adding languages
✅ **Clearer priorities**: Focus on tax workflow perfection first

### Phase 5+: Translation & Cleanup (Post-MVP)
- Code cleanup and refactoring
- PhoGPT integration at Step 4 (translation-only)
- System validation with Vietnamese queries
- Optional Phase 6: Document extraction (usage-based decision)

See PHOGPT_TRANSLATION_DISCOVERY.md for Vietnamese translation strategy.

### Realistic Timeline
- Phase 1: Database conversion (1 week) - ✅ COMPLETED (Nov 21)
- Phase 2: Workflow refactor (2-3 weeks)
- Phase 3: Testing + validation (2-3 weeks)
- Phase 4: Multi-user deployment (1-2 weeks)
- **Total MVP Timeline: 8 weeks to full English-only working system**
- Phase 5: Code cleanup + PhoGPT translation (3-4 weeks, post-MVP)
- Phase 6: Document extraction (2-4 weeks, OPTIONAL, usage-based decision)

### MVP Scope
Core tax workflow with search quality, response quality, citation accuracy, and basic usability (NOT UI polish). System usable immediately with:
- 25 fully-extracted past responses
- 568 files with text content
- ~200-300 English documents directly searchable
- 3,433 files browsable by category/metadata
- Full citation tracking (zero hallucinations)
- Multi-user access on VastAI

### What Comes Later (Phase 5+)
- Vietnamese language support (PhoGPT at Step 4)
- Code cleanup and refactoring
- Document extraction (if usage data justifies)
- UI polish and advanced features

### Team Structure
- **You**: Solo implementation for all phases
- **Phase 1**: Already completed by Claude Code (Nov 21)
- **Claude Code**: Available for implementation support

---

## PHASE 2 IMPLEMENTATION COMPLETE (NOVEMBER 26, 2025)

### Status: ✅ PHASE 2 IMPLEMENTATION COMPLETE | ⏳ DAY 10 TESTING IN PROGRESS

**Days 1-6: Backend Infrastructure ✅**
- 6 specialized tax agents (RequestCategorizer, TaxResponseSearcher, FileRecommender, TaxResponseCompiler, DocumentVerifier, CitationTracker)
- TaxOrchestrator: Master coordinator for 6-step workflow
- TaxPlanningSession: Single source of truth for all user boundaries
- Complete constraint enforcement throughout workflow
- Session persistence (recovery from Streamlit resets)
- Single save point (prevents truncation errors)
- ✅ 40/40 unit tests passing

**Days 7-9: User Interface + Logging ✅**
- Agent.generate_response() wrapper method (critical interface compatibility fix)
- Comprehensive logging infrastructure (250+ lines in logging_config.py)
- Complete logging added to all 6 tax agents
- Live log viewer in Streamlit sidebar with color-coding
- 6-screen Streamlit UI (Screens 1-6) fully functional:
  - Screen 1: Request input with validation
  - Screen 2: Category confirmation with multi-select
  - Screen 3: Past response selection (optional flow)
  - Screen 4: Document selection with FileRecommender integration
  - Screen 5: Response preview with 3 tabs (Response/Sources/Citations)
  - Screen 6: Approval gate with verification report display
- Full error handling and graceful failures throughout
- Session state persistence to disk
- Comprehensive logging at every step

**Day 10: Database Integration + Testing ⏳ (IN PROGRESS)**
- ✅ Phase 1 database successfully connected to Phase 2 system
- ✅ 3,410 tax documents (568 with content + 3,283 metadata-only)
- ✅ 25 past responses (fully extracted learning examples)
- ✅ Comprehensive metadata index (3,433 entries)
- ✅ MemAgent segments [0-3] + [4-11] populated with real data
- ⏳ Full 6-screen workflow testing with real data (IN PROGRESS)
- ⏳ Error scenario validation (IN PROGRESS)
- ⏳ Constraint boundary enforcement verification (IN PROGRESS)
- ⏳ Performance benchmarking (IN PROGRESS)
- ⏳ Logging visibility confirmation (IN PROGRESS)
- ⏳ Metadata-only file behavior assessment (IN PROGRESS)

**Verification Complete**:
- ✅ 40/40 unit tests passing
- ✅ MemAgent boundary passing verified (categories flow through entire system)
- ✅ Segments [0-3] + [4-11] enforced at agent level
- ✅ Memory namespace isolated (local-memory/tax_legal separate from PJJ-old/)
- ✅ Session state persisted to disk
- ✅ All 6 UI screens implemented and functional
- ✅ Logging system providing complete visibility
- ✅ Error handling verified on all screens
- ✅ State management working across 6-step workflow
- ✅ Real Phase 1 database connected and verified (3,410 documents, 25 past responses)

**Current Progress**: Days 1-9 COMPLETE (90%) | Day 10 Testing ACTIVE (10%)

**What's Being Tested (Day 10)**:
- Complete end-to-end system with real tax documents
- All constraint boundaries enforced with real data
- Full logging for debugging and audit trail
- Realistic performance metrics
- Acceptance of metadata-only document limitation
- Ready for Phase 3 (real KPMG question validation)

### Phase 2 Summary: Complete, Functional Tax Workflow System

**Location**: `/mem-agent-mcp/tax_app.py` (created as separate file from app.py)

**All 6 Screens Implemented**:
1. Request input → RequestCategorizer (Day 1 agent)
2. Category confirmation → TaxResponseSearcher (Day 2 agent)
3. Past response selection → Optional flow handling
4. Document selection → FileRecommender (Day 3 agent)
5. Response preview → TaxResponseCompiler verification
6. Approval gate → DocumentVerifier + CitationTracker (Days 3-4 agents)

**Architecture Decision (Implemented November 25-26, 2025)**:
- Created NEW tax_app.py (clean, isolated) ✅
- Preserved existing app.py (Project Jupiter planning) ✅
- Reason: Zero dead code risk, clear ownership, easier maintenance ✅
- Can consolidate after Phase 2 if needed

See PHASE_2_STEP3_UI.md (v2.0) for complete UI specifications.
See PHASE_2_CURRENT_STAGE.md for detailed daily implementation summary.

---

## FINAL NOTES

This is a **complete, coherent plan** for building a tax/legal AI system that:
- Delivers a working MVP in 8 weeks (Phases 2-4, English-only)
- Has clean architecture enabling later translation addition
- Focuses on core tax workflow perfection before language expansion
- Defers translation to Phase 5 (post-cleanup)
- Preserves option to add extraction or other features later based on usage data

**Next step**: Begin Phase 2 implementation when ready. All planning complete for English-only MVP. Vietnamese translation planning saved in PHOGPT_TRANSLATION_DISCOVERY.md for Phase 5.
