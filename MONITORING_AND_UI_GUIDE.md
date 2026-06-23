# 📡 MONITORING & UI GUIDE
**For**: Live Trading Oversight  
**Date**: 2026-06-23

---

## 📌 QUICK ANSWER: UI CHANGES NEEDED?

**NO UI CHANGES NEEDED** ✅

This is a **backend trading bot** (FastAPI + Python), not a web application.

- ✅ No frontend to update
- ✅ No dashboards to modify  
- ✅ No UI components affected
- ✅ All changes are backend logic only

**Monitoring is done via**:
1. **Logs** (text files in `logs/`)
2. **File State** (JSON files in `data/`)
3. **Telegram Alerts** (already wired)
4. **External Heartbeat** (new in Bug #21)

---

## 🔍 MONITORING OPTIONS

### Option 1: **Real-Time Log Monitoring** (Recommended for Testing)

**Live tail logs**:
```bash
# Follow bot logs in real-time
tail -f logs/trading_bot_*.log

# Or with filtering:
tail -f logs/trading_bot_*.log | grep -E "TURBO|ENTRY|EXIT|CIRCUIT|ERROR"

# Color highlight important messages:
tail -f logs/trading_bot_*.log | grep --color=always -E "SUCCESS|REJECTED|ERROR|CIRCUIT"
```

**Key Log Markers to Watch**:
- ✅ `[TURBO ENTRY]` = Entry signal triggered
- ✅ `[TURBO EXIT]` = Exit signal triggered  
- ✅ `[SUCCESS] ORDER PLACED` = Order accepted
- ✅ `[ORDER REJECTED]` = Order failed
- ✅ `[CIRCUIT BREAKER]` = Daily loss limit hit
- ⚠️ `[ERROR]` = Something went wrong
- 🔴 `[CRITICAL]` = Serious issue

**Watch these for Bug Validation**:
```bash
# Check for duplicate order guards
grep DUPLICATE_GUARD logs/*.log

# Check for orphaned positions
grep ORPHANED_POSITIONS logs/*.log

# Check for race conditions
grep "torn read\|inconsistent" logs/*.log

# Check for credential leaks
grep -E "token|password|secret" logs/*.log

# Monitor circuit breaker
grep CIRCUIT logs/*.log
```

---

### Option 2: **Web Dashboard (Optional - Advanced)**

**Currently Available**: Telegram notifications (already integrated)

**To Add Web Dashboard** (Future Enhancement):
```python
# Would require new development:
# 1. Create FastAPI endpoints for stats
# 2. Build React/Vue frontend
# 3. Real-time WebSocket updates
# This is OUT OF SCOPE for current fixes
```

**For Now**: Use Telegram alerts + log monitoring

---

### Option 3: **File State Monitoring**

**Monitor position state**:
```bash
# Check active positions
cat data/positions.json | python -m json.tool | head -50

# Check closed trades
cat data/daily_history.json | python -m json.tool | tail -5

# Monitor daily P&L
cat data/daily_state.json
```

**Check for corruption**:
```bash
# Verify valid JSON
python -c "import json; json.load(open('data/positions.json'))"
python -c "import json; json.load(open('data/daily_history.json'))"
python -c "import json; json.load(open('data/daily_state.json'))"
```

---

### Option 4: **Telegram Alerts** (Already Configured)

**Bot sends automatic Telegram notifications for**:
- ✅ Entry signals triggered
- ✅ Exits executed
- ✅ Daily P&L updates
- ✅ System errors
- ✅ Circuit breaker activation

**To receive alerts**:
1. Add bot's Telegram token to credentials
2. Bot automatically sends messages
3. Monitor phone for real-time updates

---

### Option 5: **External Heartbeat Monitoring** (Bug #21 - Optional)

**Set up external monitoring**:
```bash
# 1. Use free service like Uptime Kuma or Healthchecks.io
# 2. Configure environment variables:
export ENABLE_EXTERNAL_WATCHDOG=true
export WATCHDOG_URL=https://uptime.example.com/ping/your-bot-id
export WATCHDOG_INTERVAL=60

# 3. Start bot
python main.py

# 4. If heartbeat stops → Automatic SMS/webhook alert
```

**Services that work**:
- **Uptime Kuma** (Self-hosted, free) - Recommended
- **Healthchecks.io** (Managed, free tier)
- **Custom webhook** (Your own notification service)

---

## 📊 MONITORING DASHBOARD SETUP (DIY)

**If you want a simple monitoring dashboard**, create this script:

```python
# monitoring_dashboard.py
import json
import time
from datetime import datetime
from pathlib import Path

def get_live_status():
    """Get current bot status from files"""
    
    # Load positions
    positions_file = Path("data/positions.json")
    positions = json.load(open(positions_file)) if positions_file.exists() else {}
    
    # Load daily state
    state_file = Path("data/daily_state.json")
    state = json.load(open(state_file)) if state_file.exists() else {}
    
    # Load history
    history_file = Path("data/daily_history.json")
    history = json.load(open(history_file)) if history_file.exists() else []
    
    return {
        "timestamp": datetime.now().isoformat(),
        "active_positions": len(positions),
        "today_trades": len(history),
        "daily_pnl": state.get("daily_pnl", 0),
        "capital": state.get("current_capital", 0),
        "positions": list(positions.keys()),
    }

if __name__ == "__main__":
    while True:
        status = get_live_status()
        print(f"\n{'='*50}")
        print(f"Bot Status: {status['timestamp']}")
        print(f"{'='*50}")
        print(f"Active Positions: {status['active_positions']}")
        print(f"Today's Trades: {status['today_trades']}")
        print(f"Daily P&L: ₹{status['daily_pnl']:.2f}")
        print(f"Capital: ₹{status['capital']:.2f}")
        if status['positions']:
            print(f"Open: {', '.join(status['positions'])}")
        print(f"{'='*50}")
        time.sleep(30)  # Update every 30 seconds
```

**Run dashboard**:
```bash
python monitoring_dashboard.py
```

---

## 🎯 RECOMMENDED MONITORING SETUP

### **For Testing Phase** (Paper Mode)
```
1. Terminal 1: tail -f logs/trading_bot_*.log
2. Terminal 2: python monitoring_dashboard.py (optional)
3. Phone: Telegram notifications if configured
```

### **For Live Trading**
```
1. Terminal 1: tail -f logs/trading_bot_*.log (or use tmux/screen)
2. External Watchdog: Uptime Kuma heartbeat (if configured)
3. Phone: Telegram alerts + SMS from watchdog
4. Optional: Simple JSON dashboard refresh every 30s
```

---

## 📋 WHAT TO MONITOR DURING VALIDATION

### **Every 5 Minutes**
- ✅ Is bot still running? (Check log tail)
- ✅ Any ERROR messages? (Search logs)
- ✅ Daily P&L reasonable? (Check state)

### **Every 30 Minutes**
- ✅ Trades executing as expected? (Count in history)
- ✅ P&L calculations correct? (Manual verify)
- ✅ No duplicate orders? (Count per symbol)

### **Every Hour**
- ✅ Position reconciliation working? (Check logs)
- ✅ Circuit breaker would trigger? (Calculate daily loss)
- ✅ No crashes or hangs? (Bot responsive)

### **Daily**
- ✅ Backup taken? (Safety)
- ✅ Logs rotated? (Disk space)
- ✅ Database consistent? (Verify JSON files)

---

## 🔧 MONITORING CHECKLIST

```markdown
## Daily Monitoring Checklist

### Before Market Open (9:15 AM)
- [ ] Check bot is running: `ps aux | grep python`
- [ ] Verify logs exist: `ls -lah logs/`
- [ ] Check capital: `cat data/daily_state.json`
- [ ] Verify config: `cat config.json | grep live_trading`

### During Market Hours (10:00 AM - 3:30 PM)
- [ ] Watch logs: `tail -f logs/trading_bot_*.log`
- [ ] Count trades: `cat data/daily_history.json | wc -l`
- [ ] Monitor P&L: Check logs for daily values
- [ ] No crashes: Check for CRITICAL errors
- [ ] Alerts received: Any Telegram notifications?

### After Market Close (3:30 PM+)
- [ ] Final P&L: `cat data/daily_state.json`
- [ ] Trade count: All expected trades recorded?
- [ ] Backup taken: `cp -r data/ data_backup_$(date +%Y%m%d)`
- [ ] Logs archived: For record keeping
- [ ] No orphans: `grep ORPHANED logs/*.log`

### Weekly
- [ ] Win rate calculation: Manual verify
- [ ] Bug #1-21 validation: Random spot checks
- [ ] Credentials check: Still encrypted?
- [ ] Storage check: Disk usage acceptable?
- [ ] Archives: Old logs backed up?
```

---

## ⚠️ CRITICAL MONITORING RULES

1. **Always monitor first 1 hour of trading**
   - If any bug manifests, it shows up early
   - First trades are highest risk

2. **Daily loss limit is HARD LIMIT**
   - Can't override
   - Protects capital
   - Resets daily

3. **Never share logs with credentials**
   - Logs are now sanitized
   - No tokens should appear
   - Verify before sharing

4. **Keep monitoring even if "working"**
   - Edge cases appear over time
   - New scenarios may trigger bugs
   - Monitoring catches them early

---

## 🚨 ALERTS TO WATCH FOR

### **RED FLAGS** 🔴 (Stop and investigate)
- `[CRITICAL]` messages
- Orphaned positions detected
- Order rejection loops
- Circuit breaker constantly triggered
- Crashes or hangs
- P&L calculation errors

### **YELLOW FLAGS** 🟡 (Review but proceed)
- `[ERROR]` messages
- API timeouts
- Slow response times
- Missing data files
- Telegram notification failures

### **GREEN FLAGS** 🟢 (All good)
- Regular [TURBO ENTRY] signals
- [SUCCESS] ORDER PLACED messages
- Smooth P&L calculations
- No ERROR messages
- Consistent 200ms loops

---

## 📱 TELEGRAM SETUP

**Bot automatically sends**:
```
✅ Entry: NIFTY CE @ ₹500
✅ Exit: NIFTY CE @ ₹510 | P&L: +₹10
📊 Daily: P&L ₹1,500 | Trades 3
⚠️ Loss: P&L -₹5,200 | CIRCUIT BREAKER
🔴 Error: Order failed - retrying
```

**Telegram is already wired**, monitor your phone

---

## ✅ FINAL SETUP CHECKLIST

Before going live:

- [ ] Paper mode testing complete (2+ hours)
- [ ] All logs reviewed (no credential leaks)
- [ ] All P&L calculations verified
- [ ] Order lifecycle tested (rejection, fills, etc)
- [ ] Position reconciliation working
- [ ] Daily loss limit tested
- [ ] Backup system verified
- [ ] Monitoring tools ready
- [ ] Telegram alerts configured
- [ ] External watchdog configured (optional)

---

**Summary**: No UI changes needed. Monitor via logs + Telegram alerts. Optional: Simple JSON dashboard for real-time stats.
