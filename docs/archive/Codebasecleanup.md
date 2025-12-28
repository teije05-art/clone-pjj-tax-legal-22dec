# Safe Codebase Cleanup Plan for Collaborative Development

**Status**: Ready for Implementation
**Context**: Preparing memagent-modular-fixed for parallel development with partner
**User Level**: Complete beginner - prioritize safety over speed
**Primary Concern**: Partner says code "looks vibecoded" and is too messy to work on

---

## Executive Summary

The codebase structure is actually **reasonably well-organized** with clear separation between old and new systems. However, there are **critical configuration issues** that make it unprofessional:

**Critical Issues Found**:
1. ⚠️ **No .gitignore file** - cache files tracked in git (1,290 uncommitted changes)
2. 🔴 **SECURITY: Hardcoded API key** exposed in git history
3. 🗑️ **12 __pycache__ directories** with 69 .pyc files being tracked
4. 🗑️ **10 .DS_Store files** (Mac system files) tracked in git
5. 📁 **Legacy code bloat** - Old/ directory (17k lines, deprecated)
6. 📁 **No root README.md** - no project overview for collaborators
7. ⚙️ **Configuration scattered** - pyproject.toml nested deep, .venv in wrong location

**Safety Approach**: 7 phases with git backups before each destructive operation

---

## Phase 0: Pre-Cleanup Backup (CRITICAL - DO THIS FIRST)

### Create Safety Net

```bash
# 1. Create backup branch
cd /Users/teije/Desktop/memagent-modular-fixed
git checkout -b backup-before-cleanup

# 2. Commit current state (including all uncommitted changes)
git add -A
git commit -m "BACKUP: Pre-cleanup snapshot with all uncommitted changes"

# 3. Create archive tag
git tag pre-cleanup-archive

# 4. Return to main branch
git checkout main
git checkout -b feature/codebase-cleanup

# 5. Verify backup exists
git log --oneline backup-before-cleanup -1
git tag -l pre-cleanup-archive
```

**Rollback Plan**: If anything breaks, run:
```bash
git checkout main
git reset --hard backup-before-cleanup
```

---

## Phase 1: Create .gitignore (HIGH PRIORITY)

### Problem
No root-level .gitignore exists. Cache files, virtual environments, and system files are being tracked in git.

### Solution: Create Comprehensive .gitignore

**File**: `/Users/teije/Desktop/memagent-modular-fixed/.gitignore`

```gitignore
# Python cache and compiled files
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
.venv/
venv/
ENV/
env/
.Python

# Distribution / packaging
*.egg-info/
dist/
build/
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Mac OS
.DS_Store
.AppleDouble
.LSOverride

# Logs
*.log
logs/
*.log.*

# Environment variables (IMPORTANT - protect API keys)
.env
.env.local
.env.*.local

# Streamlit
.streamlit/

# Project-specific
local-memory/tax_legal/*.json
streamlit_instance_info/
systemsettings_cache/
```

**Commands**:
```bash
cd /Users/teije/Desktop/memagent-modular-fixed

# Create .gitignore
cat > .gitignore << 'EOF'
[paste content above]
EOF

# Add and commit
git add .gitignore
git commit -m "Add comprehensive .gitignore for Python project"
```

**Safety**: This only ADDS a file, doesn't delete anything. 100% safe.

---

## Phase 2: Remove Tracked Cache Files (REQUIRES CARE)

### Problem
1,290+ cache files currently tracked in git and showing as uncommitted changes.

### Solution: Untrack Without Deleting Local Files

**Commands**:
```bash
cd /Users/teije/Desktop/memagent-modular-fixed

# Remove __pycache__ from git tracking (but keep local files)
git rm -r --cached PJJ-Tax\&Legal/agent/__pycache__
git rm -r --cached PJJ-Tax\&Legal/orchestrator/__pycache__
git rm -r --cached PJJ-Tax\&Legal/orchestrator/agents/__pycache__
git rm -r --cached PJJ-Tax\&Legal/orchestrator/tax_workflow/__pycache__
git rm -r --cached Old/PJJ-planning-old/__pycache__
git rm -r --cached Old/PJJ-planning-old/agents/__pycache__
git rm -r --cached Old/PJJ-planning-old/context/__pycache__
git rm -r --cached Old/PJJ-planning-old/integration/__pycache__
git rm -r --cached Old/PJJ-planning-old/learning/__pycache__
git rm -r --cached Old/PJJ-planning-old/memory/__pycache__
git rm -r --cached Old/PJJ-planning-old/reasoning/__pycache__
git rm -r --cached Old/PJJ-planning-old/templates/__pycache__

# Remove .DS_Store files
find . -name .DS_Store | xargs git rm --cached

# Remove egg-info
git rm -r --cached PJJ-Tax\&Legal/agent/agent.egg-info

# Commit the untracking
git commit -m "Untrack Python cache files, .DS_Store, and build artifacts"
```

**Safety Notes**:
- `--cached` flag means files are removed from git tracking ONLY, not from disk
- Your local __pycache__ directories will still exist and work
- They just won't be committed to git anymore

**Verification**:
```bash
# Verify files still exist locally
ls PJJ-Tax\&Legal/agent/__pycache__/  # Should show files

# Verify git no longer tracks them
git status  # Should not show __pycache__ anymore
```

---

## Phase 3: Fix Security Issue - API Key Exposure (CRITICAL)

### Problem
🔴 **SECURITY VULNERABILITY**: Fireworks API key hardcoded in:
- `PJJ-Tax&Legal/agent/settings.py` (line 15)
- `PJJ-Tax&Legal/agent/fireworksscript.py` (line 15)

**Exposed Key**: `fw_3ZG1oZ5Pde7LFHrsad8wPQUc`

This key is in git history and accessible to anyone who clones the repository.

### Solution: Use Environment Variables

**Step 1: Rotate the API Key**
1. Go to Fireworks AI dashboard
2. Revoke key `fw_3ZG1oZ5Pde7LFHrsad8wPQUc`
3. Generate new key

**Step 2: Create .env File** (NEVER commit this)
```bash
cd /Users/teije/Desktop/memagent-modular-fixed
cat > .env << 'EOF'
FIREWORKS_API_KEY=your_new_key_here
EOF
```

**Step 3: Update Code**

File: `PJJ-Tax&Legal/agent/settings.py` (lines 14-15)
```python
# BEFORE (BAD):
# Fireworks API key
FIREWORKS_API_KEY = "fw_3ZG1oZ5Pde7LFHrsad8wPQUc"

# AFTER (GOOD):
# Fireworks API key (load from environment)
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise ValueError("FIREWORKS_API_KEY environment variable not set. Please add it to .env file")
```

File: `PJJ-Tax&Legal/agent/fireworksscript.py` (lines 14-15)
```python
# BEFORE (BAD):
# from fireworks.client import Fireworks
# fw = Fireworks(api_key="fw_3ZG1oZ5Pde7LFHrsad8wPQUc")

# AFTER (GOOD):
import os
from dotenv import load_dotenv
load_dotenv()

from fireworks.client import Fireworks
api_key = os.getenv("FIREWORKS_API_KEY")
if not api_key:
    raise ValueError("FIREWORKS_API_KEY not found in environment")
fw = Fireworks(api_key=api_key)
```

**Step 4: Commit Changes**
```bash
git add PJJ-Tax\&Legal/agent/settings.py PJJ-Tax\&Legal/agent/fireworksscript.py
git commit -m "Security: Remove hardcoded API key, use environment variables"
```

**Step 5: Clean Git History** (Optional but Recommended)
```bash
# WARNING: This rewrites history - only do if repo is private or not yet shared
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PJJ-Tax\&Legal/agent/settings.py || true" \
  --prune-empty --tag-name-filter cat -- --all
```

**Alternative**: If repo already shared, just rotate the key and move on. The old key in history is now invalid.

---

## Phase 4: Archive Legacy Code (SAFE - REVERSIBLE)

### Problem
- `Old/PJJ-planning-old/` directory (17,374 lines, completely deprecated)
- `database-extraction-old/` directory (legacy extraction scripts)

These directories bloat the codebase and confuse new developers.

### Solution: Move to Archive Branch

**Commands**:
```bash
cd /Users/teije/Desktop/memagent-modular-fixed

# Create archive branch
git checkout -b archive/legacy-code

# Move old code to this branch (it stays in history, just not in main)
git checkout main

# Create .archive directory
mkdir -p .archive

# Move directories
mv Old/ .archive/
mv database-extraction-old/ .archive/

# Update .gitignore to ignore archive
echo ".archive/" >> .gitignore

# Commit removal
git add -A
git commit -m "Archive legacy code: Move Old/ and database-extraction-old/ to .archive/"
```

**Rollback Plan**:
```bash
# To restore archived code:
mv .archive/Old/ ./
mv .archive/database-extraction-old/ ./
git add -A
git commit -m "Restore archived code"
```

**Safety**: Code is not deleted, just moved to a local folder that git ignores. You can always restore it.

---

## Phase 5: Clean Up Physical Cache Files (SAFE)

### Problem
12 __pycache__ directories and 69 .pyc files exist on disk (no longer tracked after Phase 2).

### Solution: Delete Local Cache Files

**Commands**:
```bash
cd /Users/teije/Desktop/memagent-modular-fixed

# Delete all __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} +

# Delete all .pyc files
find . -type f -name "*.pyc" -delete

# Delete all .DS_Store files
find . -type f -name .DS_Store -delete

# Delete egg-info
rm -rf PJJ-Tax\&Legal/agent/agent.egg-info

# Verify cleanup
find . -name __pycache__  # Should return nothing
find . -name "*.pyc"      # Should return nothing
find . -name .DS_Store    # Should return nothing
```

**Safety**: These are automatically regenerated by Python when you run code. Deleting them is 100% safe.

---

## Phase 6: Reorganize Project Structure (MEDIUM RISK)

### Problem
- `.venv` nested in `systemsettings_cache/system-technical-specs/`
- `pyproject.toml` not at root
- No root README

### Solution: Standardize Structure

**Step 1: Move pyproject.toml to Root**
```bash
cd /Users/teije/Desktop/memagent-modular-fixed

# Copy pyproject.toml to root (preserving original)
cp PJJ-Tax\&Legal/systemsettings_cache/system-technical-specs/pyproject.toml ./

# Update paths in pyproject.toml if needed
# (likely needs adjustment for package discovery)

git add pyproject.toml
git commit -m "Move pyproject.toml to project root for standard structure"
```

**Step 2: Create Root README.md**
```bash
cat > README.md << 'EOF'
# PJJ Tax & Legal AI System

**Domain**: Vietnamese Tax & Legal Advisory
**Architecture**: Multi-agent orchestration with memory-based constraint boundaries

## Project Structure

```
memagent-modular-fixed/
├── PJJ-Tax&Legal/          # Active tax legal agent system
│   ├── agent/              # Core agent with Fireworks LLM
│   ├── orchestrator/       # 6-step tax workflow orchestration
│   └── [other components]
├── local-memory/           # Tax database index & response cache
├── claudecodedocs_MD/      # Planning docs & technical specs
└── [configuration files]
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -e .
   ```

2. **Configure API key** (create `.env` file):
   ```bash
   FIREWORKS_API_KEY=your_key_here
   ```

3. **Run Streamlit frontend**:
   ```bash
   cd PJJ-Tax&Legal/orchestrator/tax_workflow/frontend
   streamlit run tax_app.py
   ```

## Architecture

- **Agent System**: Constrained memory navigation with Fireworks Llama 3.3 70B
- **Tax Workflow**: 6-agent pipeline (Planner → Searcher → Recommender → Compiler → Verifier → Tracker)
- **Constraint Boundaries**: Category-based directory constraints enforced via prompt engineering

## Development

- Python: 3.11
- Main dependencies: fireworks-ai, pydantic, streamlit, python-dotenv
- See `pyproject.toml` for full dependency list

## Documentation

See `claudecodedocs_MD/planningcurrent/` for current planning documents and system status.
EOF

git add README.md
git commit -m "Add root README with project overview and setup instructions"
```

**Step 3: Handle .venv** (Optional - Risky for Beginners)
```bash
# DON'T MOVE .venv - just document it
# Moving virtual environments can break paths
# Instead, document in README how to create a new one at root:

# Add to README.md:
cat >> README.md << 'EOF'

## Note on Virtual Environment

The project currently has a venv at `PJJ-Tax&Legal/systemsettings_cache/system-technical-specs/.venv/`.

For new setup, create a fresh venv at project root:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```
EOF

git add README.md
git commit -m "Document virtual environment setup"
```

**Safety**: Moving .venv is risky - skip it. Just document it and create a new one later.

---

## Phase 7: Final Cleanup and Verification

### Create .github Directory for Collaboration

```bash
mkdir -p .github

# Add CODEOWNERS file
cat > .github/CODEOWNERS << 'EOF'
# Code ownership for pull requests
* @teije05-art
/PJJ-Tax&Legal/agent/ @teije05-art
/PJJ-Tax&Legal/orchestrator/ @teije05-art @partner-username
EOF

# Add PR template
cat > .github/pull_request_template.md << 'EOF'
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] Documentation updated

## Checklist
- [ ] Code follows project style
- [ ] No hardcoded secrets
- [ ] Passes all tests
EOF

git add .github/
git commit -m "Add GitHub collaboration templates"
```

### Final Verification Checklist

```bash
# 1. Verify .gitignore working
git status  # Should NOT show __pycache__, .venv, .DS_Store

# 2. Verify no secrets
grep -r "fw_3ZG" PJJ-Tax\&Legal/  # Should return nothing

# 3. Verify structure
tree -L 2 -I '__pycache__|.venv|*.pyc'

# 4. Run tests
cd PJJ-Tax\&Legal
python -m pytest  # Verify nothing broke

# 5. Test Streamlit
cd orchestrator/tax_workflow/frontend
streamlit run tax_app.py  # Verify UI works
```

---

## Summary of Changes

| Phase | Changes | Risk Level | Reversible? |
|-------|---------|------------|-------------|
| 0 | Create backup branch | None | N/A |
| 1 | Add .gitignore | None | Yes (git rm) |
| 2 | Untrack cache files | Low | Yes (git add) |
| 3 | Fix API key security | Low | No (but necessary) |
| 4 | Archive legacy code | Low | Yes (move back) |
| 5 | Delete physical cache files | None | Yes (regenerated automatically) |
| 6 | Add README, move pyproject.toml | Low | Yes (git revert) |
| 7 | Add GitHub templates | None | Yes (git rm) |

**Total Time Estimate**: 2-3 hours
**Lines of Code Removed from Main**: ~17,374 (archived, not deleted)
**Files Cleaned**: 69 .pyc + 12 __pycache__ + 10 .DS_Store + 1 .egg-info = 92 files

---

## Partner Concerns Addressed

**Before Cleanup**:
- ❌ No .gitignore - cache files in git
- ❌ 1,290 uncommitted changes (cache spam)
- ❌ API key exposed in code
- ❌ No README explaining structure
- ❌ Legacy code bloating repo (17k lines)
- ❌ .DS_Store tracked everywhere

**After Cleanup**:
- ✅ Professional .gitignore
- ✅ Clean git status
- ✅ Environment-based configuration
- ✅ Clear README with setup instructions
- ✅ Legacy code archived
- ✅ System files properly ignored
- ✅ GitHub collaboration templates

---

## Rollback Instructions (If Something Breaks)

```bash
# Full rollback to pre-cleanup state
git checkout main
git reset --hard backup-before-cleanup

# Partial rollback - undo last commit only
git reset --hard HEAD~1

# Restore specific file
git checkout backup-before-cleanup -- path/to/file

# Verify backup still exists
git log backup-before-cleanup --oneline -5
```

---

## Post-Cleanup Collaboration Setup

1. **Push cleaned codebase**:
   ```bash
   git push origin feature/codebase-cleanup
   ```

2. **Create Pull Request** on GitHub:
   - Title: "Codebase cleanup for collaborative development"
   - Description: Reference this cleanup plan
   - Request partner review

3. **Share with partner**:
   - Invite collaborator to GitHub repo
   - Share .env template (without actual key)
   - Point them to README.md for setup

4. **Establish workflow**:
   - All changes via feature branches
   - PR required for merges
   - Partner uses CODEOWNERS for review assignment

---

**Status**: Ready for implementation. Execute phases sequentially with git commits after each phase.
