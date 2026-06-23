# Backup & Recovery Plan

**Objective**: Full safety net before any changes. Ability to rollback at any point.

---

## Step 1: Create Full Backup (Do This First)

### 1.1 Backup Strategy

```bash
# Create backup directory with timestamp
BACKUP_DIR="backups/pre-fixes_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup entire project
cp -r . "$BACKUP_DIR/"

# Backup current state in multiple locations
zip -r "${BACKUP_DIR}.zip" .  # Local zip
tar -czf "${BACKUP_DIR}.tar.gz" .  # Compressed tar

echo "✅ Backup created at: $BACKUP_DIR"
echo "✅ Zip backup: ${BACKUP_DIR}.zip"
echo "✅ Tar backup: ${BACKUP_DIR}.tar.gz"
```

### 1.2 What Gets Backed Up

```
Pre-fix backup includes:
✅ All source code (src/)
✅ All tests (tests/)
✅ Configuration templates (config.json.example, .env.example)
✅ Documentation
✅ Git history (.git folder)

❌ NOT included (local only):
- .env (credentials stay local)
- credentials.json (local token)
- logs/ (local trading logs)
- data/ (local positions)
- __pycache__/ (Python cache)
```

### 1.3 Create Multiple Backup Points

```bash
# Local backup (fast recovery)
mkdir -p backups/
cp -r . backups/pre-fixes_v1_$(date +%s)/

# USB/External Drive backup (physical safety)
cp -r . /media/external_drive/f-o-bot-backup/

# Cloud backup (disaster recovery)
# Option 1: Private GitHub repo tagged
git tag -a "backup_$(date +%Y%m%d)" -m "Full backup before critical fixes"
git push origin backup_$(date +%Y%m%d)

# Option 2: Cloud storage (Dropbox, S3, OneDrive)
aws s3 cp . s3://your-backup-bucket/f-o-bot-pre-fixes/ --recursive
```

### 1.4 Create Backup Manifest

```bash
# backups/MANIFEST.md
# Backup Manifest

## Backup: pre-fixes_20260623_141500

**Date**: 2026-06-23 14:15:00  
**Reason**: Pre-critical-fixes backup  
**Size**: 450 MB  
**Files**: 1,247  

### Contents
- src/ (12 modules, 4,500 lines)
- tests/ (0 existing tests)
- config.json.example
- .env.example
- All documentation

### Git Info
- Branch: main
- Commit: abc123def456...
- Commits since last backup: 3

### How to Restore
```bash
# Full restore
cp -r backups/pre-fixes_20260623_141500/* .

# Restore one file
cp backups/pre-fixes_20260623_141500/src/main.py src/main.py

# Restore to previous commit (via git)
git checkout abc123def456~3
```

### Verification
- [x] All files present (1,247)
- [x] No corrupted files
- [x] Git history intact
- [x] Secrets properly excluded
```

---

## Step 2: Initialize Git (If Not Already Done)

### 2.1 Check Current Status

```bash
# Check if git is already initialized
git status

# If not initialized:
git init
git config user.name "Your Brother's Name"
git config user.email "brother@example.com"
```

### 2.2 Create .gitignore (Protect Secrets)

```bash
cat > .gitignore << 'EOF'
# Secrets (NEVER commit)
.env
.env.local
credentials.json
otp_response.txt
config.json
config.local.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
build/
dist/
*.egg-info/
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs & Data
logs/
data/
*.log
*.csv
*.xlsx
~$*

# OS
.DS_Store
Thumbs.db

# Backups (keep local, don't commit)
backups/
*.zip
*.tar.gz
EOF

git add .gitignore
git commit -m "chore: add .gitignore to protect secrets"
```

### 2.3 Create Initial Commit (If Not Already Done)

```bash
# Check if there are existing commits
git log --oneline | head

# If empty, create initial commit
git add -A
git commit -m "chore: initial commit - F&O trading bot (pre-critical-fixes)"

# Verify
git log --oneline | head -1
```

### 2.4 Create Backup Branch

```bash
# Create a backup branch that we'll never touch
git branch backup/pre-fixes
git push origin backup/pre-fixes  # If using GitHub

# This branch is FROZEN - we never commit to it
# If everything goes wrong, we can reset to this branch
```

---

## Step 3: Bug Registry Setup

### 3.1 Create BUG_REGISTRY.md

```bash
# Create central bug tracking file
cat > BUG_REGISTRY.md << 'EOF'
# Bug Registry & Tracking

**Last Updated**: 2026-06-23  
**Total Bugs**: 21  
**Critical**: 8 | High: 8 | Medium: 5  

---

## Critical Bugs (MUST FIX)

### BUG-001: Order Rejection Orphans Position
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: main.py:234, main.py:407
- **Impact**: Uncontrolled position loss
- **Root Cause**: exit_trade() called unconditionally regardless of order.status
- **Fix Strategy**: 
  - Gate exit_trade() on order.status == PLACED
  - Retry rejected orders with backoff
  - Alert operator on 3 failures
- **Estimated Effort**: 2-3 hours
- **Tests Required**:
  - test_order_rejection_keeps_position
  - test_order_rejection_retry_logic
  - test_order_rejection_operator_alert
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

### BUG-002: Race Condition in Exit Logic
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: src/fno_trading_bot.py:638-643
- **Impact**: Concurrent entry/exit on same position = duplicate orders or torn reads
- **Root Cause**: Position attributes mutated without holding bot.lock
- **Fix Strategy**:
  - Hold bot.lock for entire check-decide-place-mutate sequence
  - Add per-position "exiting" flag (atomic)
  - Test concurrent scenarios
- **Estimated Effort**: 3-4 hours
- **Tests Required**:
  - test_concurrent_entry_exit_no_double_sell
  - test_race_condition_tsl_calculation
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

### BUG-003: Daily Loss Limit Not Enforced
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: main.py (entry loop ~line 336)
- **Impact**: Bot keeps trading even after daily loss limit exceeded
- **Root Cause**: daily_pnl tracked but never checked in entry_monitoring_loop
- **Fix Strategy**:
  - Check daily_pnl before each entry
  - Block new entries if limit exceeded
  - Update config: daily_loss_limit_pct = 5 (not 100)
  - Add StateManager.is_paused() check
- **Estimated Effort**: 1-2 hours
- **Tests Required**:
  - test_daily_loss_limit_blocks_entry
  - test_daily_loss_limit_percentage_calculation
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

### BUG-004: Credentials.json Plaintext Token
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: src/market_data.py:85-95
- **Impact**: Broker access token exposed if credentials.json is stolen
- **Root Cause**: No file permissions set; no .gitignore protection
- **Fix Strategy**:
  - Add os.chmod("credentials.json", 0o600) after write
  - Add credentials.json to .gitignore
  - Create pre-commit hook to prevent accidental commits
- **Estimated Effort**: 1 hour
- **Tests Required**:
  - test_credentials_file_permissions_0o600
  - test_gitignore_blocks_credentials_json
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

### BUG-005: Session Data Logged in Full
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: src/market_data.py:214
- **Impact**: Credentials/tokens may appear in logs
- **Root Cause**: Full response dict logged instead of just message
- **Fix Strategy**:
  - Log only message field: session_data.get("message", "unknown error")
  - Never log full response objects from authenticated endpoints
  - Add logging sanitizer
- **Estimated Effort**: 30 minutes
- **Tests Required**:
  - test_session_error_logging_sanitized
  - test_no_credentials_in_logs
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

### BUG-006: Login Response Logged in Full
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: src/market_data.py:178
- **Impact**: Credentials may appear in logs
- **Root Cause**: Full response logged instead of message
- **Fix Strategy**:
  - Log only message field
  - Apply same pattern as BUG-005
- **Estimated Effort**: 15 minutes
- **Tests Required**:
  - test_login_error_logging_sanitized
- **PR**: Not yet created
- **Blocked By**: BUG-005 (same pattern)
- **Blocks**: Release to production

### BUG-007: OrderManager Constructor Mismatch
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: src/order_manager.py:47 vs main.py:497
- **Impact**: Paper mode disabled; live orders execute even in paper mode
- **Root Cause**: Constructor accepts bool but receives TradingConfig object
- **Fix Strategy**:
  - Change constructor signature: def __init__(self, config: TradingConfig)
  - Set self.live_mode = config.live_trading
  - Add type hints throughout
- **Estimated Effort**: 1-2 hours
- **Tests Required**:
  - test_order_manager_paper_mode_disabled
  - test_order_manager_live_mode_enabled
  - test_paper_mode_no_real_orders
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

### BUG-008: No .gitignore for Secrets
- **Severity**: CRITICAL
- **Status**: ❌ NOT STARTED
- **Location**: Repository root
- **Impact**: Secrets can be accidentally committed to GitHub
- **Root Cause**: No .gitignore exists
- **Fix Strategy**:
  - Create comprehensive .gitignore (see SECRETS_MANAGEMENT_GUIDE.md)
  - Create .env.example template
  - Create pre-commit hook to prevent accidental commits
- **Estimated Effort**: 1 hour
- **Tests Required**:
  - test_gitignore_protects_all_secrets
  - test_pre_commit_hook_blocks_credentials
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Release to production

---

## High Severity Bugs (SHOULD FIX)

### BUG-009: Order Fill Confirmation Missing
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: src/order_manager.py
- **Impact**: Corrupted P&L; assumes "placed" = "filled"
- **Root Cause**: place_order() doesn't poll until FILLED status
- **Fix Strategy**: Poll order book until terminal (FILLED/REJECTED/EXPIRED)
- **Estimated Effort**: 3-4 hours
- **Tests Required**:
  - test_order_fill_polling
  - test_partial_fill_detection
  - test_filled_price_reconciliation
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Accurate P&L reporting

### BUG-010: Position Reconciliation Incomplete
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: src/position_sync.py
- **Impact**: Orphaned positions not detected
- **Root Cause**: Only detects local-present/broker-absent, not bot-thinks-flat/broker-open
- **Fix Strategy**: Bidirectional reconciliation
- **Estimated Effort**: 3-4 hours
- **Tests Required**:
  - test_bidirectional_reconciliation
  - test_orphaned_position_detection
- **PR**: Not yet created
- **Blocked By**: BUG-001 (need to fix orphan creation first)
- **Blocks**: Capital protection

### BUG-011: SymbolMaster Instantiated in Hot Path
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: main.py:118, 341, 426
- **Impact**: Latency spikes every 200ms in entry loop
- **Root Cause**: New instance created every 200ms
- **Fix Strategy**: Instantiate once at startup, use singleton
- **Estimated Effort**: 1-2 hours
- **Tests Required**:
  - test_symbol_master_singleton
  - test_hot_path_latency
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Performance

### BUG-012: Bare Exception Silencing Errors
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: main.py:264
- **Impact**: Errors swallowed silently; debugging impossible
- **Root Cause**: except: pass catches everything
- **Fix Strategy**: Replace with except Exception as e: logger.debug(...)
- **Estimated Effort**: 30 minutes
- **Tests Required**:
  - test_heartbeat_error_logging
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Operational visibility

### BUG-013: Hardcoded IV Value of 15.0
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: main.py:153
- **Impact**: Risk parameters not calibrated to actual volatility
- **Root Cause**: IV hardcoded instead of calculated
- **Fix Strategy**: Calculate actual IV or remove and adjust callers
- **Estimated Effort**: 2-3 hours
- **Tests Required**:
  - test_iv_calculation_accuracy
  - test_vix_adjustment_to_stop_loss
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Risk calibration

### BUG-014: Config.json Committed with Live Settings
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: config.json (currently live_trading: true, daily_loss_limit: 100%)
- **Impact**: Wrong settings if config.json accidentally pushed
- **Root Cause**: config.json in repo instead of template only
- **Fix Strategy**: 
  - Rename to config.json.example
  - Add config.json to .gitignore
  - Brother creates local config.json with his settings
- **Estimated Effort**: 30 minutes
- **Tests Required**:
  - test_config_loading_from_local
  - test_config_example_is_template
- **PR**: Not yet created
- **Blocked By**: BUG-008 (.gitignore)
- **Blocks**: Configuration safety

### BUG-015: API Error Responses Logged Unfiltered
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: src/market_data.py:369, 374, 425, 1213, 1432
- **Impact**: Account metadata leaked in logs
- **Root Cause**: Raw response.text logged to disk
- **Fix Strategy**: Log only status_code and safe parsed fields
- **Estimated Effort**: 1-2 hours
- **Tests Required**:
  - test_api_error_logging_sanitized
  - test_no_account_data_in_logs
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Security

### BUG-016: OrderManager Type Mismatch (Related to BUG-007)
- **Severity**: HIGH
- **Status**: ❌ NOT STARTED
- **Location**: src/order_manager.py
- **Impact**: Type checking not enforced
- **Root Cause**: Missing type hints
- **Fix Strategy**: Add comprehensive type hints to all functions
- **Estimated Effort**: 2-3 hours
- **Tests Required**:
  - test_type_hints_enforced (mypy)
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Code maintainability

---

## Medium Severity Bugs (NICE TO HAVE)

### BUG-017: OTP Stored on Filesystem
- **Severity**: MEDIUM
- **Status**: ❌ NOT STARTED
- **Location**: src/otp_manager.py:54, 85
- **Impact**: OTP persists on disk if deletion fails
- **Fix Strategy**: Use os.unlink() in finally block
- **Estimated Effort**: 30 minutes
- **Tests Required**:
  - test_otp_file_deleted_after_read
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Security hardening

### BUG-018: State Persistence Not Synchronous
- **Severity**: MEDIUM
- **Status**: ❌ NOT STARTED
- **Location**: src/persistence.py
- **Impact**: Crash between exit and save loses trade
- **Fix Strategy**: Persist synchronously inside every mutation
- **Estimated Effort**: 2-3 hours
- **Tests Required**:
  - test_position_persisted_immediately
  - test_crash_recovery
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Reliability

### BUG-019: History Rewrite Corruption Risk
- **Severity**: MEDIUM
- **Status**: ❌ NOT STARTED
- **Location**: src/persistence.py
- **Impact**: Corruption risk if file grows large
- **Fix Strategy**: Use append-only or per-trade atomic writes
- **Estimated Effort**: 2-3 hours
- **Tests Required**:
  - test_history_append_only
  - test_large_history_no_corruption
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Long-term reliability

### BUG-020: Symbol Parsing Silently Degrades
- **Severity**: MEDIUM
- **Status**: ❌ NOT STARTED
- **Location**: src/position_sync.py
- **Impact**: Unquotable symbols tracked, causing silent failures
- **Fix Strategy**: Fail loudly on symbol-normalization failure
- **Estimated Effort**: 1-2 hours
- **Tests Required**:
  - test_symbol_parsing_fails_loudly
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Debugging ease

### BUG-021: No External Dead-Man's-Switch
- **Severity**: MEDIUM
- **Status**: ❌ NOT STARTED
- **Location**: Watchdog is in-process only
- **Impact**: If bot dies, nobody knows
- **Fix Strategy**: External heartbeat service (pings every 5 min; absence = SMS alert)
- **Estimated Effort**: 4-5 hours
- **Tests Required**:
  - test_external_heartbeat_endpoint
  - test_alert_on_heartbeat_miss
- **PR**: Not yet created
- **Blocked By**: None
- **Blocks**: Operational safety

---

## Status Legend

- ❌ NOT STARTED - No work begun
- 🔄 IN PROGRESS - Currently being fixed
- ✅ COMPLETE - Fixed, tested, PR approved
- ⏸️ BLOCKED - Waiting for another bug to be fixed

---

## Weekly Progress Tracking

### Week 1 Target: Fix Critical Bugs (BUG-001 to BUG-008)
- [ ] BUG-001 (Order Rejection)
- [ ] BUG-002 (Race Condition)
- [ ] BUG-003 (Daily Loss Limit)
- [ ] BUG-004 (Credentials File)
- [ ] BUG-005 (Session Logging)
- [ ] BUG-006 (Login Logging)
- [ ] BUG-007 (OrderManager)
- [ ] BUG-008 (.gitignore)

**Estimated**: 15-20 hours  
**Target Completion**: End of Week 1

### Week 2 Target: Fix High Severity (BUG-009 to BUG-016)
- [ ] BUG-009 (Order Fill)
- [ ] BUG-010 (Position Sync)
- [ ] BUG-011 (SymbolMaster)
- [ ] BUG-012 (Exception Handling)
- [ ] BUG-013 (IV Calculation)
- [ ] BUG-014 (Config Template)
- [ ] BUG-015 (API Logging)
- [ ] BUG-016 (Type Hints)

**Estimated**: 15-20 hours  
**Target Completion**: End of Week 2

### Week 3 Target: Fix Medium & Build Tests
- [ ] BUG-017 to BUG-021
- [ ] Create test suite (80%+ coverage)
- [ ] End-to-end testing

**Estimated**: 20-25 hours  
**Target Completion**: End of Week 3

### Week 4 Target: Documentation & Release
- [ ] Architecture documentation
- [ ] Runbooks
- [ ] Final testing
- [ ] Release to production

---

## How to Update This Registry

When fixing a bug:

1. Change Status from ❌ to 🔄
2. Create PR with bug number in title: `fix: BUG-001 order rejection orphans position`
3. Link PR in registry
4. After PR approval: Change to ✅
5. Document any lessons learned

**Example**:
```markdown
### BUG-001: Order Rejection Orphans Position
- **Status**: ✅ COMPLETE
- **PR**: https://github.com/brother/f-o-bot/pull/42
- **Commit**: abc123def456
- **Tests**: All passed (3/3)
- **Lessons Learned**: 
  - Need to check order.status before ANY position mutation
  - Retry logic must have max attempts (prevent infinite loop)
  - Operator alert on critical failures
```

EOF
cat > BUG_REGISTRY.md
```

---

## Step 4: Documentation Framework

### 4.1 Create FIX_LOG.md

```bash
cat > FIX_LOG.md << 'EOF'
# Fix Execution Log

**Project**: F&O Trading Bot  
**Fixes Started**: 2026-06-23  
**Status**: Pre-flight checks complete; ready to start Week 1

---

## Week 1: Critical Bugs (BUG-001 to BUG-008)

### Status: 🔄 IN PROGRESS

#### BUG-001: Order Rejection Orphans Position
**Date Started**: 2026-06-23  
**Current Status**: Design phase  
**Estimated Completion**: 2026-06-24

**Work Log**:
- 2026-06-23 10:00 - Design: Order rejection handler + retry logic
- 2026-06-23 11:00 - Create test_order_rejection_keeps_position.py
- 2026-06-23 12:00 - Implement order rejection handler
- 2026-06-23 13:00 - Tests passing 3/3
- 2026-06-23 14:00 - PR review initiated

**Blockers**: None

---

EOF
cat > FIX_LOG.md
```

### 4.2 Create PRINCIPLES_CHECKLIST.md

```bash
cat > PRINCIPLES_CHECKLIST.md << 'EOF'
# Principles Compliance Checklist

All fixes must comply with 4 core principles:
1. **Coding Style** (common/coding-style.md)
2. **Testing** (common/testing.md) - TDD, 80%+ coverage
3. **Git Workflow** (common/git-workflow.md) - conventional commits, detailed PRs
4. **Security** (common/security.md) - no secrets, validation, error handling

---

## Principle 1: Coding Style

### Immutability (CRITICAL)
- [ ] No in-place mutations of objects
- [ ] New objects created instead of modifying existing ones
- [ ] Position.status is set, not mutated
- [ ] Configuration is read-only once loaded

### File Organization
- [ ] No file > 800 lines
- [ ] High cohesion, low coupling
- [ ] Utilities extracted to separate modules

### Error Handling
- [ ] All errors handled explicitly (no silent failures)
- [ ] User-friendly messages in bot logic
- [ ] Server-side detailed error logging
- [ ] No bare except clauses

### Input Validation
- [ ] All user input validated
- [ ] Schema validation on config files
- [ ] API responses validated before use
- [ ] Fail fast on validation errors

### Code Quality Checklist
- [ ] Code is readable and well-named
- [ ] Functions are < 50 lines
- [ ] Files are focused < 800 lines
- [ ] No deep nesting (> 4 levels)
- [ ] Proper error handling
- [ ] No hardcoded values
- [ ] Immutable patterns used

---

## Principle 2: Testing (TDD)

### Test-Driven Development Workflow
For each bug fix:

1. **Write Test First (RED)** ❌
   - Test should FAIL with current code
   - Test name describes the fix: `test_order_rejection_keeps_position()`
   - Assert the desired behavior

2. **Implement Fix (GREEN)** ✅
   - Write minimal code to pass test
   - Don't over-engineer

3. **Refactor (IMPROVE)** 🔄
   - Clean up code
   - No duplication
   - All tests still pass

### Coverage Requirements
- [ ] 80%+ overall coverage
- [ ] 100% coverage on critical paths (order placement, position sync)
- [ ] Unit tests for all functions
- [ ] Integration tests for API interactions
- [ ] E2E tests for full trade lifecycle

### Test Organization
```
tests/
├── unit/
│   ├── test_indicators.py
│   ├── test_trading_config.py
│   └── test_order_manager.py
├── integration/
│   ├── test_market_data_api.py
│   ├── test_order_placement.py
│   └── test_position_sync.py
├── e2e/
│   ├── test_full_trade_lifecycle.py
│   └── test_order_rejection_recovery.py
└── conftest.py (fixtures)
```

### Mark Tests
```python
import pytest

@pytest.mark.unit
def test_calculate_rsi():
    ...

@pytest.mark.integration
def test_api_quote_fetch():
    ...

@pytest.mark.e2e
def test_full_trade_entry_to_exit():
    ...
```

### Run Tests
```bash
# All tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Only unit tests
pytest tests/unit/ -v -m unit

# With coverage threshold
pytest tests/ --cov=src --cov-fail-under=80
```

### Checklist for Each Fix
- [ ] Test written BEFORE implementation
- [ ] Test currently FAILS (RED phase)
- [ ] Implementation written (GREEN phase)
- [ ] Test PASSES
- [ ] No regressions in existing tests
- [ ] Coverage maintained or improved
- [ ] Test has clear name and docstring

---

## Principle 3: Git Workflow

### Conventional Commits
All commits follow this format:

```
<type>: <description>

<optional body>

Co-Authored-By: Claude Haiku <noreply@anthropic.com>
```

**Types**:
- `fix:` Bug fix (most of our commits)
- `test:` Add or update tests
- `refactor:` Restructure without behavior change
- `docs:` Documentation only
- `chore:` Build, CI, dependencies

**Examples**:
```
fix: BUG-001 order rejection keeps position open
fix: BUG-002 add lock to position exit logic
test: add test suite for critical paths
docs: update PRINCIPLES_CHECKLIST.md
```

### Branch Strategy
```
main (stable, tested, reviewed)
├── fixes/bug-001-order-rejection
├── fixes/bug-002-race-condition
└── fixes/bug-003-daily-loss-limit
```

### Pull Request Template

Every PR must include:

```markdown
# [BUG-001] Order Rejection Orphans Position

## Problem
When broker rejects a SELL order, bot incorrectly deletes the position.
Position stays OPEN at broker, bot thinks it's CLOSED.
Result: Unbounded loss.

## Solution
1. Gate bot.exit_trade() on order.status == PLACED
2. Retry rejected orders with backoff
3. Alert operator after 3 failures
4. Keep position in state until exit confirmed

## Testing
- [x] test_order_rejection_keeps_position PASSES
- [x] test_order_rejection_retry_logic PASSES
- [x] test_order_rejection_operator_alert PASSES
- [x] All existing tests still pass (45/45)
- [x] Coverage: 85% (+2% from baseline)

## Security
- [x] No credentials in code
- [x] No secrets in logs
- [x] Input validation: Order objects validated
- [x] Error messages don't leak data

## Files Changed
- src/order_manager.py (+45 lines)
- src/notifications.py (+15 lines)
- tests/unit/test_order_manager.py (+150 lines)

## Checklist
- [x] Tests written BEFORE implementation
- [x] All tests PASS
- [x] Code follows coding style rules
- [x] No bare except clauses
- [x] Error messages are clear
- [x] Immutable patterns used
- [x] No hardcoded values (use config)
- [x] Documentation updated if needed
```

### Commit Process

```bash
# 1. Create feature branch
git checkout -b fixes/bug-001-order-rejection

# 2. Write test (RED)
# tests/unit/test_order_manager.py
# Test should FAIL with current code

# 3. Implement fix (GREEN)
# src/order_manager.py
# Code to pass the test

# 4. Verify tests pass
pytest tests/unit/test_order_manager.py -v

# 5. Verify no regressions
pytest tests/ -v

# 6. Stage changes
git add src/order_manager.py tests/unit/test_order_manager.py

# 7. Commit with conventional format
git commit -m "fix: BUG-001 order rejection keeps position open

Added retry logic with backoff. After 3 failures, alerts operator.
Position state preserved until FILLED confirmation.

Tests:
- test_order_rejection_keeps_position
- test_order_rejection_retry_logic
- test_order_rejection_operator_alert

All passing (3/3)."

# 8. Create PR on GitHub
git push origin fixes/bug-001-order-rejection
# Open PR on GitHub with template
```

### Checklist for Each Commit
- [ ] Follows conventional commit format
- [ ] Commit message describes WHY, not WHAT
- [ ] Tests included in same commit
- [ ] All tests pass
- [ ] No merge commits (rebase instead)
- [ ] One logical change per commit

---

## Principle 4: Security

### Mandatory Before Commit
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated
- [ ] SQL injection prevention (if using SQL)
- [ ] XSS prevention (if web frontend)
- [ ] CSRF protection (if web)
- [ ] Authentication/authorization verified
- [ ] Rate limiting on endpoints
- [ ] Error messages don't leak sensitive data
- [ ] No credentials in logs

### Secrets Management
- [ ] .env file is in .gitignore
- [ ] .env.example has only placeholders
- [ ] credentials.json protected with 0o600 permissions
- [ ] config.json in .gitignore (local only)
- [ ] No secrets in commit messages

### Logging Safety
- [ ] No API response bodies logged (only status_code)
- [ ] No credentials in logs
- [ ] No account metadata in logs
- [ ] Error messages safe for external viewing
- [ ] Logs deleted/archived regularly

### Input Validation
- [ ] Order objects validated on creation
- [ ] Position data validated on load
- [ ] API responses validated before use
- [ ] Configuration validated at startup

### Error Handling
- [ ] All exceptions caught explicitly
- [ ] No bare except clauses
- [ ] Errors logged with context
- [ ] User receives clear error message
- [ ] Operator receives detailed error for debugging

### Security Scanning
```bash
# Check for hardcoded secrets
grep -r "API_KEY\|PASSWORD\|SECRET" src/ | grep -v "os.environ"

# Check for SQL injection vulnerabilities (if applicable)
# Check for common security issues
bandit -r src/
```

### Checklist for Each Fix
- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] Error messages safe
- [ ] No credentials in logs
- [ ] .gitignore protects secrets
- [ ] bandit scan passes

---

## Integration: How It All Works Together

When fixing BUG-001:

1. **Security** ✅
   - Don't commit credentials
   - Validate order.status input
   - Log safely (no order details)

2. **Testing (TDD)** ✅
   - Write test_order_rejection_keeps_position first (fails)
   - Implement fix (passes)
   - Test proves the fix works

3. **Coding Style** ✅
   - No mutations of position object
   - Function < 50 lines
   - Clear error handling
   - No hardcoded retry count (use config)

4. **Git Workflow** ✅
   - Branch: fixes/bug-001-order-rejection
   - Commit: "fix: BUG-001 order rejection keeps position open"
   - PR: Explains problem, solution, testing
   - Review: Senior dev checks all above

---

## How to Use This Checklist

For each bug fix, check all 4 principles:

```bash
# Before starting fix
./check_principles.sh bug-001

# This verifies:
✅ Git setup (on correct branch)
✅ Security rules (no secrets exposed)
✅ Testing structure (test files exist)
✅ Coding style (linting checks)

# Work on fix
# ... write tests, implement, test ...

# Before committing
./verify_principles.sh

# This verifies:
✅ Tests pass (pytest)
✅ Code style (black, ruff)
✅ Type checking (mypy)
✅ Security scan (bandit)
✅ No regressions
✅ Coverage threshold (80%+)

# Then commit
git commit -m "fix: ..."

# Then create PR (uses template)
gh pr create --title "fix: BUG-001 ..."
```

EOF
cat > PRINCIPLES_CHECKLIST.md
```

---

## Summary: Pre-Fix Infrastructure

✅ **Backup**: Full backup created with recovery path  
✅ **Git**: Initialized with .gitignore protection  
✅ **Bug Registry**: Central tracking (BUG-001 to BUG-021)  
✅ **Documentation**: Fix log + principles checklist  
✅ **Principles**: Aligned to coding style, testing, git, security  

**Next**: We're ready to start Week 1 fixes following this framework.

---

## Quick Reference: Pre-Flight Checklist

Before touching any code:

- [ ] Backup created (`backups/pre-fixes_...`)
- [ ] Backup verified (restores correctly)
- [ ] Git initialized (`git status` works)
- [ ] .gitignore created (protects secrets)
- [ ] BUG_REGISTRY.md in repo
- [ ] FIX_LOG.md in repo
- [ ] PRINCIPLES_CHECKLIST.md in repo
- [ ] Brother aware of 4-week plan
- [ ] Everyone agrees on timeline

**When all above are ✅, we start Week 1 fixes.**
