# 🤖 ANTIGRAVITY STANDARD WORKFLOW
## Master Development Framework for All Future Work

**Document**: ANTIGRAVITY_STANDARD_WORKFLOW.md  
**Status**: Standing Instruction (Use for ALL development work)  
**Version**: 1.0  
**Updated**: 2026-06-23  

---

## 📌 QUICK START FOR YOUR BROTHER ARUN

**Every time you want Antigravity to do work, use this format:**

```
@Antigravity: [TASK TYPE] [Description]

REFERENCE: Use ANTIGRAVITY_STANDARD_WORKFLOW.md
```

**Examples:**
- `@Antigravity: FIX BUG-001: Order rejection orphans position (Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md)`
- `@Antigravity: FEATURE: Add position reconciliation (Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md)`
- `@Antigravity: ENHANCE: Improve order fill confirmation (Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md)`
- `@Antigravity: THINK: How can we improve risk management? (Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md)`

**That's it. Antigravity will automatically:**
1. ✅ Plan the approach (aligned with vision/goals)
2. ✅ Test-first development (TDD)
3. ✅ Security scanning
4. ✅ Code review
5. ✅ Regression testing
6. ✅ Documentation + alignment check
7. ✅ Preflight verification
8. ✅ Ready to deploy

---

# 🎯 PHASE 1: INTAKE & VISION ALIGNMENT

## When ANY request comes in:

### 1.1 Validate Against Project Vision & Goals
**Antigravity must check:**
- Does this align with VISION_AND_GOALS.md?
- Is this moving us toward "production-ready system"?
- Does this support the 4-week roadmap?
- Is this solving a real problem or adding complexity?

**If misaligned**, Antigravity should:
```
⚠️ MISALIGNED: This work conflicts with [Vision Point X]
   Current direction: [X]
   This work: [Y]
   Recommendation: [Z]
   Ask Arun: Proceed anyway or pivot?
```

**If aligned**, proceed to Phase 2.

### 1.2 Categorize the Work
**Work Types:**
- 🔴 **CRITICAL**: Safety issue, capital loss risk, data corruption
- 🟠 **HIGH**: Reliability issue, performance issue, security issue
- 🟡 **MEDIUM**: Enhancement, technical debt, documentation
- 🟢 **LOW**: Nice-to-have, refactoring, code cleanup

**Severity determines timeline & review depth.**

### 1.3 Estimate Scope
**Ask:**
- How many files affected?
- Which modules impacted?
- Risk of regression? (HIGH/MEDIUM/LOW)
- Estimated effort?

**Report to Arun:**
```
SCOPE: [files affected]
RISK: [regression risk]
EFFORT: [X hours estimated]
TIMELINE: [X days]
```

---

# 🏗️ PHASE 2: PLANNING & ARCHITECTURE

## 2.1 Use Architect Agent
**Antigravity orchestrates architect agent:**
- [ ] Analyze current code structure
- [ ] Identify affected modules
- [ ] Design approach (minimal, focused change)
- [ ] Identify potential regressions
- [ ] List all files to modify
- [ ] Create step-by-step implementation plan

**Output: Detailed implementation plan**

## 2.2 Define Success Criteria
**For the work, define:**
- ✅ **Functional**: What behavior must work?
- ✅ **Non-Functional**: Performance, memory, security?
- ✅ **Testing**: What tests prove it works?
- ✅ **Integration**: What existing functionality must not break?

**Example:**
```
FUNCTIONAL:
- Order rejection must NOT delete position from memory
- System must retry rejected orders with backoff
- Operator must get alert after 3 failures

NON-FUNCTIONAL:
- Retry logic must complete < 500ms
- Memory overhead < 1MB

TESTING:
- test_order_rejection_keeps_position() passes
- test_retry_backoff() passes
- 5+ regression tests pass

INTEGRATION:
- All existing 25 critical tests still pass
- Daily loss limit still enforced
- Telegram alerts still fire
```

## 2.3 Check Against 4 Core Principles
**PRINCIPLES_CHECKLIST.md must be satisfied:**

| Principle | Check | Status |
|-----------|-------|--------|
| **Principle 1: Test-First** | Will this have TDD? | [ ] ✅ |
| **Principle 2: One Commit** | One clear change? | [ ] ✅ |
| **Principle 3: Code Review** | Will code be reviewed? | [ ] ✅ |
| **Principle 4: Security First** | No secrets leaked? | [ ] ✅ |

**If any principle violated, STOP and ask Arun.**

---

# 🧪 PHASE 3: TEST-FIRST DEVELOPMENT (TDD)

## 3.1 Write Tests BEFORE Code
**Antigravity must orchestrate tdd-guide agent:**

**Step 1: RED (Test Fails)**
```python
# Write test FIRST - it should FAIL initially
def test_order_rejection_keeps_position():
    """Position should survive rejected SELL order"""
    bot = TradingBot(config)
    position = bot.enter_trade("BANKNIFTY")
    assert position.id in bot.positions
    
    # Order gets rejected
    broker.reject_next_order()
    bot.exit_trade(position.id)
    
    # Position should STILL exist (bug was deleting it)
    assert position.id in bot.positions, "BUG: Position deleted despite rejection!"
    assert position.status == PositionStatus.OPEN
```

**Step 2: GREEN (Implement Minimal Fix)**
```python
# Implement ONLY what's needed to pass test
order = order_manager.place_order(...)
if order.status == OrderStatus.PLACED:  # Only if successful
    bot.exit_trade(...)
else:
    logger.critical(f"Order REJECTED. Position {position_id} remains open. Will retry.")
    # Position stays in memory
```

**Step 3: IMPROVE (Refactor)**
```python
# Add retry logic, error handling, etc.
def exit_trade_with_retry(position_id, max_retries=3):
    for attempt in range(max_retries):
        order = order_manager.place_order(...)
        if order.status == OrderStatus.PLACED:
            return True
        logger.warning(f"Attempt {attempt+1} failed. Retrying in {backoff_ms}ms")
        time.sleep(backoff_ms)
    
    logger.critical(f"Order failed after {max_retries} attempts. Manual intervention needed.")
    send_alert_to_operator()
    return False
```

## 3.2 Coverage Target: 80%+
**Antigravity must verify:**
```
Coverage Report:
  Module A: 92% ✅
  Module B: 85% ✅
  Module C: 78% ❌ (Below 80%, fix needed)
  
Total: 88% ✅ (Meets 80%+ target)
```

**If coverage < 80%, FAIL and request more tests.**

## 3.3 Test Categories
**Write tests across 3 categories:**

| Category | What | Example | Count |
|----------|------|---------|-------|
| **Unit Tests** | Individual functions | test_calculate_pnl() | 60-70% |
| **Integration Tests** | API interactions | test_place_order_with_broker() | 20-30% |
| **E2E Tests** | Full workflows | test_complete_trade_entry_to_exit() | 5-10% |

---

# 🔒 PHASE 4: SECURITY & VALIDATION

## 4.1 Security Review (Automated)
**Antigravity orchestrates security-reviewer agent:**

**Scan for:**
- ❌ Hardcoded secrets (API keys, tokens, passwords)
- ❌ SQL injection vulnerabilities (if using DB)
- ❌ XSS vulnerabilities (if web-facing)
- ❌ Unvalidated user input
- ❌ Insecure file permissions
- ❌ Logging sensitive data
- ❌ Unsafe cryptography
- ❌ OWASP Top 10 violations

**Run tools:**
```bash
bandit -r src/  # Python security scanner
mypy --strict src/  # Type checking (catches errors)
```

**Report:**
```
SECURITY SCAN RESULTS:
✅ No hardcoded secrets found
✅ No SQL injection risks
✅ No XSS vulnerabilities
✅ File permissions correct (0o600)
✅ Logging sanitized (no credentials)
✅ Input validation present
✅ Type hints 100% coverage
Status: ✅ PASSED - Safe to merge
```

**If ANY security issue found, FAIL and fix before proceeding.**

## 4.2 Input Validation
**All inputs must be validated:**
```python
# Example: Validate order parameters
def place_order(self, symbol: str, qty: int, order_type: str) -> Order:
    # Validate symbol
    if symbol not in self.valid_symbols:
        raise ValueError(f"Invalid symbol: {symbol}")
    
    # Validate quantity (must be > 0, multiple of lot size)
    if qty <= 0 or qty % self.lot_size != 0:
        raise ValueError(f"Invalid qty: {qty}")
    
    # Validate order type
    if order_type not in ["LIMIT", "MARKET"]:
        raise ValueError(f"Invalid order_type: {order_type}")
    
    # All valid - proceed
    return self.broker.place_order(symbol, qty, order_type)
```

## 4.3 Secrets Protection Checklist
**NEVER:**
- ❌ Commit credentials.json with real tokens
- ❌ Log API responses that contain tokens
- ❌ Store OTP on filesystem without 0o600 permissions
- ❌ Hardcode API keys in code
- ❌ Write tokens to log files

**ALWAYS:**
- ✅ Use environment variables for secrets
- ✅ Protect files with 0o600 permissions
- ✅ Sanitize logs (only log safe fields)
- ✅ Use .env.example template
- ✅ Add secrets to .gitignore
- ✅ Rotate tokens if ever exposed

---

# 📝 PHASE 5: CODE REVIEW GATE

## 5.1 Mandatory Code Review
**Antigravity orchestrates code-reviewer agent:**

**Reviewer must check:**

| Category | Checklist |
|----------|-----------|
| **Correctness** | ✅ Logic correct? ✅ Edge cases handled? ✅ Off-by-one errors? |
| **Safety** | ✅ Thread-safe? ✅ Race conditions? ✅ Resource leaks? |
| **Security** | ✅ No secrets logged? ✅ Input validated? ✅ Permissions correct? |
| **Quality** | ✅ Functions < 50 lines? ✅ Variables well-named? ✅ Imports clean? |
| **Tests** | ✅ Tests cover happy path? ✅ Edge cases tested? ✅ Coverage 80%+? |
| **Documentation** | ✅ Function docstrings? ✅ Complex logic explained? ✅ Config documented? |
| **Alignment** | ✅ Follows 4 principles? ✅ Matches project patterns? ✅ Aligns with vision? |

## 5.2 Issue Severity Tiers

| Tier | Action | Example |
|------|--------|---------|
| 🔴 **CRITICAL** | Block merge | Race condition, data corruption, secret leak |
| 🟠 **HIGH** | Must fix before merge | Missing test, no error handling, unsafe cast |
| 🟡 **MEDIUM** | Fix if quick, document if complex | Code style, naming, minor inefficiency |
| 🟢 **LOW** | Nice-to-have | Comment typo, refactoring suggestion |

**Decision Rule:**
- 🔴 CRITICAL issues: **BLOCK merge**, must fix
- 🟠 HIGH issues: **MUST fix**, no exceptions
- 🟡 MEDIUM issues: **Fix if < 30 min**, document trade-off if complex
- 🟢 LOW issues: **Nice-to-have**, don't block

## 5.3 Code Review Output
**Reviewer provides:**
```
CODE REVIEW COMPLETE
Reviewer: [Agent Name]
Files: [main.py, order_manager.py]

CRITICAL ISSUES: 0 ✅
HIGH ISSUES: 1 (FIXABLE)
  - Missing error handling in retry logic

MEDIUM ISSUES: 2 (OPTIONAL)
  - Variable name could be clearer
  - Consider extracting helper function

Recommendation: FIX 1 HIGH issue, then ready to merge ✅
```

**If issues exist, Antigravity fixes them and re-requests review.**

---

# 📚 PHASE 6: DOCUMENTATION & ALIGNMENT

## 6.1 Documentation: Update Existing, Rarely Create New

**AMENDMENT: No Documentation Bloat**

✅ **RULE: UPDATE existing docs. RARELY create new docs.**

### Before Creating Any New Documentation, Check:
```
1. Does this info already exist elsewhere? 
   → YES: Update that doc instead, don't create duplicate
   → NO: Proceed to next check

2. Is this documentation essential for operations?
   → NO: Don't document it
   → YES: Proceed to next check

3. Can this fit in existing docs (BUG_REGISTRY, FIX_LOG)?
   → YES: Add there instead, don't create new file
   → NO: New doc approved (rare)

4. If creating new doc, what's the archival plan?
   → Docs must be archived when no longer relevant
   → Don't let old docs accumulate
```

**Result**: Only essential, non-redundant docs. Clean, maintainable documentation.

### Documentation to Update (Only These)

| Document | When to Update | What |
|----------|---|---|
| **BUG_REGISTRY.md** | Every bug fix | Mark FIXED with date, commit SHA, tests added |
| **FIX_LOG.md** | Every work item | Entry: date, what, why, tests, commit, time |
| **VISION_AND_GOALS.md** | Only if scope changed | Update goals section (rarely) |
| **PRINCIPLES_CHECKLIST.md** | Only if principles changed | Verify all 4 principles followed (review, don't update) |
| **README.md** | Only if behavior changed | Update feature list (rarely) |
| **Architecture docs** | Only if components changed | Update diagrams (rarely) |
| **Runbooks** | Only if failure mode changed | Update procedures (rarely) |

**DO NOT CREATE:**
- ❌ New docs for every bug fix (use BUG_REGISTRY + FIX_LOG)
- ❌ Duplicate documentation (consolidate into existing docs)
- ❌ Detailed change logs (FIX_LOG is sufficient)
- ❌ Per-bug documentation files
- ❌ Temporary docs that won't be maintained

### Documentation Bloat Prevention Checklist

**Before creating ANY new documentation, Antigravity must verify:**

```
🚫 BLOAT CHECK: Is this new documentation really necessary?

❌ DON'T create if:
  - This info already exists in BUG_REGISTRY.md
  - This info already exists in FIX_LOG.md
  - This info already exists in architecture docs
  - This is a one-off, temporary note
  - This duplicates existing documentation
  - This is "nice to have" but not essential

✅ OK to create only if:
  - Info doesn't fit in existing docs
  - It's essential for operations
  - It will be maintained going forward
  - There's a clear archival plan
  - It's referenced from multiple places
```

**If bloat check FAILS → Don't create new doc, update existing instead.**

### Archival Strategy: Keep Docs Fresh

**Documentation Lifecycle:**

```
ACTIVE (Current, maintained)
  ↓ Document becomes outdated/irrelevant
ARCHIVE (Move to archive/ folder)
  ↓ After 6 months in archive
DELETE (Remove permanently)
```

**When to Archive:**
- Document describes a bug that's been fixed for 3+ months
- Document describes a feature that's been removed
- Document is superseded by newer documentation
- Document is no longer referenced anywhere

**How to Archive:**
1. Move old doc to `docs/archive/` folder
2. Update all references to point to new location
3. Add note at top: "ARCHIVED: [reason]. [date]"
4. Keep 1 reference in main docs pointing to archive

**Example:**
```
docs/
├── VISION_AND_GOALS.md (current)
├── BUG_REGISTRY.md (current)
└── archive/
    ├── OLD_ARCHITECTURE.md (archived 2026-09-01)
    └── DEPRECATED_FEATURES.md (archived 2026-08-15)
```

**Benefit**: Main documentation stays clean, relevant, and maintainable.

**Example BUG_REGISTRY entry:**
```markdown
### BUG-001: Order Rejection Orphans Position ⭐ HIGHEST RISK
**Status**: ✅ FIXED (2026-06-25)
**Commit**: abc123def456
**Effort**: 3 hours
**Tests Added**: 5 (test_order_rejection_keeps_position, test_retry_backoff, etc.)
**Coverage Before**: 0% | **After**: 92%
**Changes**:
- Modified: src/order_manager.py (lines 234-260)
- Modified: src/fno_trading_bot.py (lines 638-700)
- Added: tests/test_order_rejection.py
**Verification**:
- ✅ All 5 new tests passing
- ✅ All 25 critical tests still passing
- ✅ Preflight checks: 25/25 ✅
```

## 6.2 Keep Project Vision Aligned
**For every change, verify:**
- ✅ Does this move us toward "production-ready system"?
- ✅ Does this reduce capital loss risk?
- ✅ Does this improve reliability/testability?
- ✅ Does this prevent future bugs?

**If answer is NO to any, Antigravity should ask Arun:**
```
⚠️ ALIGNMENT CHECK FAILED
This change: [description]
Project goal: [vision point]
Impact: [misaligned because...]
Proceed anyway? (Yes/No)
```

## 6.3 Update FIX_LOG.md
**Entry template:**
```markdown
## 2026-06-25 - BUG-001: Order Rejection

**What**: Fixed position being deleted when order rejected by broker

**Root Cause**: Code called `bot.exit_trade()` regardless of order.status

**Fix**:
- Check order.status == OrderStatus.PLACED before exiting
- Added retry logic with exponential backoff
- Added operator alert after 3 failures

**Tests Added**: 5
- test_order_rejection_keeps_position
- test_order_rejection_retry_backoff
- test_order_rejection_operator_alert
- test_order_rejection_max_retries
- test_concurrent_order_rejection

**Commit**: abc123def456
**Time**: 3 hours
**Status**: ✅ MERGED
```

---

# ✅ PHASE 7: REGRESSION & PREFLIGHT VERIFICATION

## 7.1 Run Full Test Suite
**ALL tests must pass:**
```
Running test suite...

Unit Tests: 85/85 ✅
Integration Tests: 45/45 ✅
E2E Tests: 20/20 ✅
Regression Tests: 25/25 ✅

Total: 175/175 ✅
Coverage: 88% ✅ (Target: 80%+)

Status: ✅ ALL TESTS PASSING
```

**If ANY test fails, STOP and debug.**

## 7.2 Automated Preflight Checks (25 points)
**Run: `./verify_preflight.sh`**

```
PREFLIGHT CHECKLIST (25 POINTS)
✅ Git initialized with .gitignore
✅ No credentials.json in git history
✅ credentials.json has 0o600 permissions
✅ No API keys in code
✅ No secrets in logs
✅ Type hints 100% coverage (mypy passes)
✅ Security scan passes (bandit)
✅ All tests passing (175/175)
✅ Code coverage 80%+ (88%)
✅ No bare exception clauses
✅ All imports used
✅ No undefined variables
✅ All functions documented
✅ Functions < 50 lines
✅ Files < 800 lines
✅ No hardcoded values (except constants)
✅ Daily loss limit enforced
✅ Order rejection retry logic works
✅ Position reconciliation passes
✅ SymbolMaster optimized (singleton)
✅ Error handling comprehensive
✅ Telegram alerts configured
✅ Backup created (3+ locations)
✅ BUG_REGISTRY.md updated
✅ FIX_LOG.md updated
✅ Vision alignment verified

RESULT: 25/25 ✅ ALL CHECKS PASSED
Status: READY TO DEPLOY
```

**If ANY check fails, STOP and fix before proceeding.**

## 7.3 Manual Regression Testing
**For CRITICAL bugs, test manually:**
```
REGRESSION TEST CHECKLIST:
✅ Bot starts without errors
✅ Can connect to broker (paper mode)
✅ Can place test order (paper mode)
✅ Order fills detected correctly
✅ Position reconciliation works
✅ Daily loss limit blocks entry when hit
✅ Order rejection triggers retry
✅ Telegram alerts fire correctly
✅ State persists after restart
✅ No memory leaks (run for 1 hour)
```

**If ANY manual test fails, DEBUG and fix.**

---

# 🚀 PHASE 8: DEPLOYMENT & MONITORING

## 8.1 Pre-Deployment Checklist
**Before deploying to live:**

```
PRE-DEPLOYMENT CHECKLIST:
✅ All automated tests passing (175/175)
✅ Code review approved
✅ Security scan passed
✅ Preflight checks 25/25
✅ Regression tests passed
✅ Documentation updated
✅ BUG_REGISTRY updated
✅ Backup created (3+ locations)
✅ Rollback procedure documented
✅ Operator trained on change
✅ Telegram alerts configured
✅ Paper mode tested
✅ Vision alignment verified
✅ No new CRITICAL/HIGH issues

STATUS: ✅ READY TO DEPLOY
```

## 8.2 Deployment Steps
**Deploy carefully (1 change at a time):**

```
DEPLOYMENT:
1. Backup current code (git tag as backup-[date])
2. Pull latest changes
3. Run ./verify_preflight.sh (must be 25/25)
4. Start bot in PAPER MODE first
5. Monitor for 30 minutes (no errors?)
6. Check Telegram alerts (firing correctly?)
7. Verify position reconciliation (running?)
8. Check order fills (detecting correctly?)
9. If all OK → switch to LIVE MODE
10. Monitor first 30 minutes intensely
11. Document deployment in FIX_LOG.md
```

## 8.3 Post-Deployment Monitoring
**Monitor for issues:**

```
MONITORING CHECKLIST (Hour 1):
✅ No exceptions in logs
✅ Telegram alerts firing
✅ Orders filling correctly
✅ P&L calculating correctly
✅ Daily loss limit enforced
✅ Position reconciliation running
✅ CPU usage < 20%
✅ Memory usage stable
✅ No hanging threads

If ANY issue detected → ROLLBACK immediately
```

---

# 🔄 PHASE 9: CONTINUOUS IMPROVEMENT

## 9.1 Weekly Review Cycle
**Every Sunday (or weekly):**

```
WEEKLY REVIEW:
1. Check BUG_REGISTRY.md (any new issues?)
2. Review FIX_LOG.md (what was fixed?)
3. Check test coverage (still 80%+?)
4. Review Telegram alerts (any patterns?)
5. Check trades (win rate holding at 73%?)
6. Update VISION_AND_GOALS.md (progress?)
7. Plan next week's fixes
```

## 9.2 Monthly Deep Dive
**First of each month:**

```
MONTHLY DEEP DIVE:
1. Code quality audit (mypy, bandit, coverage)
2. Performance profiling (any slowdowns?)
3. Risk audit (daily loss limit working?)
4. Security audit (any new vulnerabilities?)
5. Documentation review (all current?)
6. Architecture review (anything need refactoring?)
7. Roadmap check (on track for 4-week transformation?)
```

---

# 🎯 QUICK REFERENCE - ALL PHASES AT A GLANCE

```
PHASE 1: INTAKE & VISION ALIGNMENT
├─ Validate against VISION_AND_GOALS.md
├─ Categorize severity (CRITICAL/HIGH/MEDIUM/LOW)
└─ Estimate scope & risk

PHASE 2: PLANNING & ARCHITECTURE
├─ Use architect agent
├─ Define success criteria
└─ Check against 4 principles

PHASE 3: TEST-FIRST DEVELOPMENT (TDD)
├─ Write tests FIRST (RED)
├─ Implement fix (GREEN)
├─ Refactor (IMPROVE)
└─ Achieve 80%+ coverage

PHASE 4: SECURITY & VALIDATION
├─ Security scan (bandit, mypy)
├─ Input validation
└─ Secrets protection checklist

PHASE 5: CODE REVIEW GATE
├─ Mandatory code review
├─ Fix CRITICAL/HIGH issues
└─ Approve before merge

PHASE 6: DOCUMENTATION & ALIGNMENT
├─ Update BUG_REGISTRY.md
├─ Update FIX_LOG.md
├─ Verify vision alignment
└─ Update architecture docs

PHASE 7: REGRESSION & PREFLIGHT
├─ Run full test suite (all pass?)
├─ Preflight checklist (25/25?)
└─ Manual regression tests

PHASE 8: DEPLOYMENT & MONITORING
├─ Pre-deployment checklist
├─ Deploy carefully
└─ Monitor hour 1 intensely

PHASE 9: CONTINUOUS IMPROVEMENT
├─ Weekly review cycle
└─ Monthly deep dive
```

---

# 📊 SUCCESS METRICS

**For EVERY piece of work, measure:**

| Metric | Target | How to Check |
|--------|--------|---|
| **Test Coverage** | 80%+ | `pytest --cov=src/` |
| **Type Safety** | 100% | `mypy --strict src/` |
| **Security** | 0 issues | `bandit -r src/` |
| **Code Quality** | No CRITICAL/HIGH issues | Code review |
| **Regression** | 0 new failures | Test suite |
| **Documentation** | 100% updated | Manual check |
| **Performance** | No degradation | Profiling |
| **Alignment** | ✅ with vision | Vision check |

---

# ⚠️ WHAT HAPPENS IF SOMETHING GOES WRONG

## If Tests Fail
```
STOP. Do not merge.
1. Analyze test failure
2. Fix implementation or test
3. Re-run tests
4. Re-request code review
5. Only merge when all tests pass
```

## If Security Scan Fails
```
STOP. Do not merge.
1. Fix security issue
2. Re-run bandit
3. Get security reviewer approval
4. Only merge when scan passes
```

## If Code Review Finds CRITICAL Issues
```
STOP. Do not merge.
1. Fix all CRITICAL issues
2. Request re-review
3. Only merge when approved
```

## If Preflight Checks Fail
```
STOP. Do not deploy.
1. Run verify_preflight.sh
2. Fix failing checks one by one
3. Re-run until 25/25 pass
4. Only deploy when ready
```

## If Something Breaks in Production
```
IMMEDIATE ACTIONS:
1. STOP bot (halt new trades)
2. Analyze what broke
3. Pull from backup branch
4. Redeploy previous version
5. Post-mortem: what went wrong?
6. Add test to prevent recurrence
7. Once fixed, redeploy new version
```

---

# 📞 WHEN TO USE WHICH AGENT

**Antigravity automatically selects right agent:**

| Task | Agent(s) | Purpose |
|------|----------|---------|
| **Plan approach** | planner | Break down work into steps |
| **Design system** | architect | Architectural decisions |
| **Write tests first** | tdd-guide | TDD workflow |
| **Review code** | code-reviewer | Quality assurance |
| **Security check** | security-reviewer | Vulnerability scanning |
| **Fix build** | build-error-resolver | Compilation errors |
| **Fix type errors** | code-reviewer + mypy | Type safety |
| **Optimize performance** | architect + profiler | Speed improvements |

---

# 🎓 TRAINING FOR ARUN

**Arun should understand:**

1. ✅ **4 Principles**: Test-First, One Commit, Code Review, Security First
2. ✅ **TDD Workflow**: RED → GREEN → IMPROVE
3. ✅ **Code Review Process**: CRITICAL/HIGH/MEDIUM/LOW tiers
4. ✅ **Preflight Checks**: Must pass 25/25 before deploy
5. ✅ **Git Workflow**: One clear commit per bug, detailed messages
6. ✅ **When to Rollback**: If anything breaks, go back to backup
7. ✅ **Vision Alignment**: Every change must support project goals

---

# ✅ FINAL CHECKLIST - READY TO DEPLOY?

**Before Arun uses this with Antigravity, verify:**

- [ ] Arun has read ANTIGRAVITY_STANDARD_WORKFLOW.md
- [ ] Arun understands 9 phases
- [ ] Arun knows to reference this file in every request
- [ ] Arun has BACKUP_AND_RECOVERY_PLAN.md if rollback needed
- [ ] Arun has BUG_REGISTRY.md for tracking
- [ ] Arun has FIX_LOG.md for documenting
- [ ] Arun has PRINCIPLES_CHECKLIST.md as daily reference
- [ ] Arun understands: **No work skips any phase**
- [ ] Arun understands: **No work deploys without 25/25 preflight**
- [ ] Arun understands: **Tests are mandatory, not optional**

**When all above ✅, Arun is ready to use Antigravity with confidence.**

---

# 🚀 EXAMPLE USAGE

## Example 1: Bug Fix
```
@Antigravity: FIX BUG-001: Order rejection orphans position
Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md

This is CRITICAL severity (capital loss risk).
Follow all 9 phases.
Target: Complete in < 3 hours with 5+ tests.
```

**Antigravity delivers:**
```
✅ PLAN: Analyzed code, identified fix location
✅ TEST: Wrote 5 failing tests (RED phase)
✅ CODE: Implemented fix (GREEN phase)
✅ REFACTOR: Cleaned up retry logic (IMPROVE phase)
✅ SECURITY: Scan passed, no secrets logged
✅ REVIEW: Code review approved
✅ DOCS: Updated BUG_REGISTRY.md, FIX_LOG.md
✅ REGRESSION: All 175 tests passing
✅ PREFLIGHT: 25/25 checks passed
✅ READY: Approved for deployment

Status: ✅ READY TO DEPLOY
Commit: abc123def456
Time: 2.5 hours
```

## Example 2: Enhancement
```
@Antigravity: FEATURE: Add position reconciliation
Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md

This is HIGH severity (improves reliability).
Follow all 9 phases.
Should improve detection of orphaned positions.
Must not break existing functionality.
```

**Antigravity delivers:**
```
✅ PLAN: Designed bidirectional reconciliation
✅ TEST: Wrote 8 tests for reconciliation
✅ CODE: Implemented reconciliation loop
✅ REFACTOR: Optimized database queries
✅ SECURITY: No performance regression, no data leaks
✅ REVIEW: Code review approved
✅ DOCS: Updated architecture, runbooks
✅ REGRESSION: All 180 tests passing (5 new)
✅ PREFLIGHT: 25/25 checks passed
✅ ALIGNED: Supports "production-ready system" goal

Status: ✅ READY TO DEPLOY
Commit: def456abc123
Time: 5 hours
Coverage: 87%
```

## Example 3: Out-of-Box Thinking
```
@Antigravity: THINK: How can we reduce order rejection rate?
Reference: ANTIGRAVITY_STANDARD_WORKFLOW.md

Current issues: 15% of orders rejected by broker.
Current approach: Retry logic.
Ask: Are there preventive measures?
```

**Antigravity delivers:**
```
📊 ANALYSIS:

Current State:
- 15% orders rejected
- Mostly due to: insufficient margin (40%), liquidity (35%), session expired (25%)

Preventive Measures:
1. Pre-order validation: Check margin BEFORE sending order
   → Would prevent 40% of rejections
   → Test: test_margin_check_prevents_rejection

2. Liquidity check: Verify spread < threshold before order
   → Would prevent 35% of rejections
   → Test: test_liquidity_check_prevents_rejection

3. Session refresh: Refresh session token every 30 min
   → Would prevent 25% of rejections
   → Test: test_session_refresh_prevents_expiry

Recommendation: Implement all 3 (total 6-8 hours, HIGH impact)

Follow ANTIGRAVITY_STANDARD_WORKFLOW.md for implementation?
```

---

# 🎯 FINAL INSTRUCTION TO ARUN

**Use this document for EVERY request to Antigravity:**

```
Dear Antigravity,

Please [TASK: describe what you want done]

Use ANTIGRAVITY_STANDARD_WORKFLOW.md and follow all 9 phases:
1. Intake & Vision Alignment
2. Planning & Architecture
3. Test-First Development
4. Security & Validation
5. Code Review Gate
6. Documentation & Alignment
7. Regression & Preflight Verification
8. Deployment & Monitoring
9. Continuous Improvement

Deliver:
✅ Working code with 80%+ test coverage
✅ All tests passing
✅ Security scan passed
✅ Code review approved
✅ Preflight 25/25 checks passed
✅ Documentation updated
✅ Ready to deploy or flagged with blockers

Thank you,
Arun
```

---

**This is your standing instruction for all future development work.**

**No phase is skipped. No work deploys without 25/25 preflight checks. Tests are mandatory. Code review is mandatory. Vision alignment is mandatory.**

**With this framework, your bot transforms from "risky prototype" to "production-ready system."**

🚀 **Let's build something great!**
