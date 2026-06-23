# 🐛 BUG REGISTRY - Paper Mode Testing Log
**Status**: ACTIVE TESTING  
**Date Started**: 2026-06-23  
**Duration**: Full trading day (9:15 AM - 3:30 PM IST)  
**Mode**: PAPER TRADING (live_trading=false)

---

## 📊 SUMMARY TABLE

| Bug # | Category | Title | Status | Evidence | Validated | Notes |
|-------|----------|-------|--------|----------|-----------|-------|
| #1 | CRITICAL | Order Rejection → Orphaned Positions | ⏳ TESTING | - | - | - |
| #2 | CRITICAL | Race Condition Entry/Exit | ⏳ TESTING | - | - | - |
| #3 | CRITICAL | Duplicate Entry Orders | ⏳ TESTING | - | - | - |
| #4 | CRITICAL | Credentials Protection | ⏳ TESTING | - | - | - |
| #5 | CRITICAL | Daily Loss Limits | ⏳ TESTING | - | - | - |
| #6 | CRITICAL | Session Logging Sanitization | ⏳ TESTING | - | - | - |
| #7 | CRITICAL | Login Logging Sanitization | ⏳ TESTING | - | - | - |
| #8 | CRITICAL | Paper Mode OrderManager | ⏳ TESTING | - | - | - |
| #9 | HIGH | Order Fill Confirmation | ⏳ TESTING | - | - | - |
| #10 | HIGH | Position Reconciliation | ⏳ TESTING | - | - | - |
| #11 | HIGH | SymbolMaster Singleton | ⏳ TESTING | - | - | - |
| #12 | HIGH | Exception Handling | ⏳ TESTING | - | - | - |
| #13 | HIGH | IV Calculation | ⏳ TESTING | - | - | - |
| #14 | HIGH | Config Safe Defaults | ⏳ TESTING | - | - | - |
| #15 | HIGH | API Response Logging | ⏳ TESTING | - | - | - |
| #16 | HIGH | .gitignore Protection | ⏳ TESTING | - | - | - |
| #17 | MEDIUM | OTP File Cleanup | ⏳ TESTING | - | - | - |
| #18 | MEDIUM | State Persistence | ⏳ TESTING | - | - | - |
| #19 | MEDIUM | History Atomicity | ⏳ TESTING | - | - | - |
| #20 | MEDIUM | Symbol Parsing | ⏳ TESTING | - | - | - |
| #21 | MEDIUM | External Monitoring | ⏳ TESTING | - | - | - |

---

## 🔍 DETAILED BUG TRACKING

### **BUG #1: Order Rejection → Orphaned Positions**
**Category**: CRITICAL  
**Risk**: Unbounded losses from stranded positions  

**Test Setup**:
```
Watch for order rejections in live market conditions
Verify position is retained for retry (not deleted)
Verify exit_trade() not called on rejection
```

**Expected Behavior** (PAPER MODE):
- ✅ Order placed: `[SUCCESS] ORDER PLACED! Broker ID: PAPER_ORDER_*`
- ✅ Order fills: `Order FILLED: NIFTY24JUN20500CE @ 500.25`
- ✅ Position closed: Position removed from data/positions.json

**What to Watch For**:
```bash
grep -E "SUCCESS.*ORDER|REJECTED|exit_trade\|ORDER_STATUS" logs/trading_bot_*.log

# Should see:
✅ [SUCCESS] ORDER PLACED! (order accepted)
   OR
✅ [ORDER REJECTED] Exit order rejected. Position retained. (retry next cycle)
```

**Pass Criteria**:
- [ ] Every successful order → position closed
- [ ] Every rejected order → position retained
- [ ] Never see position deleted on rejection
- [ ] Orphan count remains 0

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

### **BUG #2: Race Condition Entry/Exit**
**Category**: CRITICAL  
**Risk**: Data corruption during concurrent access  

**Test Setup**:
```
Monitor entry and exit happening simultaneously
Watch for P&L inconsistencies
Check position data corruption
```

**Expected Behavior** (PAPER MODE):
- ✅ Entry and exit can happen in same cycle (locked access)
- ✅ Position data always consistent
- ✅ P&L calculations always match state

**What to Watch For**:
```bash
tail -f logs/trading_bot_*.log | grep -E "EXIT CHECK|ENTRY|LOGIC_SNAPSHOT"

# Should see both happening without crashes:
[LOGIC_SNAPSHOT] NIFTY | Status: OK | Entry: 25600 | P&L: +5%
[EXIT CHECK] NIFTY | LTP: 25500 | Max Loss: 0.70%
(both in same cycle = lock working)
```

**Pass Criteria**:
- [ ] No crashes during concurrent access
- [ ] No "inconsistent data" errors
- [ ] P&L values match state file
- [ ] No torn reads on position mutations

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

### **BUG #3: Duplicate Entry Orders**
**Category**: CRITICAL  
**Risk**: Double-buying same contract  

**Test Setup**:
```
Monitor entry signals in rapid succession
Count orders per symbol per cycle
Verify [DUPLICATE_GUARD] message
```

**Expected Behavior** (PAPER MODE):
- ✅ Only 1 order per entry signal
- ✅ [DUPLICATE_GUARD] message blocks second order
- ✅ Order count matches signal count

**What to Watch For**:
```bash
grep -E "PLACING ORDER.*NIFTY|DUPLICATE_GUARD" logs/trading_bot_*.log

# Should see ONE order, then guard message:
PLACING ORDER: BUY 1 x NIFTY24JUN20500CE
[DUPLICATE_GUARD] Entry order still pending. Skipping to prevent duplicate.
```

**Pass Criteria**:
- [ ] [DUPLICATE_GUARD] appears
- [ ] Never see 2 orders for same symbol in 1 cycle
- [ ] Order count = signal count (not 2x)

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

### **BUG #4: Credentials Protection**
**Category**: CRITICAL  
**Risk**: API token theft  

**Test Setup**:
```bash
Check file permissions
Grep logs for tokens
Check git history
```

**Expected Behavior**:
- ✅ credentials.json has 0o600 permissions (owner only)
- ✅ credentials.json in .gitignore
- ✅ No tokens in logs or git history

**What to Watch For**:
```bash
# 1. File permissions
ls -la credentials.json
# Should show: -rw------- (600)

# 2. Grep logs
grep -E "token|access_\|password|session" logs/trading_bot_*.log
# Should return ZERO results

# 3. Check git
git log --all -S "access_token" --oneline
# Should return ZERO results
```

**Pass Criteria**:
- [ ] Permissions: 0o600 ✅
- [ ] In .gitignore ✅
- [ ] No tokens in logs ✅
- [ ] No tokens in git history ✅

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

### **BUG #5: Daily Loss Limits Enforced**
**Category**: CRITICAL  
**Risk**: Complete capital wipeout  

**Test Setup**:
```
Monitor circuit breaker activation
When daily loss > 5% → entries should be blocked
```

**Expected Behavior**:
- ✅ Circuit breaker activates at 5% daily loss
- ✅ [CIRCUIT_BREAKER] message appears
- ✅ Entry conditions checked but orders blocked

**What to Watch For**:
```bash
grep "CIRCUIT\|loss.*limit\|Daily P&L" logs/trading_bot_*.log | tail -20

# Should eventually show:
[CIRCUIT_BREAKER] Daily loss limit exceeded. Daily P&L: -5200.00 vs Limit: -5000.00.
No new entries allowed.

# Next entry signal should be skipped:
[ENTRY CHECK] NIFTY: ADX valid, RSI valid
[CIRCUIT_BREAKER] Daily loss limit exceeded... No new entries allowed.
(no order placed)
```

**Pass Criteria**:
- [ ] Circuit breaker message appears
- [ ] Entries are blocked after activation
- [ ] Daily loss correctly calculated
- [ ] Resets next trading day

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

### **BUG #6 & #7: Logging Sanitization (Session & Login)**
**Category**: CRITICAL  
**Risk**: Credential exposure in logs  

**Test Setup**:
```bash
Search for credential patterns
Verify only messages logged, not full responses
```

**Expected Behavior**:
- ✅ Errors logged without full response dict
- ✅ No tokens in logs
- ✅ Only safe fields logged

**What to Watch For**:
```bash
# Check for credential leaks
grep -E "\{.*\}|response|session_data\|login_data" logs/trading_bot_*.log | grep -i "token\|password\|secret"

# Should return ZERO matches

# Errors should look clean:
# GOOD: "Login error: Invalid credentials"
# BAD:  "Login error: {'token': 'abc123', 'response': {...}}"
```

**Pass Criteria**:
- [ ] grep credentials returns ZERO
- [ ] Error messages are clean (no dict dumps)
- [ ] Only message fields logged
- [ ] No credential exposure

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

### **BUG #8: Paper Mode OrderManager**
**Category**: CRITICAL  
**Risk**: Accidental live trading in paper mode  

**Test Setup**:
```
Verify all orders are PAPER_ORDER_*
No real broker order IDs appear
```

**Expected Behavior**:
- ✅ All orders are simulated: PAPER_ORDER_*
- ✅ No real broker IDs (numeric) in logs

**What to Watch For**:
```bash
grep "PAPER\|Broker ID\|ORDER" logs/trading_bot_*.log | head -20

# Should ONLY see:
PAPER ORDER placed: NIFTY24JUN20500CE
[SUCCESS] ORDER PLACED! Broker ID: PAPER_ORDER_20260623143652

# Should NOT see:
Broker ID: 12345678 (numeric real ID)
```

**Pass Criteria**:
- [ ] All orders are PAPER_ORDER_*
- [ ] No real broker IDs
- [ ] live_trading config = false
- [ ] No real trades at broker

**Test Result**: 
- Status: ⏳ PENDING
- Timestamp: -
- Evidence: -

---

## 📝 LOGGING INSTRUCTIONS

### **Every Hour** (Validation Check)

Run:
```bash
python monitoring/hourly_validation.py
```

It will:
1. Check bot still running
2. Count orders in logs
3. Verify no errors
4. Check P&L is reasonable
5. Validate all 21 bugs
6. Generate hourly report

### **At End of Day**

Run:
```bash
python monitoring/daily_summary.py
```

It will:
1. Compile all hourly reports
2. Generate final statistics
3. List any bugs found
4. Save logs to archive
5. Generate BUG_REGISTRY_TESTING_FINAL.md

---

## 📊 TESTING TIMELINE

| Time | Action | Check |
|------|--------|-------|
| 10:00 AM | Bot starts | No startup errors |
| 11:00 AM | 1st validation | 1+ entries, 0 crashes |
| 12:00 PM | 2nd validation | P&L reasonable |
| 1:00 PM | 3rd validation | No credential leaks |
| 2:00 PM | 4th validation | Circuit breaker ready |
| 3:00 PM | 5th validation | Final check |
| 3:30 PM | Market close | Summary report |

---

## 🎯 SUCCESS CRITERIA

**PASS**: If by end of day:
- ✅ Bot runs for entire day without crashes
- ✅ All 21 bugs show PASS status
- ✅ No credential leaks in logs
- ✅ P&L calculations accurate
- ✅ Orders are all simulated (PAPER_ORDER_*)
- ✅ Daily loss limit works if tested
- ✅ Positions reconcile with state files

**FAIL**: If any of:
- ❌ Bot crashes more than once
- ❌ Any bug shows FAIL status
- ❌ Credentials appear in logs
- ❌ Real orders appear (not PAPER_)
- ❌ Data corruption detected
- ❌ Duplicate orders for same symbol

---

## 📎 NOTES

- This registry is LIVE during testing
- Updated every hour with validation results
- Final version saved as BUG_REGISTRY_TESTING_FINAL.md
- All logs saved in logs/ directory for reference

---

**READY TO START TESTING?** Provide credentials and we begin! 🚀
