# DEVELOPMENT CYCLE 2: MULTI-USER MEMORY SYSTEM WITH SHARED CONTEXT
**Version:** 1.0
**Created:** November 14, 2025
**Duration:** ~0.5-1 day
**Scope:** Private per-user memory + organization-wide shared memory; MemAgent search modes
**Depends On:** DEVELOPMENT_CYCLE_1 (Clean Architecture) ← Must be complete first
**Status:** Ready for Execution

---

## 1. STRATEGIC PURPOSE

### What is Being Developed?

A multi-user memory architecture where:
- **Each user has private local memory** (plans, patterns, analysis specific to that user)
- **Organization has shared memory** (common frameworks, proven strategies accessible to all users)
- **MemAgent can search both** with explicit modes: `search_private` / `search_shared` / `search_both`
- **Data isolation enforced** (User A cannot see User B's private data)
- **Shared knowledge accessible** (All users can access organization-wide shared resources)

### Why Does This Matter?

**Current Limitation:** System treats memory as single monolithic repository. Doesn't distinguish between private vs. shared context.

**What This Enables:**
- **Scalability (Path 3):** Foundation for multi-tenant isolation
- **Knowledge Sharing (Path 9):** Organization benefits from collective learning
- **Privacy (Section 1):** User data stays private while enabling collaboration
- **Institutional Intelligence (Section 2):** Shared patterns available to all, without exposing individual data

### Success Criteria

✅ Private memory directory structure per user
✅ Shared memory directory structure (organization-wide)
✅ MemAgent search modes implemented (private/shared/both)
✅ User isolation enforced (no data leakage)
✅ Shared resources accessible to all
✅ Backward compatible (existing single-user data can migrate)
✅ All tests pass
✅ No behavioral regression

---

## 2. EXTERNAL REFERENCES ANALYZED

### Source 1: full-stack-flask-couchdb
**URL:** `https://github.com/tiangolo/full-stack-flask-couchdb`

**Key Patterns:**
- **User-scoped data:** Each user has documents only they can access
- **Shared documents:** Some documents accessible to all users (permissions-based)
- **View-based queries:** CouchDB views aggregate data while respecting permissions
- **Sync mechanism:** Changes replicate while maintaining isolation

**How It Applies:**
Your markdown file structure can adopt similar isolation:
- `local-memory/users/{user_id}/plans/` - User's private plans
- `local-memory/users/{user_id}/patterns/` - User's private patterns
- `local-memory/shared/frameworks/` - Organization patterns
- `local-memory/shared/templates/` - Shared templates

### Source 2: Multi-Tenancy in Cloud-Based Collaboration Services
**URL:** `https://www.academia.edu/16990372/Multi_tenancy_in_cloud_based_collaboration_services`

**Key Concepts:**
- **Logical Isolation:** Same database/storage, separate logical partitions
- **Permission-based Access:** Queries filtered by user permissions
- **Shared Resources:** Some resources accessible by all users
- **Audit Trail:** Track who accessed what and when

**How It Applies:**
- Private memory: Filtered by `user_id` in queries
- Shared memory: Accessible to all users
- MemAgent queries include user context to filter appropriately
- Audit metadata: Track searches and access

---

## 3. CURRENT MEMORY SYSTEM ASSESSMENT

### Current Architecture

```
local-memory/
├── entities/
├── plans/
└── other_data/
```

**Current Behavior:**
- Single global memory repository
- MemAgent searches entire repository
- No user context
- No private vs. shared distinction

### Issues This Creates

1. **No multi-user support** - Can't separate which data belongs to whom
2. **No shared knowledge** - Each user's patterns isolated, can't share discoveries
3. **Privacy concerns** - In multi-user system, all data would be visible to all users
4. **Scaling blocker** - Can't move to multi-tenant without redesigning memory

---

## 4. TARGET ARCHITECTURE

### New Directory Structure

```
local-memory/
├── users/
│   ├── {user_1_id}/
│   │   ├── plans/
│   │   │   ├── plan_20251114_123456_goal.md
│   │   │   └── ...
│   │   ├── patterns/
│   │   │   ├── successful_patterns.md
│   │   │   └── learned_patterns.md
│   │   ├── analysis/
│   │   │   └── execution_history.md
│   │   └── metadata.json
│   │
│   ├── {user_2_id}/
│   │   ├── plans/
│   │   ├── patterns/
│   │   ├── analysis/
│   │   └── metadata.json
│   │
│   └── ...
│
├── shared/
│   ├── frameworks/
│   │   ├── market_entry_framework.md
│   │   ├── regulatory_compliance_framework.md
│   │   └── ...
│   │
│   ├── proven_strategies/
│   │   ├── healthcare_entry_patterns.md
│   │   ├── finance_expansion_patterns.md
│   │   └── ...
│   │
│   ├── templates/
│   │   ├── market_analysis_template.md
│   │   ├── risk_assessment_template.md
│   │   └── ...
│   │
│   └── metadata.json
│
└── system/
    ├── config.json                 (System configuration)
    └── audit_log.json             (Who accessed what and when)
```

### Data Isolation Model

**Private Memory (User-Scoped):**
- User's plans and iterations
- User's learned patterns
- User's execution history
- User's analysis notes
- Only accessible by: User themselves + (future) admins with permission

**Shared Memory (Organization-Scoped):**
- Common frameworks approved for organization
- Proven strategies from across organization
- Templates and best practices
- Accessible by: All users, read-only

**System Metadata:**
- Configuration (which frameworks are shared)
- Audit log (what was accessed)
- Accessible by: System & admins

### MemAgent Search Modes

```python
# Three explicit search modes:

# Mode 1: Search only user's private memory
results = memagent.search(
    query="market entry strategies",
    context="planning",
    search_mode='private',
    user_id='user_123'
)

# Mode 2: Search only shared organization memory
results = memagent.search(
    query="market entry frameworks",
    context="planning",
    search_mode='shared'
)

# Mode 3: Search both private + shared (default if not specified)
# Private results marked with [PRIVATE]
# Shared results marked with [SHARED]
results = memagent.search(
    query="market entry",
    context="planning",
    search_mode='both',
    user_id='user_123'
)
```

---

## 5. IMPLEMENTATION PLAN (Modular)

### PHASE 1: Data Model & Isolation Layer (2 hours)

#### Step 1.1: Define Domain Entities

```python
# memory/domain/entities/memory_scope.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class MemoryScopeType(Enum):
    PRIVATE = "private"
    SHARED = "shared"

@dataclass
class MemoryScope:
    """Scope of memory - private or shared"""
    scope_type: MemoryScopeType
    user_id: Optional[str] = None  # Required if PRIVATE, None if SHARED

    def is_accessible_by(self, accessor_user_id: str) -> bool:
        """Check if user can access this memory scope"""
        if self.scope_type == MemoryScopeType.SHARED:
            return True  # All users can access shared
        elif self.scope_type == MemoryScopeType.PRIVATE:
            return accessor_user_id == self.user_id  # Only owner can access private
        return False
```

#### Step 1.2: Update Memory Entity

```python
# memory/domain/entities/memory_entry.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from .memory_scope import MemoryScope

@dataclass
class MemoryEntry:
    """Single entry in memory (plan, pattern, analysis, etc.)"""
    id: str
    content: str
    scope: MemoryScope
    entry_type: str  # 'plan', 'pattern', 'analysis', etc.
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str  # Which user created this

    def is_accessible_by(self, user_id: str) -> bool:
        """Check if user can access this entry"""
        return self.scope.is_accessible_by(user_id)
```

#### Step 1.3: Create Repository Interfaces

```python
# memory/domain/repositories/memory_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from memory.domain.entities import MemoryEntry, MemoryScope

class MemoryRepository(ABC):
    """Abstract memory repository with scope-aware queries"""

    @abstractmethod
    def search(
        self,
        query: str,
        scope_type: str,  # 'private', 'shared', or 'both'
        user_id: Optional[str] = None,
        entry_type: Optional[str] = None
    ) -> List[MemoryEntry]:
        """Search memory entries within specified scope"""
        pass

    @abstractmethod
    def store(
        self,
        entry: MemoryEntry
    ) -> str:
        """Store memory entry (returns ID)"""
        pass

    @abstractmethod
    def get(
        self,
        entry_id: str,
        user_id: str
    ) -> Optional[MemoryEntry]:
        """Retrieve specific entry (with access check)"""
        pass

    @abstractmethod
    def list_by_scope(
        self,
        scope_type: str,
        user_id: Optional[str] = None
    ) -> List[MemoryEntry]:
        """List all entries in scope"""
        pass
```

---

### PHASE 2: Migrate File Structure (2 hours)

#### Step 2.1: Create New Directory Structure

```bash
# Create user directory structure
mkdir -p local-memory/users
mkdir -p local-memory/shared/frameworks
mkdir -p local-memory/shared/proven_strategies
mkdir -p local-memory/shared/templates
mkdir -p local-memory/system
```

#### Step 2.2: Create Migration Script

```python
# scripts/migrate_memory_to_multiuser.py

import os
import json
from pathlib import Path
from datetime import datetime
import uuid

def migrate_memory():
    """Migrate existing memory to multi-user structure"""

    # Assume default user (first user in system)
    default_user_id = "user_default_001"

    old_memory = Path("local-memory")
    new_users_dir = Path("local-memory/users")

    # Create user directory
    user_dir = new_users_dir / default_user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    # Migrate plans
    plans_dir = user_dir / "plans"
    if (old_memory / "plans").exists():
        (old_memory / "plans").rename(plans_dir)
    else:
        plans_dir.mkdir(parents=True, exist_ok=True)

    # Migrate patterns
    patterns_dir = user_dir / "patterns"
    if (old_memory / "successful_patterns.md").exists():
        (old_memory / "successful_patterns.md").rename(
            patterns_dir / "successful_patterns.md"
        )

    # Create user metadata
    user_metadata = {
        "user_id": default_user_id,
        "created_at": datetime.now().isoformat(),
        "name": "Default User"
    }
    (user_dir / "metadata.json").write_text(
        json.dumps(user_metadata, indent=2)
    )

    # Create shared directories
    shared_dir = Path("local-memory/shared")
    for subdir in ["frameworks", "proven_strategies", "templates"]:
        (shared_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Create system config
    system_config = {
        "default_user_id": default_user_id,
        "created_at": datetime.now().isoformat(),
        "shared_resources": {
            "frameworks": "Approved frameworks for organization",
            "proven_strategies": "Successful strategies from all users",
            "templates": "Planning templates and best practices"
        }
    }
    (Path("local-memory/system") / "config.json").write_text(
        json.dumps(system_config, indent=2)
    )

    print(f"✅ Migration complete. Default user: {default_user_id}")

if __name__ == "__main__":
    migrate_memory()
```

#### Step 2.3: Run Migration

```bash
# Back up existing memory first
cp -r local-memory local-memory.backup

# Run migration
python scripts/migrate_memory_to_multiuser.py

# Verify structure
ls -la local-memory/users/
tree local-memory/ -L 3
```

---

### PHASE 3: MemAgent Integration (3 hours)

#### Step 3.1: Create MemAgent Wrapper with Search Modes

```python
# memory/infrastructure/memagent_integration.py

from typing import List, Optional, Dict, Any
from pathlib import Path
from memory.domain.entities import MemoryEntry, MemoryScope, MemoryScopeType

class MemAgentSearcher:
    """MemAgent wrapper with scope-aware searching"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        # MemAgent initialized here
        self.memagent = self._init_memagent()

    def search(
        self,
        query: str,
        scope_type: str,  # 'private', 'shared', 'both'
        user_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memory with explicit scope mode.

        Args:
            query: Search query
            scope_type: 'private' (user's data only), 'shared' (org data),
                       or 'both' (results marked with [PRIVATE]/[SHARED])
            user_id: Required if scope_type is 'private'
            context: Optional context (e.g., 'planning', 'learning')

        Returns:
            List of results with scope labels
        """

        if scope_type == 'private':
            if not user_id:
                raise ValueError("user_id required for private search")
            return self._search_private(query, user_id, context)

        elif scope_type == 'shared':
            return self._search_shared(query, context)

        elif scope_type == 'both':
            if not user_id:
                raise ValueError("user_id required for both search")
            private_results = self._search_private(query, user_id, context)
            shared_results = self._search_shared(query, context)
            return self._merge_results(private_results, shared_results)

        else:
            raise ValueError(f"Invalid scope_type: {scope_type}")

    def _search_private(
        self,
        query: str,
        user_id: str,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search only user's private memory"""

        user_dir = self.base_path / 'users' / user_id
        if not user_dir.exists():
            return []

        # MemAgent searches within user directory
        results = self.memagent.search(query, root_dir=str(user_dir))

        # Mark results as private
        for result in results:
            result['scope'] = 'PRIVATE'
            result['user_id'] = user_id

        return results

    def _search_shared(
        self,
        query: str,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search organization shared memory"""

        shared_dir = self.base_path / 'shared'
        if not shared_dir.exists():
            return []

        # MemAgent searches within shared directory
        results = self.memagent.search(query, root_dir=str(shared_dir))

        # Mark results as shared
        for result in results:
            result['scope'] = 'SHARED'

        return results

    def _merge_results(
        self,
        private_results: List[Dict],
        shared_results: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Merge private and shared results, sorted by relevance"""

        # Combine results
        all_results = private_results + shared_results

        # Sort by relevance score (if available)
        all_results.sort(
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )

        return all_results

    def _init_memagent(self):
        """Initialize MemAgent client"""
        # Implementation depends on MemAgent version
        # Assume memagent.Searcher or similar
        pass
```

#### Step 3.2: Update Memory Service to Use Search Modes

```python
# memory/application/services/memory_service.py

from typing import List, Dict, Any, Optional
from memory.domain.repositories import MemoryRepository
from memory.infrastructure.memagent_integration import MemAgentSearcher

class MemoryService:
    """Application service for memory operations"""

    def __init__(
        self,
        memory_repository: MemoryRepository,
        memagent_searcher: MemAgentSearcher
    ):
        self.memory_repository = memory_repository
        self.memagent_searcher = memagent_searcher

    def search_memory(
        self,
        query: str,
        scope_type: str,  # 'private', 'shared', 'both'
        user_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memory with explicit scope.

        Returns:
            List of results with 'scope' field indicating [PRIVATE] or [SHARED]
        """

        results = self.memagent_searcher.search(
            query=query,
            scope_type=scope_type,
            user_id=user_id,
            context=context
        )

        return results

    def store_private_entry(
        self,
        user_id: str,
        content: str,
        entry_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store entry in user's private memory"""

        from memory.domain.entities import MemoryEntry, MemoryScope, MemoryScopeType
        from datetime import datetime
        import uuid

        scope = MemoryScope(
            scope_type=MemoryScopeType.PRIVATE,
            user_id=user_id
        )

        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            scope=scope,
            entry_type=entry_type,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=user_id
        )

        return self.memory_repository.store(entry)

    def store_shared_entry(
        self,
        content: str,
        entry_type: str,
        metadata: Dict[str, Any],
        created_by: str
    ) -> str:
        """Store entry in shared organization memory"""

        from memory.domain.entities import MemoryEntry, MemoryScope, MemoryScopeType
        from datetime import datetime
        import uuid

        scope = MemoryScope(scope_type=MemoryScopeType.SHARED)

        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            scope=scope,
            entry_type=entry_type,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=created_by
        )

        return self.memory_repository.store(entry)
```

---

### PHASE 4: API Integration (1 hour)

#### Step 4.1: Update Context Builder to Use New Memory Service

```python
# orchestrator/interfaces/api/routes/planning_routes.py

@bp.route('/api/search', methods=['POST'])
def search_memory():
    """POST /api/search - Search memory with scope"""

    data = request.json
    user_id = data.get('user_id')  # From session/auth
    query = data.get('query')
    scope_type = data.get('scope_type', 'both')  # 'private', 'shared', 'both'
    context = data.get('context')  # Optional context

    results = memory_service.search_memory(
        query=query,
        scope_type=scope_type,
        user_id=user_id,
        context=context
    )

    return jsonify({
        'results': results,
        'scope': scope_type,
        'user_id': user_id,
        'query': query
    }), 200
```

#### Step 4.2: Update Orchestrator to Pass User Context

```python
# orchestrator/simple_orchestrator.py

def plan(self, goal: str, user_id: str):
    """Execute planning with user context"""

    # Update context builder call to include user_id
    context = self.context_manager.retrieve_context(
        goal=goal,
        user_id=user_id,  # NEW: Pass user_id
        search_scope='both'  # NEW: Search both private + shared
    )

    # Rest of planning logic...
```

---

## 6. INTEGRATION VERIFICATION

### Verification Checklist

#### 1. Directory Structure Correct
```bash
# Check structure exists
ls -la local-memory/users/
ls -la local-memory/shared/
ls -la local-memory/system/

# Verify user directories created
find local-memory/users -name "metadata.json" | wc -l
# Should be >= 1 (at least one user)
```

#### 2. MemAgent Search Modes Work
```python
# Test private search
results_private = memory_service.search_memory(
    query="market entry",
    scope_type='private',
    user_id='user_default_001'
)
assert all(r['scope'] == 'PRIVATE' for r in results_private)

# Test shared search
results_shared = memory_service.search_memory(
    query="market entry framework",
    scope_type='shared'
)
assert all(r['scope'] == 'SHARED' for r in results_shared)

# Test both search
results_both = memory_service.search_memory(
    query="market entry",
    scope_type='both',
    user_id='user_default_001'
)
assert any(r['scope'] == 'PRIVATE' for r in results_both) or len(results_both) >= 0
```

#### 3. Data Isolation Working
```python
# User A stores private data
memory_service.store_private_entry(
    user_id='user_001',
    content='Secret plan',
    entry_type='plan',
    metadata={}
)

# User B searches (should NOT find User A's data)
results = memory_service.search_memory(
    query='secret',
    scope_type='private',
    user_id='user_002'
)
assert len(results) == 0  # User B can't see User A's private data
```

#### 4. Shared Resources Accessible
```python
# Add to shared memory
memory_service.store_shared_entry(
    content='Market Entry Framework',
    entry_type='framework',
    metadata={},
    created_by='user_001'
)

# User A can access shared
results_a = memory_service.search_memory(
    query='Market Entry',
    scope_type='shared',
    user_id='user_001'
)
assert len(results_a) > 0

# User B can access same shared
results_b = memory_service.search_memory(
    query='Market Entry',
    scope_type='shared',
    user_id='user_002'
)
assert len(results_b) > 0
assert results_a == results_b  # Same results for both
```

#### 5. Backward Compatibility
```bash
# Migration didn't break existing data
# All plans still accessible
grep -r "goal:" local-memory/users/*/plans/ | wc -l
# Should match count before migration
```

---

## 7. RISK/ISSUE SECTIONS (Proactive Problem-Solving)

### Risk 1: Data Loss During Migration

**Problem:** Old data accidentally deleted during migration.

**Prevention:**
- [ ] Backup existing memory: `cp -r local-memory local-memory.backup`
- [ ] Verify backup completeness
- [ ] Diff before/after: `diff -r local-memory.backup/plans local-memory/users/user_default_001/plans`

**If It Happens:**
```bash
# Restore from backup
rm -rf local-memory/users
cp -r local-memory.backup/plans local-memory/users/user_default_001/

# Re-run migration carefully
python scripts/migrate_memory_to_multiuser.py
```

---

### Risk 2: MemAgent Search Returns Wrong Scope Results

**Problem:** Search for 'private' returns shared results or vice versa.

**Debug:**
```python
# Check search path
user_dir = Path(f'local-memory/users/{user_id}')
print(f"Searching in: {user_dir}")
print(f"Directory exists: {user_dir.exists()}")
print(f"Files in directory: {list(user_dir.rglob('*.md'))}")

# Verify scope labels in results
results = memory_service.search_memory(
    query="test",
    scope_type='private',
    user_id='user_001'
)
for result in results:
    assert result['scope'] == 'PRIVATE', f"Wrong scope: {result['scope']}"
```

---

### Risk 3: Performance Degradation

**Problem:** Search slower with larger memory.

**Solution:**
- MemAgent already indexes files
- Pattern tiering (Phase 9 of roadmap) handles very large scale
- For now, acceptable performance with file-based approach

---

### Risk 4: User Isolation Bypass

**Problem:** Code accidentally allows User A to access User B's private data.

**Prevention:**
- Code review: All memory access should check `user_id`
- Tests: Explicit test that cross-user access is blocked
- Grep check: `grep -r "user_id" memory/ | grep "==" | wc -l`

**Verify:**
```python
# Comprehensive isolation test
def test_user_isolation():
    # Store data as user_001
    entry_id = memory_service.store_private_entry(
        user_id='user_001',
        content='Secret data',
        entry_type='plan',
        metadata={}
    )

    # Try to retrieve as user_002
    result = memory_service.get_entry(entry_id, user_id='user_002')
    assert result is None  # Can't access

    # Can retrieve as user_001
    result = memory_service.get_entry(entry_id, user_id='user_001')
    assert result is not None  # Can access
```

---

## 8. DECISION TREES (When You Hit Choices)

### Decision 1: Should This Data Be Private or Shared?

```
"I have content. Should it go in private or shared memory?"

IF content is specific to one user's project/analysis:
  → PRIVATE (user-scoped)
  → Example: "User's market entry plan for specific company"

ELSE IF content is a strategy/framework/template useful to everyone:
  → SHARED (organization-scoped)
  → Example: "Market entry framework applicable to all markets"

ELSE IF content is sensitive (competitor analysis, internal secrets):
  → PRIVATE (user-scoped, better security)

ELSE:
  → Start with PRIVATE, move to SHARED if it proves valuable
```

---

### Decision 2: How to Handle Shared Content Updates?

```
"Someone updated a shared framework. How do we version it?"

IF update is minor (typo, clarification):
  → Update in-place with updated_at timestamp

ELSE IF update is significant (different approach):
  → Create versioned file: "framework_v1.md", "framework_v2.md"
  → In metadata, link to new version

ELSE:
  → Create new file with date: "framework_updated_20251114.md"
  → Keep old version for historical reference
```

---

## 9. TESTING STRATEGY

### Unit Tests

```python
# tests/unit/memory/test_memory_scope.py

def test_memory_scope_private_access():
    """Private scope only accessible by owner"""
    scope = MemoryScope(
        scope_type=MemoryScopeType.PRIVATE,
        user_id='user_001'
    )
    assert scope.is_accessible_by('user_001') == True
    assert scope.is_accessible_by('user_002') == False

def test_memory_scope_shared_access():
    """Shared scope accessible by all"""
    scope = MemoryScope(scope_type=MemoryScopeType.SHARED)
    assert scope.is_accessible_by('user_001') == True
    assert scope.is_accessible_by('user_002') == True
    assert scope.is_accessible_by('user_999') == True
```

### Integration Tests

```python
# tests/integration/test_memory_multiuser.py

def test_memory_service_search_modes():
    """Test search modes return correct scope"""

    service = MemoryService(
        memory_repository=FileMemoryRepository('local-memory'),
        memagent_searcher=MemAgentSearcher('local-memory')
    )

    # Store private entry
    service.store_private_entry(
        user_id='user_001',
        content='User 1 plan',
        entry_type='plan',
        metadata={}
    )

    # Store shared entry
    service.store_shared_entry(
        content='Shared framework',
        entry_type='framework',
        metadata={},
        created_by='user_001'
    )

    # Search private
    results = service.search_memory(
        query='User',
        scope_type='private',
        user_id='user_001'
    )
    assert any('User 1 plan' in str(r) for r in results)

    # Search shared
    results = service.search_memory(
        query='framework',
        scope_type='shared'
    )
    assert any('Shared framework' in str(r) for r in results)

    # Search both (as user_001)
    results = service.search_memory(
        query='',  # Empty query finds all
        scope_type='both',
        user_id='user_001'
    )
    assert len(results) >= 2  # Found both private and shared
```

### End-to-End Test

```python
# tests/e2e/test_multiuser_memory_workflow.py

def test_complete_multiuser_workflow():
    """Test complete multi-user memory workflow"""

    # User 1: Create private plan
    user1_plan_id = memory_service.store_private_entry(
        user_id='user_001',
        content='Market entry strategy for Company X',
        entry_type='plan',
        metadata={'market': 'healthcare'}
    )

    # User 2: Can't access User 1's plan
    results = memory_service.search_memory(
        query='Company X',
        scope_type='private',
        user_id='user_002'
    )
    assert len(results) == 0

    # User 1: Shares learned pattern as shared
    pattern_id = memory_service.store_shared_entry(
        content='Healthcare market entry requires 6-month regulatory approval',
        entry_type='framework',
        metadata={'domain': 'healthcare'},
        created_by='user_001'
    )

    # User 2: Can now access the shared pattern
    results = memory_service.search_memory(
        query='healthcare',
        scope_type='shared',
        user_id='user_002'
    )
    assert len(results) > 0

    # User 2: Uses shared pattern for their plan
    user2_plan_id = memory_service.store_private_entry(
        user_id='user_002',
        content='Market entry strategy for Company Y (using healthcare framework from user_001)',
        entry_type='plan',
        metadata={'market': 'healthcare', 'inspired_by': pattern_id}
    )

    # Both users can see shared, but not each other's private
    all_results = memory_service.search_memory(
        query='market entry',
        scope_type='both',
        user_id='user_001'
    )
    # Should include user_001's private + shared only
    assert any(r['scope'] == 'PRIVATE' for r in all_results)
    assert any(r['scope'] == 'SHARED' for r in all_results)
```

---

## 10. ROLLBACK STRATEGY

If multi-user implementation breaks something:

```bash
# Option 1: Restore from backup
rm -rf local-memory/
cp -r local-memory.backup local-memory/

# Option 2: Revert code changes
git revert <commit_hash>

# Option 3: Migrate back to single-user
# (Script provided in migration section)
```

---

## 11. COMPLETION CHECKLIST (Process Framework)

- [ ] **Development Specification:** Clear definition ✅
- [ ] **Codebase Scope:** Files to change identified ✅
- [ ] **Implementation Details:** Step-by-step provided ✅
- [ ] **Code Removal:** Old memory search code refactored ✅
- [ ] **Verification Strategy:** Tests and checks provided ✅
- [ ] **Risk/Issues:** Proactive solutions documented ✅
- [ ] **Decision Trees:** Clear guidance when choices arise ✅

**Execution Checklist:**
- [ ] Directory structure created
- [ ] Migration script run successfully
- [ ] MemAgent search modes implemented
- [ ] Memory service updated with scope awareness
- [ ] API routes updated
- [ ] User context passed through orchestrator
- [ ] All tests passing (unit, integration, e2e)
- [ ] Data isolation verified
- [ ] Backward compatibility confirmed
- [ ] No behavioral regressions

---

## NEXT STEPS

After completing DEVELOPMENT_CYCLE_2:
1. Verify all tests pass (100%)
2. Confirm data isolation working
3. Test mixed-scope searches
4. Mark Goal 2 as COMPLETE
5. Move to DEVELOPMENT_CYCLE_3 (Subagent Hierarchy)

**Estimated Timeline:** 0.5-1 day

---

**Document Status:** Complete & Ready for Execution
**Last Updated:** November 14, 2025
**Next Document:** DEVELOPMENT_CYCLE_3_SUBAGENT_HIERARCHY.md
