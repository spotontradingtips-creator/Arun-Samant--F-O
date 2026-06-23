# 🚀 COMPREHENSIVE BUG FIX EXECUTION PLAN
**Status**: ACTIVE | **Date**: 2026-06-23 | **Confidence**: 101%

---

## 📊 EXECUTIVE SUMMARY

**Total Bugs to Fix**: 21 (8 CRITICAL + 8 HIGH + 5 MEDIUM)  
**Estimated Timeline**: 4 weeks (systematic, TDD-based)  
**Methodology**: Antigravity Standard Workflow (9-phase approach)  
**Target**: Transform bot from "risky prototype" → "production-ready system"

---

## ⚠️ CRITICAL BUGS (1-8) — MUST FIX FIRST

### Bug #1: Order Rejection → Orphaned Positions ⚡ HIGHEST RISK
**Files**: `main.py:234`, `main.py:407`  
**Problem**: Exit order placed, then `bot.exit_trade()` called unconditionally. If broker REJECTS order (margin, session expired), position deleted from bot memory but still OPEN at broker.  
**Impact**: Unbounded losses  
**Fix**: 
- [ ] Gate exit_trade() on `order.status == OrderStatus.PLACED`
- [ ] On rejection: keep position in memory, retry with backoff (exponential: 100ms→200ms→400ms)
- [ ] Add order rejection handler with logging

**Tests Required**:
- [ ] Test order rejection doesn't exit position
- [ ] Test retry logic with exponential backoff
- [ ] Test position remains in bot memory after rejection

---

### Bug #2: Race Condition in Entry/Exit Thread
**Files**: `src/fno_trading_bot.py:638-643`  
**Problem**: Exit thread mutates `position.max_pnl_reached`, `position.dynamic_trailing_sl` without holding `bot.lock`. Concurrent entry thread reads same position. No per-Position thread safety.  
**Impact**: Torn reads on TSL calculation → premature/missed stop-loss exits  
**Fix**:
- [ ] Hold `bot.lock` for entire check-and-place-and-mutate sequence
- [ ] OR add per-position locks (RLock)
- [ ] Test concurrent access

**Tests Required**:
- [ ] Thread safety test (concurrent entry + exit on same symbol)
- [ ] No data corruption under concurrent access
- [ ] Lock release verified (no deadlock)

---

### Bug #3: Duplicate Entry Orders Possible
**Files**: `main.py:415-431`  
**Problem**: Entry monitoring runs every 200ms. If order propagation delayed, loop may iterate again before position synced, placing duplicate order on same symbol.  
**Impact**: Double-buying same option (2x capital loss)  
**Fix**:
- [ ] Set per-symbol `order_pending` flag before placing order
- [ ] Clear on completion (success or failure)
- [ ] Skip symbol while flag is set

**Tests Required**:
- [ ] Test duplicate orders blocked
- [ ] Test flag cleared after order completion
- [ ] Test symbol skipped while pending

---

### Bug #4: Credentials.json Plaintext Token Leak 🔐
**Files**: `src/market_data.py:85-95`  
**Problem**: Broker access token saved to `credentials.json` with world-readable permissions. No `.gitignore` entry.  
**Impact**: Token theft → unauthorized broker access  
**Fix**:
- [ ] Create `.gitignore` with `credentials.json`
- [ ] Add `os.chmod("credentials.json", 0o600)` after write
- [ ] Verify file permissions on Windows
- [ ] Consider OS credential store instead

**Tests Required**:
- [ ] Verify credentials.json in .gitignore
- [ ] Verify file permissions set to 0o600
- [ ] Test credentials not logged

---

### Bug #5: Daily Loss Limits Not Enforced
**Files**: `main.py:336-350` (entry loop)  
**Problem**: Config defines `daily_loss_limit_pct=5.0` but entry loop never checks it. `daily_pnl` tracked but not gated.  
**Impact**: On bad day, bot keeps entering until capital wiped  
**Fix**:
- [ ] At top of entry loop, check: `if daily_pnl <= -daily_loss_limit_pct% * capital: return` (block new entries)
- [ ] Log when circuit breaker activates
- [ ] Add position to preserve state

**Tests Required**:
- [ ] Test entry blocked when daily loss exceeded
- [ ] Test circuit breaker re-enabled next day
- [ ] Test logging of circuit breaker activation

---

### Bug #6: Session Data Logged in Full (Credential Leak) 🔐
**Files**: `src/market_data.py:214`  
**Problem**: On login error, full response dict logged. May contain tokens.  
**Impact**: Credential exposure via logs  
**Fix**:
- [ ] Log only `session_data.get("message", "unknown error")`, never full response

**Tests Required**:
- [ ] Test logs don't contain session tokens
- [ ] Test error message still logged

---

### Bug #7: Login Response Logged in Full (Credential Leak) 🔐
**Files**: `src/market_data.py:178`  
**Problem**: Full login API response logged on error; may contain credentials  
**Fix**:
- [ ] Log only message field

**Tests Required**:
- [ ] Test logs don't contain login response
- [ ] Test error logged safely

---

### Bug #8: OrderManager Constructor Accepts Wrong Type
**Files**: `src/order_manager.py:47` vs `main.py:497`  
**Problem**: `OrderManager(config)` called with `TradingConfig` but constructor expects `live_mode: bool`. Python accepts (truthy) → `self.live_mode` becomes config object, not boolean. `if self.live_mode:` always passes → live orders in paper mode.  
**Impact**: Paper-mode testing places real orders!  
**Fix**:
- [ ] Change constructor: `def __init__(self, config: TradingConfig): self.live_mode = config.live_trading`
- [ ] Fix caller in main.py

**Tests Required**:
- [ ] Test paper mode doesn't place live orders
- [ ] Test live mode places orders correctly
- [ ] Type checking with mypy

---

## 📊 HIGH PRIORITY BUGS (9-16)

### Bug #9: Order Fill Confirmation Missing
**Files**: `src/order_manager.py`  
**Problem**: `place_order()` returns PLACED when broker acknowledges. No poll for FILLED status. Filled_price never populated.  
**Impact**: Corrupted realized P&L  
**Fix**:
- [ ] Poll order status until terminal (FILLED / REJECTED / EXPIRED)
- [ ] Populate filled_qty and filled_price

---

### Bug #10: Position Reconciliation Incomplete
**Files**: `src/position_sync.py`  
**Problem**: Detects local-present/broker-absent but not bot-thinks-flat/broker-open. Orphans persist 5+ min unmonitored.  
**Impact**: Orphaned positions undetected  
**Fix**:
- [ ] Bidirectional reconciliation
- [ ] Cap blind-mode duration; force alert if exceeded

---

### Bug #11: SymbolMaster Instantiated in Hot Path
**Files**: `main.py:118, 341, 426`  
**Problem**: New instance created every 200ms. Expensive I/O repeated thousands of times/day.  
**Impact**: Latency spikes, potential file handle exhaustion  
**Fix**:
- [ ] Instantiate once at startup
- [ ] Pass as dependency or module singleton

---

### Bug #12: Bare Exception Silencing Errors
**Files**: `main.py:264`  
**Problem**: `except: pass` catches everything. Actual errors swallowed silently.  
**Fix**:
- [ ] `except Exception as e: logger.debug(f"Heartbeat error: {e}")`

---

### Bug #13: Hardcoded IV Value of 15.0
**Files**: `main.py:153`  
**Problem**: Hardcoded IV=15.0 unconditionally returned. Never reflects market volatility.  
**Impact**: Miscalibrated risk under high-VIX  
**Fix**:
- [ ] Calculate actual IV or adjust callers

---

### Bug #14: Config.json Committed with Live Settings
**Files**: `config.json`  
**Problem**: `live_trading=true`, `daily_loss_limit_percent=100`  
**Fix**:
- [ ] Set daily loss limit to 5-10%
- [ ] Add config.json to .gitignore

---

### Bug #15: API Error Responses Logged Unfiltered
**Files**: `src/market_data.py:369, 374, 425, 1213, 1432`  
**Problem**: Raw broker HTTP responses logged to disk  
**Fix**:
- [ ] Log only status code and safe fields, never raw response

---

### Bug #16: No .gitignore for Secrets
**Files**: Root directory  
**Problem**: `.gitignore` missing or incomplete  
**Fix**:
- [ ] Create comprehensive .gitignore

---

## 🟡 MEDIUM PRIORITY BUGS (17-21)

### Bug #17: OTP Stored on Filesystem
**Files**: `src/otp_manager.py:54, 85`  
**Problem**: OTP written to `otp_response.txt` without deletion guarantee  
**Fix**: Use `os.unlink()` in finally block

---

### Bug #18: State Persistence Not Synchronous
**Files**: `src/persistence.py`  
**Problem**: Mutations may not persist immediately  
**Fix**: Persist synchronously inside every state mutation

---

### Bug #19: History Rewrite Corruption Risk
**Files**: `src/persistence.py`  
**Problem**: `load_history()` overwrites daily_history.json wholesale  
**Fix**: Use append-only or atomic per-trade writes

---

### Bug #20: Symbol Parsing Silently Degrades
**Files**: `src/position_sync.py`  
**Problem**: Strike/expiry regex fails silently, falls back to raw broker symbols  
**Fix**: Fail loudly on symbol-normalization failure

---

### Bug #21: No External Dead-Man's-Switch
**Files**: Watchdog is in-process only  
**Problem**: If bot dies, watchdog dies too  
**Fix**: External heartbeat monitor (uptime service)

---

## 🔄 EXECUTION PHASES

### ✅ PHASE 1: PREPARATION (Today)
- [ ] Create execution plan ← **YOU ARE HERE**
- [ ] Set up test framework (pytest)
- [ ] Create bug tracking sheets
- [ ] Backup database

### 🔧 PHASE 2: FIX CRITICAL BUGS (Bugs 1-8)
- [ ] Bug #1: Order rejection handler
- [ ] Bug #2: Thread safety
- [ ] Bug #3: Duplicate order prevention
- [ ] Bug #4: .gitignore + chmod
- [ ] Bug #5: Daily loss limit enforcement
- [ ] Bug #6: Session logging sanitization
- [ ] Bug #7: Login logging sanitization
- [ ] Bug #8: OrderManager type fix

### 🔨 PHASE 3: FIX HIGH BUGS (Bugs 9-16)
- [ ] Bug #9: Order fill confirmation poll
- [ ] Bug #10: Bidirectional reconciliation
- [ ] Bug #11: SymbolMaster singleton
- [ ] Bug #12: Exception handling
- [ ] Bug #13: IV calculation
- [ ] Bug #14: config.json security
- [ ] Bug #15: API response logging
- [ ] Bug #16: .gitignore completion

### 🟡 PHASE 4: FIX MEDIUM BUGS (Bugs 17-21)
- [ ] Bug #17: OTP cleanup
- [ ] Bug #18: Sync persistence
- [ ] Bug #19: Append-only history
- [ ] Bug #20: Symbol parsing strictness
- [ ] Bug #21: External monitoring

### 🧪 PHASE 5: TEST SUITE (150+ tests, 80%+ coverage)
- [ ] Unit tests for all modules
- [ ] Integration tests for critical paths
- [ ] E2E tests for trading flow
- [ ] Thread safety tests
- [ ] Security tests

### 📚 PHASE 6: DOCUMENTATION
- [ ] Update all .md files
- [ ] Update memory files
- [ ] Update QUICK_START guides
- [ ] Code comments where needed

### 🚀 PHASE 7: FINAL VALIDATION & GIT PUSH
- [ ] Run all tests (100% pass)
- [ ] Security scan (bandit)
- [ ] Type checking (mypy)
- [ ] Code review (pass all checks)
- [ ] Preflight verification (25/25 checks)
- [ ] Git commit all changes
- [ ] Push to remote

---

## 📋 SUCCESS CRITERIA

### Code Quality
- [ ] No CRITICAL or HIGH issues from code review
- [ ] All tests passing (100%)
- [ ] Test coverage 80%+
- [ ] Type checking 100%
- [ ] Security scan: 0 issues

### Functionality
- [ ] All 21 bugs fixed
- [ ] No regressions
- [ ] Bot can safely trade again
- [ ] Paper mode truly simulates (no live orders)
- [ ] Daily loss limits enforced

### Documentation
- [ ] All .md files updated
- [ ] BUG_REGISTRY.md complete
- [ ] FIX_LOG.md with all fixes
- [ ] Memory files updated
- [ ] Code comments where needed

### Safety
- [ ] No credentials in code/logs
- [ ] .gitignore complete
- [ ] Backup available
- [ ] Rollback plan documented

---

## 🔐 SAFETY PROTOCOLS

1. **Backup Before Any Change**: Full database backup taken
2. **Atomic Commits**: One bug per commit
3. **Test-First**: Tests written before code
4. **Code Review**: All changes reviewed
5. **Regression Testing**: Full test suite before push
6. **Documentation**: All changes documented
7. **Rollback Ready**: Backup available for any emergency

---

## 📞 CHECKPOINTS

| Phase | Target Date | Checkpoint | Status |
|-------|-------------|-----------|--------|
| Prep | TODAY (6/23) | Plan created | ⏳ |
| Critical | 6/24-6/25 | 8 bugs fixed | ⏳ |
| High | 6/26-6/27 | 8 bugs fixed | ⏳ |
| Medium | 6/28-6/29 | 5 bugs fixed | ⏳ |
| Tests | 6/30-7/1 | 150+ tests, 80%+ coverage | ⏳ |
| Docs | 7/2 | All .md files updated | ⏳ |
| Release | 7/3 | Validation + git push | ⏳ |

---

## 🎯 NEXT STEPS

1. ✅ **Create this execution plan** (DONE)
2. ⏳ **Set up test framework** (pytest, fixtures)
3. ⏳ **Start Bug #1: Order rejection handler** (NEXT)
4. ⏳ **Systematic fixes through all 21 bugs**
5. ⏳ **Comprehensive test suite**
6. ⏳ **Documentation + validation**
7. ⏳ **Git push with confidence**

---

**Document Status**: ACTIVE  
**Last Updated**: 2026-06-23  
**Next Review**: After each phase completion
