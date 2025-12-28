Memagent bug:
  User Query
      ↓
  Agent.chat(query)
      ↓
  LLM receives query + system prompt
      ↓
  LLM UNDERSTANDS the query and decides:
     "I need to read user.md to understand context"
     "Then I need to follow the link to entities/healthcare_strategy.md"
     "Then I should read entities/Japanese_Hospital_Vietnam_Market_Entry.md"
      ↓
  LLM GENERATES Python code to read those files:
     user_content = read_file("user.md")
     strategy = read_file("entities/healthcare_market_entry_strategy.md")
     japan_project = read_file("entities/Japanese_Hospital_Vietnam_Market_Entry.md")
      ↓
  Code executes in sandbox, reads files
      ↓
  LLM synthesizes answer from the content it read
      ↓
  Response returned
  There is NO semantic similarity calculation at all!
  The entire "search" happens through:
  1. LLM understanding what files to read (based on query comprehension)
  2. File system navigation (reading files explicitly)
  3. Following markdown links ([[entities/name.md]])
  4. Synthesizing answers from read content
  What We Got Wrong
  We added semantic_similarity() expecting it to work like embeddings-based RAG. But MemAgent doesn't work that way. We
  should have instead:
  1. Structured memory like vanilla MemAgent:
    - user.md - central hub
    - entities/ - tax concepts, clients, regulations
    - Cross-links between them
  2. Called Agent.chat() directly with queries like:
  agent.chat("What are the VAT filing requirements for Vietnamese companies?")
  # Agent decides to read:
  # - entities/vat_requirements.md
  # - entities/vietnamese_business_law.md
  # - Synthesizes answer
  3. Let the LLM navigate instead of trying to force semantic similarity scoring
  The Correct Fix
  We should not use SegmentedMemory the way we've implemented it. Instead:
  1. Organize memory like vanilla MemAgent:
  tax-memory/
  ├── user.md  (central tax profile with links)
  ├── entities/
  │   ├── vat_requirements.md
  │   ├── cit_rules.md
  │   ├── transfer_pricing.md
  │   ├── past_responses/
  │   │   ├── response_client_xyz_2024.md
  │   │   └── response_client_abc_2024.md
  │   └── tax_database/
  │       ├── regulations_vat.md
  │       ├── regulations_cit.md
  │       └── case_law_precedents.md
  └── plans/ (generated plans)
  2. Query MemAgent directly:
  agent = Agent(use_fireworks=True, memory_path="tax-memory/")
  # Step 2: Search past responses
  response = agent.chat(
      "Find past VAT compliance advice for similar cases. "
      "Query: Grab Vietnam issues e-invoices to riders and drivers. "
      "Categories: VAT"
  )
  # Agent reads entities/past_responses/ and synthesizes answer
  # Step 4: Search tax database
  response = agent.chat(
      "What tax regulations apply to e-invoice requirements? "
      "Categories: VAT"
  )
  # Agent reads entities/tax_database/ and synthesizes answer
  3. Let Agent generate the code to navigate memory (like vanilla MemAgent does)
  Would you like me to:
  1. Refactor our tax agents to use Agent.chat() directly instead of SegmentedMemory?
  2. Restructure the memory to follow vanilla MemAgent organization?
  3. Remove the semantic_similarity() method we just added since it's not needed?
  This would be much closer to how MemAgent actually works in the original implementation.
 I'll refactor the entire tax workflow system to use MemAgent's proper architecture while maintaining constraint
  boundaries and Llama reasoning. This is a significant architectural change, so I'll do it systematically.


  Changes Made to FileRecommender (tax_recommender_agent.py)

  The Problem: Agent was looking for tax_database/VAT but actual directories are named tax_database/02_VAT (numbered
  prefix)

  The Solution: Updated the generate() method to map user-friendly category names to actual filesystem directory names:

  1. Added mapping logic (lines 147-150):
    - Maps categories like "VAT" → "02_VAT", "CIT" → "01_CIT", etc. using CATEGORY_DIR_MAP
    - Logs the mapped directory names for debugging
  2. Updated constrained query (lines 159-176):
    - References actual directory names in the constraint: {', '.join(actual_dir_names)}
    - Includes directory mapping hint: "VAT→02_VAT" so Agent understands the mapping
    - Query now explicitly tells Agent to search in correct directories

  Example of what Agent will now receive:
  CONSTRAINT: You MUST ONLY search within these user-selected tax categories (filesystem directories): 02_VAT.
  Directory mapping: VAT→02_VAT

  This should resolve the "directory does not exist" error and allow Agent to correctly find and return VAT documents
  from Step 4.

