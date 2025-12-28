# DEVELOPMENT CYCLE 1: COMPLETE CODEBASE CLEANUP TO CLEAN ARCHITECTURE
**Version:** 1.0
**Created:** November 14, 2025
**Duration:** ~1 day (intensive)
**Scope:** Refactor all 31+ modules to Clean Architecture pattern; remove all dead code
**Status:** Ready for Execution

---

## 1. STRATEGIC PURPOSE & WHY CLEAN ARCHITECTURE

### What is Being Developed?

A complete architectural refactoring of the entire codebase from its current modular-but-mixed state to strict **Clean Architecture** pattern. This establishes a clean, dependency-managed foundation for Goals 2-4 and prevents technical debt from accumulating.

### Why Does This Matter?

**Current State Problems:**
- Modules exist but lack consistent architectural pattern
- Dependencies may be tangled (unclear what depends on what)
- Dead code scattered throughout (unused functions, orphaned classes)
- Hard to add multi-user support to messy architecture
- Hard to refactor agents if current structure is unclear

**What Clean Architecture Solves:**
- **Clear dependency direction:** Outer layers depend on inner layers, never the reverse
- **Testable:** Business logic isolated from frameworks
- **Modifiable:** Changes in one layer don't cascade to others
- **Understandable:** Clear folder structure shows intent immediately
- **Scalable:** Adding multi-tenant support, agent spawning, etc. becomes straightforward

**Why This MUST Come First:**
Goals 2-4 (multi-user memory, agents, chat) will be much easier on clean code. Refactoring while building new features creates technical debt.

### Success Criteria

✅ All 31+ modules reorganized to Clean Architecture
✅ All dead code removed (zero orphaned functions)
✅ All dependencies acyclic and documented
✅ Each module has single responsibility
✅ Tests pass after refactoring
✅ No behavioral changes (refactoring only, no feature changes)

---

## 2. EXTERNAL REFERENCES ANALYZED

### Source 1: python-clean-architecture-example
**URL:** `https://github.com/claudiosw/python-clean-architecture-example`

**Key Patterns Adopted:**
- **Folder Structure:** `presentation/` → `application/` → `domain/` → `infrastructure/`
- **Dependency Rule:** Always point inward. Domain knows nothing of outer layers.
- **Entities:** Core business logic, zero external dependencies
- **Use Cases (Application Services):** Orchestration logic, coordinates entities
- **Interface Adapters:** Convert data formats (API JSON ↔ entities)
- **Frameworks & Drivers:** Flask, databases, external libraries

**How It Applies Here:**
Your current system has some of these already (agents, context, orchestrator), but lacks clean separation. We'll reorganize to explicit layers.

### Source 2: Design Smells (Duke CS Paper)
**URL:** `https://courses.cs.duke.edu/compsci308/spring24/readings/Design_Smells.pdf`

**Key Smells to Identify & Remove:**

| Smell | What It Looks Like | How to Fix |
|-------|-------------------|-----------|
| **Rigidity** | Hard to change one thing without affecting others | Break circular dependencies |
| **Fragility** | One change breaks unrelated code | Reduce coupling, increase cohesion |
| **Immobility** | Can't reuse components | Extract to standalone module |
| **Viscosity** | Easier to do wrong thing than right thing | Clear architecture makes right thing easier |
| **Needless Complexity** | Over-engineered for current needs | Remove unused features |
| **Needless Repetition** | Same code in multiple places | Extract to shared utility |
| **Opacity** | Hard to understand what code does | Clear naming, documented responsibilities |

---

## 3. CURRENT CODE ASSESSMENT

### Current Module Structure (What Exists)

Based on your codebase analysis:

```
orchestrator/
  ├── agents/               (4 agents: planner, verifier, executor, generator)
  ├── context/             (context builders, memory context)
  ├── learning/            (learning_analyzer, pattern_recommender)
  ├── simple_orchestrator.py
  └── __init__.py

local-memory/              (user data storage, markdown files)

static/                    (frontend - NOT TOUCHING during this cycle)

simple_chatbox.py          (API endpoints)

Multiple utility modules:  (learning_tracker, goal_analyzer, verification_feedback, etc.)
```

### Current Issues (Design Smells Identified)

1. **Tangled Dependencies:** Modules import from multiple places; unclear dependency graph
2. **Dead Code:** Old experimental code, unused functions scattered throughout
3. **Mixed Concerns:** Some modules do too much (orchestrator, agents)
4. **Unclear Boundaries:** What's domain logic vs. application logic vs. presentation?
5. **Tight Coupling:** Hard to swap components (e.g., replace Fireworks with cluster GPU)
6. **No Clear Layering:** No separation between business logic and frameworks

### What Will NOT Change (Preserved Behavior)

- ✅ All existing features work identically
- ✅ Planning pipeline produces same outputs
- ✅ Memory system stores/retrieves same data
- ✅ Learning mechanisms function identically
- ✅ External API behavior unchanged

---

## 4. TARGET CLEAN ARCHITECTURE STRUCTURE

### New Folder Organization

```
orchestrator/
  ├── domain/                   (INNERMOST: Business logic, zero dependencies)
  │   ├── entities/             (Planning entities, Agent, Pattern, Plan)
  │   ├── value_objects/        (Goal, Confidence, Timeline, etc.)
  │   └── repositories/         (Abstract interfaces for data access)
  │
  ├── application/              (MIDDLE: Use cases & orchestration)
  │   ├── services/             (Planning service, Learning service, Agent service)
  │   ├── dto/                  (Data transfer objects)
  │   └── mappers/              (Convert domain ↔ DTO)
  │
  ├── infrastructure/           (OUTER: External dependencies)
  │   ├── repositories/         (Implement abstract repositories with file/DB access)
  │   ├── llm_providers/        (Fireworks, Ollama, cluster GPU adapters)
  │   └── memory/               (MemAgent integration, persistence)
  │
  ├── interfaces/               (OUTERMOST: API & presentation)
  │   ├── api/                  (Flask endpoints)
  │   └── cli/                  (Command-line interface if needed)
  │
  └── tests/                    (Unit, integration, end-to-end tests)

learning/
  ├── domain/                   (Learning entities, Pattern, Learning rule)
  ├── application/              (Learning service)
  ├── infrastructure/           (Pattern storage, pattern retriever)
  └── tests/

memory/                         (NEW: Dedicated memory layer)
  ├── domain/                   (Memory entity, User, SharedMemory)
  ├── application/              (Memory service, search service)
  ├── infrastructure/           (MemAgent integration)
  └── tests/

shared/                         (SHARED: Utilities, constants, helpers)
  ├── constants.py              (Configuration, model names)
  ├── exceptions.py             (Domain-specific exceptions)
  └── types.py                  (Type hints, enums)

tests/                          (Root test directory)
  ├── unit/
  ├── integration/
  └── e2e/
```

### Dependency Flow (Arrows Point Inward)

```
                    CLI / API Endpoints
                           ↓
              Interfaces Layer (Flask routes)
                           ↓
        Application Services (Planning, Learning, Memory)
                           ↓
         Domain Entities (Plan, Agent, Pattern, Memory)
                           ↓
      Infrastructure Adapters (LLM providers, File storage)
```

**Rule:** Domain layer never imports from application, infrastructure, or interfaces.
Application never imports from interfaces.
Interfaces can import anything.

---

## 5. MODULE-BY-MODULE REFACTORING PLAN (Dependency Order)

### PHASE 1: Foundation Layers (No Dependencies)

These have no internal dependencies on other modules. Refactor first.

#### Module 1.1: Shared Utilities & Constants
**Current Location:** Scattered across files
**New Location:** `shared/`

**What to Extract:**
- All constants (model names, paths, defaults)
- All custom exceptions
- All type definitions & enums
- All utility functions (string parsing, formatting, etc.)

**Refactoring Steps:**
1. Create `shared/constants.py` - centralize all constants
2. Create `shared/exceptions.py` - custom exception classes
3. Create `shared/types.py` - type hints, enums, dataclasses
4. Create `shared/utils.py` - utility functions
5. Update all imports throughout codebase

**Testing:**
- Verify all constants accessible from new location
- Run full test suite to confirm no import errors

---

#### Module 1.2: Domain Entities
**Current Location:** Scattered in agents, orchestrator
**New Location:** `orchestrator/domain/entities/`

**What to Extract:**
- `Plan` class (from current planning code)
- `Agent` class (base agent definition)
- `Pattern` class (learning patterns)
- `Goal` class (user goals)
- `ExecutionStep` class
- Any other business entity

**Refactoring Steps:**
1. Create `orchestrator/domain/entities/__init__.py`
2. Define `Plan` entity with pure business methods
3. Define `Agent` entity with status, performance
4. Define `Pattern` entity with versioning
5. Define supporting entities
6. Ensure ZERO external dependencies

**Code Pattern - Domain Entity:**
```python
# orchestrator/domain/entities/plan.py

from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class Plan:
    """Core planning entity - pure business logic, zero framework dependencies"""
    id: str
    goal: str
    status: str  # 'draft', 'in_progress', 'completed', 'rejected'
    created_at: datetime
    updated_at: datetime
    steps: List['PlanStep']

    def is_complete(self) -> bool:
        """Pure business logic method"""
        return self.status == 'completed'

    def add_step(self, step: 'PlanStep') -> None:
        """Domain logic: adding steps"""
        self.steps.append(step)
        self.updated_at = datetime.now()
```

**Testing:**
- Unit tests for each entity's business methods
- No external dependencies (no file I/O, no LLM calls)

---

### PHASE 2: Application Services (Depends on Domain)

These orchestrate domain entities. Refactor after Phase 1.

#### Module 2.1: Planning Service
**Current Location:** Scattered in orchestrator, agents
**New Location:** `orchestrator/application/services/planning_service.py`

**What to Extract:**
- Planning logic (goal analysis, step generation, verification)
- Orchestration of agents
- Checkpoint management

**Refactoring Steps:**
1. Create `orchestrator/application/services/planning_service.py`
2. Extract planning use cases into service methods
3. Service depends on domain entities, NOT on infrastructure
4. Receive dependencies via constructor (dependency injection)

**Code Pattern - Application Service:**
```python
# orchestrator/application/services/planning_service.py

from typing import List
from orchestrator.domain.entities import Plan, PlanStep
from orchestrator.domain.repositories import PlanRepository

class PlanningService:
    """Application service - orchestrates domain entities"""

    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository

    def create_plan(self, goal: str) -> Plan:
        """Use case: Create a new plan"""
        plan = Plan(
            id=generate_id(),
            goal=goal,
            status='draft',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            steps=[]
        )
        self.plan_repository.save(plan)
        return plan

    def add_step(self, plan_id: str, step: PlanStep) -> Plan:
        """Use case: Add step to plan"""
        plan = self.plan_repository.get(plan_id)
        plan.add_step(step)  # Domain logic
        self.plan_repository.save(plan)
        return plan
```

**Testing:**
- Integration tests with mock repository
- Verify planning logic correct

---

#### Module 2.2: Learning Service
**Current Location:** `learning_analyzer.py`, `pattern_recommender.py`, `learning_tracker.py`
**New Location:** `learning/application/services/learning_service.py`

**What to Extract:**
- Pattern extraction logic
- Pattern recommendation logic
- Pattern versioning logic
- Learning analytics

**Refactoring Steps:**
1. Create `learning/application/services/learning_service.py`
2. Extract pattern learning into service methods
3. Service depends on domain entities, NOT on files directly
4. Receive pattern repository via constructor

**Testing:**
- Test pattern extraction produces correct patterns
- Test pattern versioning works
- Test pattern recommendation returns sorted list

---

#### Module 2.3: Agent Service
**Current Location:** `orchestrator/agents/` and `simple_orchestrator.py`
**New Location:** `orchestrator/application/services/agent_service.py`

**What to Extract:**
- Agent lifecycle management
- Agent selection logic
- Agent communication orchestration

**Refactoring Steps:**
1. Create `orchestrator/application/services/agent_service.py`
2. Service manages agent creation, execution, monitoring
3. Doesn't know about Flask or frontend
4. Returns DTOs for presentation layer

**Testing:**
- Test agent selection logic
- Test agent execution returns expected results

---

### PHASE 3: Infrastructure Layer (Depends on Domain & Application)

These implement abstract repositories and integrate with external systems.

#### Module 3.1: LLM Provider Abstraction
**Current Location:** Scattered (Fireworks integration)
**New Location:** `orchestrator/infrastructure/llm_providers/`

**What to Extract:**
- Abstract LLM interface
- Fireworks implementation
- (Future: Ollama, cluster GPU, etc.)

**Refactoring Steps:**
1. Create `orchestrator/infrastructure/llm_providers/__init__.py`
2. Define abstract `LLMProvider` interface
3. Implement `FireworksProvider`
4. Application services depend on abstract interface, not concrete implementation

**Code Pattern - Infrastructure Abstraction:**
```python
# orchestrator/infrastructure/llm_providers/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Abstract LLM provider interface"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """List available models"""
        pass


# orchestrator/infrastructure/llm_providers/fireworks.py

class FireworksProvider(LLMProvider):
    """Concrete Fireworks implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = init_fireworks(api_key)

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.completions.create(
            prompt=prompt,
            **kwargs
        )
        return response.choices[0].text
```

**Testing:**
- Mock LLM provider for unit tests
- Real Fireworks tests (integration)

---

#### Module 3.2: Memory Storage Repository
**Current Location:** `orchestrator/context/memory_context.py`
**New Location:** `memory/infrastructure/repositories/memory_repository.py`

**What to Extract:**
- File-based memory storage (local-memory/)
- MemAgent integration
- Query execution

**Refactoring Steps:**
1. Create `memory/domain/entities/memory_entity.py` - Memory entity
2. Create `memory/domain/repositories/memory_repository.py` - Abstract interface
3. Create `memory/infrastructure/repositories/file_memory_repository.py` - File implementation
4. Create `memory/infrastructure/memagent_integration.py` - MemAgent wrapper

**Code Pattern - Repository Pattern:**
```python
# memory/domain/repositories/memory_repository.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MemoryRepository(ABC):
    """Abstract memory repository"""

    @abstractmethod
    def search(self, query: str, context: str = None) -> List[Dict[str, Any]]:
        """Search memory"""
        pass

    @abstractmethod
    def store(self, content: str, metadata: Dict) -> str:
        """Store content"""
        pass


# memory/infrastructure/repositories/file_memory_repository.py

import os
from memory.domain.repositories import MemoryRepository

class FileMemoryRepository(MemoryRepository):
    """File-based memory implementation"""

    def __init__(self, base_path: str):
        self.base_path = base_path

    def search(self, query: str, context: str = None) -> List[Dict[str, Any]]:
        # Search files in local-memory/
        pass

    def store(self, content: str, metadata: Dict) -> str:
        # Save to local-memory/
        pass
```

**Testing:**
- Repository tests with temporary directory
- Integration tests with real local-memory/

---

#### Module 3.3: Plan Persistence Repository
**Current Location:** `local-memory/plans/`
**New Location:** `orchestrator/infrastructure/repositories/plan_repository.py`

**Refactoring Steps:**
1. Create abstract `PlanRepository` in domain
2. Implement `FilePlanRepository` in infrastructure
3. Service uses abstract interface

**Testing:**
- Save and retrieve plans
- Verify metadata preserved

---

### PHASE 4: Interface Layer (Depends on Everything)

These expose services to the outside world.

#### Module 4.1: API Endpoints
**Current Location:** `simple_chatbox.py`
**New Location:** `orchestrator/interfaces/api/routes/`

**What to Extract:**
- Flask route definitions
- Request validation & parsing
- Response formatting

**Refactoring Steps:**
1. Create `orchestrator/interfaces/api/routes/planning_routes.py`
2. Create `orchestrator/interfaces/api/routes/learning_routes.py`
3. Inject services into routes via constructor
4. Routes handle HTTP, not business logic

**Code Pattern - API Route:**
```python
# orchestrator/interfaces/api/routes/planning_routes.py

from flask import Blueprint, request, jsonify
from orchestrator.application.services import PlanningService
from orchestrator.interfaces.api.dto import PlanDTO

def create_planning_routes(planning_service: PlanningService):
    """Factory function to create routes with injected service"""

    bp = Blueprint('planning', __name__, url_prefix='/api/plans')

    @bp.route('', methods=['POST'])
    def create_plan():
        data = request.json
        plan = planning_service.create_plan(goal=data['goal'])
        return jsonify(PlanDTO.from_entity(plan).to_dict()), 201

    return bp
```

**Testing:**
- Test endpoints with mock services
- Verify request/response format correct

---

### PHASE 5: Dead Code Removal

After refactoring into clean architecture, identify and remove dead code.

#### Dead Code Identification Strategy

**Search for these patterns:**

```bash
# 1. Unused imports
grep -r "^import" . | grep -v "# used for"

# 2. Unused functions (defined but never called)
grep -r "^def " . > defined_functions.txt
grep -r "function_name(" . > called_functions.txt
# Compare files manually

# 3. Unused classes
grep -r "^class " . > defined_classes.txt
grep -r "ClassName" . > used_classes.txt
# Compare files manually

# 4. Old experimental code (often has "old_", "experimental_", "test_" prefix)
find . -name "*old*" -o -name "*experimental*" -o -name "*debug*"

# 5. Commented code (more than 3 lines)
grep -r "^\s*#" . | grep -E "^[^:]*:\s*#[^#]" | wc -l
```

#### Dead Code Removal Process

1. **Identify:** List all candidates
2. **Verify:** Grep entire codebase to confirm no references
3. **Remove:** Delete file or function
4. **Test:** Run full test suite to confirm nothing broke
5. **Commit:** Commit removal with message "Remove dead code: [reason]"

#### Example: Removing Dead Functions

```python
# OLD CODE (unused since Goal X refactoring)
def old_planning_logic(goal):
    """This function was replaced by PlanningService"""
    pass

# REMOVAL STEPS:
# 1. Grep for "old_planning_logic" - zero results elsewhere ✓
# 2. Delete function
# 3. Run tests - all pass ✓
# 4. Commit: "Remove dead code: old_planning_logic replaced by PlanningService"
```

---

## 6. IMPLEMENTATION STEPS (Sequential Execution)

### STEP 1: Prepare & Inventory (30 minutes)

**What to do:**
1. Create new folders per Clean Architecture structure
2. Inventory all current modules - list what each does
3. Create mapping: Current module → New location

**Commands:**
```bash
# Create folder structure
mkdir -p orchestrator/domain/{entities,value_objects,repositories}
mkdir -p orchestrator/application/{services,dto,mappers}
mkdir -p orchestrator/infrastructure/{repositories,llm_providers,memory}
mkdir -p orchestrator/interfaces/{api,cli}
mkdir -p learning/{domain,application,infrastructure}
mkdir -p memory/{domain,application,infrastructure}
mkdir -p shared
mkdir -p tests/{unit,integration,e2e}

# Verify structure
tree -L 3
```

**Checklist:**
- [ ] All folders created
- [ ] Current modules inventoried
- [ ] Mapping document created (what goes where)

---

### STEP 2: Extract Shared Layer (1 hour)

**What to do:**
1. Centralize all constants
2. Extract common exceptions
3. Extract type definitions

**Implementation:**
```bash
# 1. Identify all constants
grep -r "^[A-Z_]* = " --include="*.py" . > constants_found.txt

# 2. Extract to shared/constants.py
# Copy all relevant constants

# 3. Update imports throughout
# Old: from some_module import CONSTANT
# New: from shared.constants import CONSTANT

# 4. Test imports
python -c "from shared.constants import *"
```

**Checklist:**
- [ ] Constants centralized
- [ ] Exceptions extracted to shared/exceptions.py
- [ ] Type definitions in shared/types.py
- [ ] All imports updated
- [ ] No import errors

---

### STEP 3: Extract Domain Layer (2 hours)

**What to do:**
1. Define all entity classes
2. Create repository interfaces
3. Zero external dependencies in domain/

**Implementation:**
```python
# orchestrator/domain/entities/__init__.py

from .plan import Plan
from .agent import Agent
from .pattern import Pattern
from .goal import Goal

__all__ = ['Plan', 'Agent', 'Pattern', 'Goal']
```

**Checklist:**
- [ ] All entities defined
- [ ] Entity tests passing
- [ ] Repository interfaces created
- [ ] Domain/ has zero external dependencies
- [ ] Domain/ tests: 100% pass rate

---

### STEP 4: Extract Application Services (3 hours)

**What to do:**
1. Create service classes for each major use case
2. Services depend on domain entities, NOT infrastructure
3. Services depend on abstract repositories (interfaces)

**Implementation:**
```python
# orchestrator/application/services/__init__.py

from .planning_service import PlanningService
from .learning_service import LearningService
from .agent_service import AgentService

__all__ = ['PlanningService', 'LearningService', 'AgentService']
```

**Checklist:**
- [ ] PlanningService created and tested
- [ ] LearningService created and tested
- [ ] AgentService created and tested
- [ ] Services depend only on domain, not infrastructure
- [ ] Services receive dependencies via constructor (DI)
- [ ] Application/ tests: 100% pass rate

---

### STEP 5: Create Infrastructure Implementations (3 hours)

**What to do:**
1. Implement all repository interfaces with file storage
2. Implement LLM provider abstraction
3. Implement memory/persistence layer

**Implementation:**
```python
# orchestrator/infrastructure/repositories/plan_repository.py

from orchestrator.domain.repositories import PlanRepository
from orchestrator.domain.entities import Plan

class FilePlanRepository(PlanRepository):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def save(self, plan: Plan) -> None:
        # File-based persistence
        pass

    def get(self, plan_id: str) -> Plan:
        # Load from file
        pass
```

**Checklist:**
- [ ] All repositories implemented
- [ ] LLM provider abstraction created
- [ ] Fireworks provider implemented
- [ ] Memory persistence layer working
- [ ] Infrastructure/ tests: 100% pass rate
- [ ] Can swap Fireworks ↔ mock provider without changing services

---

### STEP 6: Migrate API Layer (2 hours)

**What to do:**
1. Migrate Flask routes to new interfaces/ folder
2. Inject services into routes
3. Ensure request/response format unchanged

**Implementation:**
```python
# orchestrator/interfaces/api/app.py

from flask import Flask
from orchestrator.application.services import PlanningService
from orchestrator.interfaces.api.routes import create_planning_routes
from orchestrator.infrastructure.repositories import FilePlanRepository

def create_app():
    app = Flask(__name__)

    # Create repositories & services
    plan_repo = FilePlanRepository(base_path='./local-memory/plans')
    planning_service = PlanningService(plan_repo)

    # Register routes
    app.register_blueprint(create_planning_routes(planning_service))

    return app
```

**Checklist:**
- [ ] All routes migrated to interfaces/
- [ ] Services injected into routes
- [ ] API behavior unchanged (same request/response)
- [ ] Endpoints tests: 100% pass rate

---

### STEP 7: Identify & Remove Dead Code (2 hours)

**What to do:**
1. Find all unused functions, classes, imports
2. Verify no references before removing
3. Remove dead code
4. Run full test suite

**Implementation:**
```bash
# Identify candidates
grep -r "def " orchestrator/ | awk -F: '{print $2}' | sed 's/def //' | sed 's/(.*)//' > functions.txt

# Check each function's usage
for func in $(cat functions.txt); do
    count=$(grep -r "$func(" . --include="*.py" | wc -l)
    if [ $count -le 1 ]; then
        echo "DEAD: $func (referenced $count times)"
    fi
done

# Remove dead code manually
# Then test
pytest tests/ -v
```

**Checklist:**
- [ ] All dead code identified
- [ ] No references to dead code elsewhere
- [ ] Dead code removed
- [ ] Tests: 100% pass rate
- [ ] No new dead code introduced

---

### STEP 8: Full System Integration Test (2 hours)

**What to do:**
1. Start backend server
2. Test planning workflow end-to-end
3. Verify all components work together
4. Verify no behavior changes

**Implementation:**
```bash
# Start backend
python -m pytest tests/e2e/ -v

# Manual testing
# 1. Run planning iteration (should work identically)
# 2. Check memory access (should work identically)
# 3. Check learning (should work identically)
# 4. Check approvals (should work identically)
```

**Checklist:**
- [ ] Backend starts without errors
- [ ] Planning iteration: works identically
- [ ] Memory retrieval: works identically
- [ ] Learning: works identically
- [ ] Approvals: work identically
- [ ] Zero regressions
- [ ] All tests pass: 100%

---

## 7. CODE PATTERNS & EXAMPLES

### Pattern 1: Domain Entity (Pure Business Logic)

```python
# orchestrator/domain/entities/plan.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from shared.types import PlanStatus, AgentName

@dataclass
class PlanStep:
    """Single step in plan - domain entity"""
    order: int
    description: str
    agent_name: AgentName
    reasoning: str

    def is_valid(self) -> bool:
        return self.order > 0 and len(self.description) > 0

@dataclass
class Plan:
    """Planning entity - pure business logic"""
    id: str
    goal: str
    status: PlanStatus  # 'draft', 'executing', 'completed', 'rejected'
    created_at: datetime
    updated_at: datetime
    steps: List[PlanStep]
    approval_required: bool = True

    # Pure business methods (no I/O, no external dependencies)
    def is_ready_to_execute(self) -> bool:
        """Business rule: Plan has steps and isn't rejected"""
        return self.status != 'rejected' and len(self.steps) > 0

    def add_step(self, step: PlanStep) -> None:
        """Business rule: Add step, update timestamp"""
        self.steps.append(step)
        self.updated_at = datetime.now()

    def mark_complete(self) -> None:
        """Business rule: Mark plan complete"""
        self.status = 'completed'
        self.updated_at = datetime.now()

    def get_step_by_order(self, order: int) -> Optional[PlanStep]:
        """Business rule: Find step by order"""
        for step in self.steps:
            if step.order == order:
                return step
        return None
```

### Pattern 2: Repository Interface (Domain Layer)

```python
# orchestrator/domain/repositories/plan_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from orchestrator.domain.entities import Plan

class PlanRepository(ABC):
    """Abstract repository - depends only on domain"""

    @abstractmethod
    def save(self, plan: Plan) -> None:
        """Persist plan"""
        pass

    @abstractmethod
    def get(self, plan_id: str) -> Optional[Plan]:
        """Retrieve plan by ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Plan]:
        """Retrieve all plans"""
        pass

    @abstractmethod
    def delete(self, plan_id: str) -> None:
        """Delete plan"""
        pass
```

### Pattern 3: Application Service (Orchestration)

```python
# orchestrator/application/services/planning_service.py

from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from orchestrator.domain.entities import Plan, PlanStep
from orchestrator.domain.repositories import PlanRepository
from shared.exceptions import PlanNotFoundError, InvalidPlanError

class PlanningService:
    """Application service - orchestrates domain logic"""

    def __init__(self, plan_repository: PlanRepository):
        """Constructor injection of dependencies"""
        self.plan_repository = plan_repository

    def create_plan(self, goal: str) -> Plan:
        """Use case: Create new plan"""
        if not goal or len(goal) == 0:
            raise InvalidPlanError("Goal cannot be empty")

        plan = Plan(
            id=str(uuid4()),
            goal=goal,
            status='draft',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            steps=[]
        )
        self.plan_repository.save(plan)
        return plan

    def add_step(self, plan_id: str, step: PlanStep) -> Plan:
        """Use case: Add step to plan"""
        plan = self.plan_repository.get(plan_id)
        if not plan:
            raise PlanNotFoundError(f"Plan {plan_id} not found")

        if not step.is_valid():
            raise InvalidPlanError("Step is invalid")

        plan.add_step(step)  # Domain logic
        self.plan_repository.save(plan)
        return plan

    def list_plans(self) -> List[Plan]:
        """Use case: List all plans"""
        return self.plan_repository.get_all()
```

### Pattern 4: Repository Implementation (Infrastructure)

```python
# orchestrator/infrastructure/repositories/plan_repository.py

import json
import os
from pathlib import Path
from typing import Optional, List

from orchestrator.domain.repositories import PlanRepository
from orchestrator.domain.entities import Plan, PlanStep
from shared.exceptions import RepositoryError

class FilePlanRepository(PlanRepository):
    """File-based plan repository - implements abstract interface"""

    def __init__(self, base_path: str):
        """Constructor receives dependency (directory path)"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, plan: Plan) -> None:
        """Persist plan to file"""
        try:
            plan_file = self.base_path / f"{plan.id}.json"
            plan_data = {
                'id': plan.id,
                'goal': plan.goal,
                'status': plan.status,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat(),
                'steps': [
                    {
                        'order': step.order,
                        'description': step.description,
                        'agent_name': step.agent_name,
                        'reasoning': step.reasoning
                    }
                    for step in plan.steps
                ]
            }
            plan_file.write_text(json.dumps(plan_data, indent=2))
        except Exception as e:
            raise RepositoryError(f"Failed to save plan: {str(e)}")

    def get(self, plan_id: str) -> Optional[Plan]:
        """Load plan from file"""
        try:
            plan_file = self.base_path / f"{plan_id}.json"
            if not plan_file.exists():
                return None

            plan_data = json.loads(plan_file.read_text())
            # Convert to Plan entity
            # ... (conversion logic)
            return plan
        except Exception as e:
            raise RepositoryError(f"Failed to get plan: {str(e)}")

    def get_all(self) -> List[Plan]:
        """Load all plans from directory"""
        plans = []
        for plan_file in self.base_path.glob("*.json"):
            plan_data = json.loads(plan_file.read_text())
            # Convert and append
            # ... (conversion logic)
            plans.append(plan)
        return plans

    def delete(self, plan_id: str) -> None:
        """Delete plan file"""
        try:
            plan_file = self.base_path / f"{plan_id}.json"
            if plan_file.exists():
                plan_file.unlink()
        except Exception as e:
            raise RepositoryError(f"Failed to delete plan: {str(e)}")
```

### Pattern 5: API Route (Interface Layer)

```python
# orchestrator/interfaces/api/routes/planning_routes.py

from flask import Blueprint, request, jsonify
from orchestrator.application.services import PlanningService
from orchestrator.interfaces.api.dto import PlanDTO, CreatePlanRequest
from shared.exceptions import InvalidPlanError, PlanNotFoundError

def create_planning_routes(planning_service: PlanningService):
    """Factory function - creates routes with injected service"""

    bp = Blueprint('planning', __name__, url_prefix='/api/plans')

    @bp.route('', methods=['POST'])
    def create_plan():
        """POST /api/plans - Create new plan"""
        try:
            request_data = CreatePlanRequest.from_dict(request.json)
            plan = planning_service.create_plan(goal=request_data.goal)
            return jsonify(PlanDTO.from_entity(plan).to_dict()), 201
        except InvalidPlanError as e:
            return jsonify({'error': str(e)}), 400

    @bp.route('/<plan_id>', methods=['GET'])
    def get_plan(plan_id: str):
        """GET /api/plans/{plan_id} - Get plan details"""
        try:
            plan = planning_service.get_plan(plan_id)
            if not plan:
                return jsonify({'error': 'Plan not found'}), 404
            return jsonify(PlanDTO.from_entity(plan).to_dict()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return bp
```

---

## 8. INTEGRATION VERIFICATION

### How to Verify Architecture is Clean

After refactoring, verify:

**1. Dependency Flow is Correct**
```bash
# Check: Domain should import ONLY from domain/
grep -r "^from\|^import" orchestrator/domain/ | grep -v "from orchestrator.domain" | grep -v "from shared"
# RESULT: Should be zero lines (only internal domain imports allowed)

# Check: Application should import from domain only (not infrastructure)
grep -r "^from orchestrator.infrastructure\|^import.*infrastructure" orchestrator/application/
# RESULT: Should be zero lines (application never imports from infrastructure directly)

# Check: Interfaces can import from anywhere
grep -r "^from\|^import" orchestrator/interfaces/ | wc -l
# RESULT: Many lines (interfaces orchestrate everything)
```

**2. Repository Pattern is Used**
```bash
# Every service should receive repositories via constructor
grep -r "def __init__" orchestrator/application/services/ | grep Repository
# RESULT: Every service has Repository in constructor
```

**3. No Dead Code**
```bash
# No unused imports
python -m pylint orchestrator/ --disable=all --enable=unused-import

# No unused functions (rough check)
grep -r "def " orchestrator/ | grep "# UNUSED" | wc -l
# RESULT: Should be 0
```

**4. All Tests Pass**
```bash
pytest tests/ -v --cov=orchestrator/
# RESULT: 100% pass rate, good coverage
```

---

## 9. RISK/ISSUE SECTIONS (Proactive Problem-Solving)

### Risk 1: Circular Dependencies During Refactoring

**Problem:** While refactoring, you might accidentally create circular imports (A imports B, B imports A).

**How to Prevent:**
- Follow dependency flow strictly: Interfaces → Application → Domain
- Never import from outer layers in inner layers
- Use abstract interfaces (repository pattern)

**If You Encounter It:**
```python
# ERROR: ImportError: cannot import name 'PlanningService'
# LIKELY CAUSE: application/services/planning_service.py imports from interfaces/

# FIX:
# 1. Move shared logic to domain layer
# 2. Or use dependency injection to break cycle
# 3. Verify: grep "from orchestrator.interfaces" orchestrator/application/
#    Should return 0 results
```

---

### Risk 2: Breaking Existing Functionality

**Problem:** Refactoring might inadvertently change behavior.

**How to Prevent:**
- Run tests after EVERY step
- Don't combine refactoring with feature changes
- Preserve external API contracts

**If Tests Fail:**
```bash
# 1. Check git diff to see what changed
git diff HEAD~1 --name-only

# 2. Run failing tests in isolation
pytest tests/path/to/test_file.py -v

# 3. Compare old vs. new behavior
# - Expected output: same
# - New output: different
# Check what changed in the refactored code

# 4. Revert and try again
git revert HEAD
```

---

### Risk 3: Infrastructure Dependency Still Leaking

**Problem:** Service accidentally imports infrastructure layer (violates Clean Architecture).

**How to Catch It:**
```bash
# Scan for infrastructure imports in application/
grep -r "from orchestrator.infrastructure\|import.*infrastructure" orchestrator/application/

# If found:
# ERROR: infrastructure should NOT be imported in application layer

# FIX: Extract to domain as abstract interface, implement in infrastructure
```

---

### Risk 4: Test Coverage Drops

**Problem:** Refactoring loses test coverage.

**How to Monitor:**
```bash
# Before refactoring
pytest --cov=orchestrator/ --cov-report=term-missing > coverage_before.txt

# After refactoring
pytest --cov=orchestrator/ --cov-report=term-missing > coverage_after.txt

# Compare
diff coverage_before.txt coverage_after.txt
```

---

### Risk 5: Incompleteness - Refactoring Half-Done

**Problem:** Refactoring started but not finished, leaving code in inconsistent state.

**How to Prevent:**
- Use the step-by-step process
- Commit after each complete step
- Never leave refactoring incomplete

---

## 10. DECISION TREES (When You Hit Choices)

### Decision 1: Where Does This Code Belong?

```
"I have code for [feature]. Where does it go?"

IF code is pure business logic (no I/O, no frameworks):
  → PUT in orchestrator/domain/entities/
  → Example: Plan.is_ready_to_execute() method

ELSE IF code orchestrates domain logic (uses entities but not infrastructure):
  → PUT in orchestrator/application/services/
  → Example: PlanningService.create_plan() method

ELSE IF code implements persistence/external dependency:
  → PUT in orchestrator/infrastructure/
  → Example: FilePlanRepository, FireworksProvider

ELSE IF code handles HTTP requests/responses:
  → PUT in orchestrator/interfaces/api/
  → Example: Flask route handlers

ELSE:
  → Unclear. Discuss with team, likely needs decomposition
```

---

### Decision 2: Should I Create a Service for This?

```
"Should I create a new application service?"

IF functionality coordinates multiple domain entities:
  AND functionality represents a use case (user-facing action):
  AND multiple parts of the codebase need this logic:
  → YES, create a service
  → Example: PlanningService (coordinates Plan, Agent, Step entities)

ELSE IF functionality is just a single entity method:
  OR functionality is a utility helper:
  → NO, don't create a service
  → Example: Plan.is_valid() goes in domain entity, not a service

ELSE:
  → Create a service and let feedback tell you if wrong
```

---

### Decision 3: How to Handle Legacy Code?

```
"I found old code that doesn't fit Clean Architecture. What do I do?"

IF code is dead (unused):
  → DELETE it (with verification it's truly unused)

ELSE IF code is still used but messy:
  → REFACTOR it into Clean Architecture
  → Follow step-by-step process

ELSE IF code is external library/framework code:
  → ADAPT it in infrastructure/ layer
  → Don't modify the library code itself

ELSE:
  → Make a decision and document it
```

---

## 11. TESTING STRATEGY

### Test Structure

```
tests/
├── unit/                      (Pure unit tests, no dependencies)
│   ├── domain/                (Test domain entities in isolation)
│   ├── application/           (Test services with mocked repositories)
│   └── infrastructure/        (Test individual adapters)
├── integration/               (Test components together)
│   ├── test_planning_flow.py  (Plan creation → step addition → save)
│   └── test_agent_flow.py     (Agent selection → execution)
└── e2e/                       (Full system tests)
    └── test_planning_iteration.py  (Full planning workflow)
```

### Unit Test Example (Domain Entity)

```python
# tests/unit/domain/test_plan.py

from orchestrator.domain.entities import Plan, PlanStep
from datetime import datetime

def test_plan_add_step():
    """Test: Plan.add_step() adds step and updates timestamp"""
    plan = Plan(
        id='123',
        goal='Market entry',
        status='draft',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        steps=[]
    )

    step = PlanStep(
        order=1,
        description='Research market',
        agent_name='Planner',
        reasoning='Need baseline info'
    )

    plan.add_step(step)

    assert len(plan.steps) == 1
    assert plan.steps[0] == step
    # Note: updated_at changed, but we won't test exact time
```

### Integration Test Example (Service + Mock Repository)

```python
# tests/integration/test_planning_service.py

from unittest.mock import Mock
from orchestrator.application.services import PlanningService
from orchestrator.domain.entities import Plan

def test_planning_service_create_plan():
    """Test: PlanningService.create_plan() creates and saves plan"""

    # Mock repository
    mock_repo = Mock()
    mock_repo.save = Mock()

    # Create service with mocked repository
    service = PlanningService(plan_repository=mock_repo)

    # Execute use case
    plan = service.create_plan(goal='Market entry')

    # Verify behavior
    assert plan.goal == 'Market entry'
    assert plan.status == 'draft'
    mock_repo.save.assert_called_once_with(plan)
```

### End-to-End Test Example

```python
# tests/e2e/test_planning_iteration.py

def test_complete_planning_iteration():
    """Test: Complete planning iteration works end-to-end"""

    # 1. Create app with real repositories
    from orchestrator.interfaces.api.app import create_app
    app = create_app()
    client = app.test_client()

    # 2. Create plan via API
    response = client.post(
        '/api/plans',
        json={'goal': 'Market entry strategy'}
    )
    assert response.status_code == 201
    plan_id = response.json['id']

    # 3. Add step via API
    response = client.post(
        f'/api/plans/{plan_id}/steps',
        json={
            'order': 1,
            'description': 'Research market',
            'agent_name': 'Planner',
            'reasoning': 'Baseline info'
        }
    )
    assert response.status_code == 201

    # 4. Retrieve plan
    response = client.get(f'/api/plans/{plan_id}')
    assert response.status_code == 200
    assert len(response.json['steps']) == 1
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/domain/test_plan.py -v

# Run with coverage
pytest tests/ --cov=orchestrator/ --cov-report=html

# Run and stop on first failure
pytest tests/ -x
```

---

## 12. ROLLBACK STRATEGY

If something goes seriously wrong during refactoring:

### Option 1: Rollback Single Step

```bash
# If Step 4 (application services) broke things:
git log --oneline | head -20
# Find the commit before Step 4

git revert <commit_hash>
# Reverts just that step

# Fix the issue, try again
```

### Option 2: Full Rollback

```bash
# Go back to start of refactoring
git reset --hard <original_commit_hash>

# You're back to pre-refactoring state

# Analyze what went wrong
# Try a different approach
```

### Option 3: Parallel Branches

```bash
# While doing cleanup, keep original as backup
git checkout -b cleanup/clean-architecture
# Do all refactoring here

# If needed, compare with original
git diff main cleanup/clean-architecture

# Only merge when confident
git checkout main
git merge cleanup/clean-architecture
```

### How to Minimize Need for Rollback

1. **Commit frequently** - After each completed step
2. **Test continuously** - Run tests after every step
3. **Small refactorings** - Don't try to refactor everything at once
4. **Code review** - Have someone review before merging

---

## 13. COMPLETION CHECKLIST (Apply Process Framework)

### 1. DEVELOPMENT SPECIFICATION ✅
- [x] What is being developed? (Clean Architecture refactoring)
- [x] Why does this matter? (Foundation for multi-user, agents, chat)
- [x] Success criteria? (All 31+ modules refactored, zero dead code, all tests pass)

### 2. CODEBASE SCOPE ✅
- [x] Files that will change? (All Python files in orchestrator/, learning/, etc.)
- [x] Files that will be deleted? (Dead code, old experimental functions)
- [x] Files that will NOT change? (Frontend, local-memory/ structure)
- [x] Architecture diagram? (Yes, shown in section 4)

### 3. IMPLEMENTATION DETAILS ✅
- [x] Step-by-step execution? (8 steps, each detailed)
- [x] Code patterns? (Yes, 5 patterns with real code)
- [x] Integration points? (Yes, service injection, repository pattern)

### 4. CODE REMOVAL & CLEANUP ✅
- [x] Old code that must be deleted? (Dead code, unused functions)
- [x] Verification checklist? (Yes, grep-based verification)
- [x] Dead code audit? (Yes, search strategy provided)

### 5. VERIFICATION STRATEGY ✅
- [x] Unit tests? (Yes, test structure defined)
- [x] Integration tests? (Yes, service+repo tests)
- [x] Manual testing steps? (Yes, step-by-step)
- [x] Expected output? (Same behavior, new architecture)
- [x] How to rollback? (Git revert, parallel branches)

### 6. RISK/ISSUE SECTIONS ✅
- [x] Circular dependencies? (Yes, how to prevent and fix)
- [x] Breaking functionality? (Yes, testing strategy)
- [x] Infrastructure leakage? (Yes, grep verification)
- [x] Test coverage drop? (Yes, monitoring)
- [x] Incomplete refactoring? (Yes, step-by-step prevents this)

### 7. DECISION TREES ✅
- [x] Code placement? (Decision tree provided)
- [x] Service creation? (Decision tree provided)
- [x] Legacy code? (Decision tree provided)

---

## NEXT STEPS

After completing DEVELOPMENT_CYCLE_1:
1. Verify all tests pass (100%)
2. Confirm no behavioral changes
3. Mark Goal 1 as COMPLETE
4. Move to DEVELOPMENT_CYCLE_2 (Multi-User Memory)

**Estimated Timeline:** 1 full day (could be faster if code is clean, slower if lots of dead code)

---

**Document Status:** Complete & Ready for Execution
**Last Updated:** November 14, 2025
**Next Document:** DEVELOPMENT_CYCLE_2_MULTI_USER_MEMORY.md
