# 📦 VERSIONING AMENDMENT
## Semantic Versioning + Release Management

**Date**: 2026-06-23  
**Applies To**: Integration across all 9 phases  
**Status**: Active  

---

## 🎯 Core Versioning Strategy

### Semantic Versioning Format

```
MAJOR.MINOR.PATCH-STAGE

Examples:
v0.1.0-alpha  (initial pre-release)
v0.2.0-beta   (testing phase)
v1.0.0        (production release)
v1.0.1        (patch/hotfix)
v1.1.0        (minor feature)
v2.0.0        (breaking change)
```

### Version Components

| Component | When to Increment | Example |
|-----------|---|---|
| **MAJOR** | Breaking changes | v1.0.0 → v2.0.0 (API changed) |
| **MINOR** | New features (backward compatible) | v1.0.0 → v1.1.0 (added feature) |
| **PATCH** | Bug fixes | v1.0.0 → v1.0.1 (bug fixed) |
| **STAGE** | Pre-release phase | -alpha, -beta, -rc1 (release candidate) |

---

## 🏗️ Release Stages

### Stage 1: Alpha (Internal Testing)
```
Version: v0.x.x-alpha
Status: Highly unstable, feature-complete
Testing: Internal team only
Deployment: Development environment only
Backup: Not required
Duration: Until feature set stable
```

**When to move to Beta:**
- ✅ All features coded
- ✅ Core bugs fixed
- ✅ 80%+ test coverage
- ✅ Security scan passed

### Stage 2: Beta (Extended Testing)
```
Version: v0.x.x-beta
Status: Mostly stable, all bugs unknown
Testing: Trusted testers + internal team
Deployment: Staging/test environment
Backup: Daily backups
Duration: Until production-ready
```

**When to move to RC (Release Candidate):**
- ✅ No CRITICAL bugs in beta
- ✅ No HIGH bugs blocking release
- ✅ Documentation complete
- ✅ Runbooks tested

### Stage 3: Release Candidate (Pre-Production)
```
Version: v1.0.0-rc1
Status: Stable, ready for production
Testing: Full regression testing
Deployment: Production environment (careful)
Backup: Multiple backups + 3-location redundancy
Duration: 1-2 weeks before release
```

**When to move to Stable Release:**
- ✅ 0 CRITICAL bugs in RC
- ✅ 0 HIGH bugs in RC
- ✅ All tests passing (175+)
- ✅ All runbooks tested
- ✅ Operator trained

### Stage 4: Stable Release (Production)
```
Version: v1.0.0
Status: Production-ready
Testing: All testing complete
Deployment: Production environment
Backup: Continuous + 3-location redundancy
Support: Full support
Duration: Until next version
```

---

## 📋 Release Checklist

**Every release must pass:**

```
RELEASE CHECKLIST (Mandatory):

Code Quality:
  ✅ All tests passing (175+)
  ✅ Code coverage 80%+
  ✅ Type checking passes (mypy)
  ✅ Security scan passes (bandit)
  ✅ No CRITICAL/HIGH bugs remaining

Testing:
  ✅ Unit tests: 100% passing
  ✅ Integration tests: 100% passing
  ✅ E2E tests: 100% passing
  ✅ Regression tests: 100% passing
  ✅ Manual testing complete

Security:
  ✅ No hardcoded secrets
  ✅ No credential leaks
  ✅ File permissions correct
  ✅ Input validation complete
  ✅ No OWASP vulnerabilities

Documentation:
  ✅ CHANGELOG.md updated
  ✅ Runbooks tested
  ✅ Architecture docs current
  ✅ README.md accurate
  ✅ API docs complete

Deployment:
  ✅ Backup created (3+ locations)
  ✅ Rollback procedure documented
  ✅ Operator trained
  ✅ Deployment checklist passed
  ✅ Pre-flight checks: 25/25 passed

Operations:
  ✅ Monitoring configured
  ✅ Alerts tested
  ✅ Telegram notifications ready
  ✅ Daily loss limits enforced
  ✅ Position reconciliation working

Status: ✅ APPROVED FOR RELEASE
```

**If ANY check fails: STOP. Don't release. Fix and re-check.**

---

## 🏷️ Git Tagging Strategy

### Tag Format

```
git tag -a v1.0.0 -m "Release v1.0.0: Production-ready system"
```

### Tags Created At Each Stage

**Alpha Release:**
```
git tag v0.1.0-alpha
```

**Beta Release:**
```
git tag v0.2.0-beta
```

**Release Candidate:**
```
git tag v1.0.0-rc1
```

**Stable Release:**
```
git tag v1.0.0
```

### Tag Information Includes

```
Tag: v1.0.0
Date: 2026-06-30
Commit: abc123def456
Stage: Stable Release
Changes: Fixed 8 CRITICAL bugs, added position reconciliation
Tests: 175/175 passing, 88% coverage
Deployment: Production ready
Backup: Created at 3 locations
Rollback: Documented and tested
```

---

## 📝 CHANGELOG.md Management

### Format

```markdown
# CHANGELOG

## [1.0.0] - 2026-06-30
### Added
- Order fill confirmation polling
- Position reconciliation (bidirectional)
- Retry logic with exponential backoff

### Fixed
- BUG-001: Order rejection orphans position
- BUG-002: Race condition in exit logic
- BUG-003: Daily loss limits not enforced

### Changed
- OrderManager now requires config object (not bool)
- Improved error messages for order rejection

### Security
- File permissions: 0o600 for credentials.json
- Logging: Sanitized all API responses
- Secrets: Added .gitignore protection

### Tests
- Added 25+ new tests
- Coverage: 88% (target: 80%+)
- All regression tests passing

### Deployment
- Backward compatible with v0.2.0
- No data migration required
- Rollback to v0.2.0 supported

## [0.2.0-beta] - 2026-06-15
...
```

### What to Document in CHANGELOG

✅ **Added**: New features  
✅ **Fixed**: Bug fixes  
✅ **Changed**: Behavior changes  
✅ **Removed**: Removed features  
✅ **Deprecated**: Features going away  
✅ **Security**: Security fixes  
✅ **Tests**: Testing improvements  
✅ **Performance**: Performance changes  

---

## 🔄 Version Increment Strategy

### When to Increment PATCH (v1.0.0 → v1.0.1)

**Increment PATCH for:**
- ✅ Bug fixes (no new features)
- ✅ Security patches
- ✅ Performance improvements
- ✅ Documentation fixes

**Example:**
```
v1.0.0 → v1.0.1
Fixed: Race condition in order exit logic
Tests: All passing, no behavior change
Backward compatible: Yes
```

### When to Increment MINOR (v1.0.0 → v1.1.0)

**Increment MINOR for:**
- ✅ New features (backward compatible)
- ✅ API additions (not changes)
- ✅ Significant improvements

**Example:**
```
v1.0.0 → v1.1.0
Added: Position reconciliation feature
Tests: 10 new tests, 88% → 89% coverage
Backward compatible: Yes
```

### When to Increment MAJOR (v1.0.0 → v2.0.0)

**Increment MAJOR for:**
- ✅ Breaking API changes
- ✅ Incompatible behavior changes
- ✅ Major architectural changes

**Example:**
```
v1.0.0 → v2.0.0
Changed: API completely rewritten
Breaking: Old API no longer supported
Backward compatible: No
Migration: Provided
```

---

## 📦 Release Workflow

### Step 1: Create Release Branch
```bash
git checkout main
git pull origin main
git checkout -b release/v1.0.0
```

### Step 2: Update Version Numbers
```
Update in:
- src/__init__.py (version = "1.0.0")
- README.md (version reference)
- CHANGELOG.md (new section)
```

### Step 3: Run Full Checklist
```
✅ All tests passing
✅ Code coverage 80%+
✅ Security scan passed
✅ Preflight checks 25/25
✅ Documentation updated
```

### Step 4: Create Release Commit
```bash
git commit -m "Release: v1.0.0"
```

### Step 5: Create Tag
```bash
git tag -a v1.0.0 -m "Release v1.0.0: Production-ready system"
```

### Step 6: Create Backup
```bash
./backup.sh  # Creates 3 backups
```

### Step 7: Merge to Main
```bash
git checkout main
git merge --no-ff release/v1.0.0
git push origin main
git push origin v1.0.0
```

### Step 8: Deploy
```
1. Backup current production
2. Deploy v1.0.0
3. Run post-deployment checks
4. Document in FIX_LOG.md
```

---

## 📊 Version Lifecycle

```
DEVELOPMENT (v0.x.x-alpha)
  ↓ Feature complete + 80%+ coverage
  ↓
BETA TESTING (v0.x.x-beta)
  ↓ No CRITICAL bugs, documentation ready
  ↓
RELEASE CANDIDATE (v1.0.0-rc1)
  ↓ No CRITICAL/HIGH bugs, runbooks tested
  ↓
STABLE RELEASE (v1.0.0)
  ↓
MAINTENANCE (v1.0.1, v1.0.2, ...)
  ↓ Bug fixes
  ↓
END OF LIFE (v0.x.x, older versions)
  ↓ Deprecated, archive, eventually remove
```

---

## 🔐 Version-Based Rollback

### Quick Rollback Procedure

**If production breaks:**
```bash
# Check available versions
git tag | grep v

# Rollback to previous version
git checkout v1.0.0  # Current broken version
git checkout v0.2.0  # Previous stable version

# Or restore from backup
./restore.sh backup-2026-06-30-v1.0.0
```

### Version Compatibility Matrix

```
Current → Can Rollback To
v1.0.1  → v1.0.0, v0.2.0-beta
v1.0.0  → v0.2.0-beta
v0.2.0  → v0.1.0-alpha
```

---

## 📋 Version Tracking

### Version Registry (in code)

```python
# src/__init__.py
__version__ = "1.0.0"
__released__ = "2026-06-30"
__stage__ = "stable"
__status__ = "production-ready"

VERSION_HISTORY = {
    "1.0.0": {
        "released": "2026-06-30",
        "stage": "stable",
        "tests": "175/175 passing",
        "coverage": "88%",
        "status": "production-ready"
    },
    "0.2.0-beta": {
        "released": "2026-06-15",
        "stage": "beta",
        "tests": "150/150 passing",
        "coverage": "85%",
        "status": "ready for extended testing"
    }
}
```

### Version Display

```python
# Show version at startup
def show_version():
    print(f"F&O Trading Bot v{__version__} ({__stage__})")
    print(f"Released: {__released__}")
    print(f"Status: {__status__}")
```

---

## 🎯 Integration with 9-Phase Workflow

### Phase 2 (Planning)
- Determine version increment (PATCH/MINOR/MAJOR)
- Plan stage progression (alpha → beta → rc → stable)

### Phase 6 (Documentation)
- Update CHANGELOG.md
- Update version numbers

### Phase 7 (Preflight)
- Verify version is unique
- Verify tag doesn't already exist
- Verify version in code matches tag

### Phase 8 (Deployment)
- Create git tag
- Create backup with version name
- Document in deployment log

### Phase 9 (Continuous Improvement)
- Track version metrics
- Plan next version based on issues found
- Maintain version compatibility

---

## 📊 Release Tracking

**Track in FIX_LOG.md:**
```markdown
## Release v1.0.0 - 2026-06-30

**Stage**: Stable Release  
**Tests**: 175/175 passing  
**Coverage**: 88%  
**Bugs Fixed**: 8 CRITICAL + 8 HIGH  
**New Features**: Position reconciliation  
**Deployment**: Production  
**Backup**: 3-location redundancy  
**Status**: ✅ Live and stable  
```

---

## ✅ Versioning Checklist

**Before every release:**

- [ ] Version number determined (PATCH/MINOR/MAJOR)
- [ ] CHANGELOG.md updated
- [ ] Version in code updated
- [ ] Release branch created
- [ ] All tests passing
- [ ] Security scan passed
- [ ] Release checklist passed
- [ ] Backup created (3+ locations)
- [ ] Git tag created
- [ ] Merged to main
- [ ] Deployed successfully
- [ ] Post-deployment checks passed
- [ ] FIX_LOG.md updated

**All checks MUST pass before release.**

---

## 🎓 Summary

**Versioning provides:**
- ✅ Clear release progression (alpha → beta → rc → stable)
- ✅ Rollback capability (easy to return to previous version)
- ✅ Change tracking (CHANGELOG documents everything)
- ✅ Quality gates (release checklist ensures quality)
- ✅ Version compatibility (know what can rollback to)
- ✅ Deployment confidence (versions are tested)

**Result**: Professional release management with safety net for rollbacks.

---

**Status**: Active  
**Effective**: 2026-06-23  
**Next Review**: 2026-09-23 (quarterly)
