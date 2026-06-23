# 🧪 PAPER MODE SETUP & VALIDATION GUIDE
**For**: Testing all 21 bug fixes safely  
**Date**: 2026-06-23  
**Goal**: Change live_trading=false and validate fixes without real trades

---

## 📋 QUICK START (5 Minutes)

### Step 1: Open config.json
```bash
# Option A: Direct file editing
nano config.json
# or
vim config.json
# or open in VS Code/any text editor
```

### Step 2: Find and Change This Line
```json
// CURRENT (LIVE MODE - DANGEROUS):
"trading_mode": {
    "live_trading": true,  ← CHANGE THIS TO FALSE
    ...
}

// AFTER CHANGE (PAPER MODE - SAFE):
"trading_mode": {
    "live_trading": false,  ← Now it's safe
    ...
}
```

### Step 3: Save and Verify
```bash
# Verify the change
grep -A 2 "trading_mode" config.json
# Should show: "live_trading": false
```

### Step 4: Start Bot
```bash
python main.py
# Bot now runs in PAPER MODE (no real trades)
```

---

## 🎛️ UI OPTION: Config Editor Tool

**If you want a UI instead of editing files**, use this tool:

### **Method 1: Simple Python Script** (Quick)

Create `config_editor.py`:
```python
#!/usr/bin/env python3
"""Simple config editor UI"""

import json
import sys
from pathlib import Path

def edit_config():
    config_path = Path("config.json")
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("\n" + "="*50)
    print("ANTIGRAVITY BOT - CONFIG EDITOR")
    print("="*50)
    
    # Show current state
    print(f"\n📊 CURRENT SETTINGS:")
    print(f"  Live Trading: {config['trading_mode']['live_trading']}")
    print(f"  Daily Loss Limit: {config['capital']['daily_loss_limit_percent']}%")
    print(f"  Initial Capital: ₹{config['capital']['initial_capital']}")
    
    # Ask for changes
    print("\n⚙️  CHANGE SETTINGS:")
    print("\n1. Switch to PAPER MODE (Safe for Testing)")
    print("2. Switch to LIVE MODE (Real Trading)")
    print("3. View Full Config")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        config['trading_mode']['live_trading'] = False
        print("\n✅ Switched to PAPER MODE")
        print("   Orders will be simulated (no real trades)")
    
    elif choice == "2":
        confirm = input("\n⚠️  WARNING: Switch to LIVE MODE? (yes/no): ").strip().lower()
        if confirm == "yes":
            config['trading_mode']['live_trading'] = True
            print("\n⚠️  Switched to LIVE MODE")
            print("   Real trades will execute!")
        else:
            print("Cancelled.")
            return
    
    elif choice == "3":
        print("\n📋 FULL CONFIG:")
        print(json.dumps(config, indent=2))
        return
    
    elif choice == "4":
        print("Exiting.")
        return
    
    else:
        print("Invalid option.")
        return
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"\n💾 Config saved to {config_path}")
    print(f"🚀 Ready to start bot with:")
    print(f"   python main.py")

if __name__ == "__main__":
    edit_config()
```

**Run it**:
```bash
python config_editor.py
# Follow the prompts to switch modes
```

---

### **Method 2: Web UI Dashboard** (More Advanced)

Create `web_config.py`:
```python
#!/usr/bin/env python3
"""Web UI for config changes"""

from flask import Flask, render_template_string, request, jsonify
import json
from pathlib import Path

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Antigravity Bot - Config</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        .status { 
            padding: 10px; 
            border-radius: 5px; 
            margin: 10px 0;
            font-weight: bold;
        }
        .status.live { background: #ffebee; color: #c62828; }
        .status.paper { background: #e8f5e9; color: #2e7d32; }
        button { 
            padding: 10px 20px; 
            font-size: 16px; 
            border: none; 
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn-paper { background: #4caf50; color: white; }
        .btn-live { background: #ff9800; color: white; }
        .btn-paper:hover { background: #45a049; }
        .btn-live:hover { background: #e68900; }
        .settings { margin-top: 20px; }
        .setting-item { 
            background: white; 
            padding: 10px; 
            margin: 10px 0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Antigravity Bot - Config</h1>
        
        <div id="status" class="status"></div>
        
        <div>
            <button class="btn-paper" onclick="setMode('paper')">
                📄 PAPER MODE (Testing)
            </button>
            <button class="btn-live" onclick="setMode('live')">
                ⚠️ LIVE MODE (Real Trading)
            </button>
        </div>
        
        <div class="settings">
            <h3>📊 Current Settings:</h3>
            <div id="settings-display"></div>
        </div>
    </div>
    
    <script>
        async function setMode(mode) {
            if (mode === 'live') {
                const confirm = window.confirm('⚠️ WARNING: Switch to LIVE MODE? Real trades will execute!');
                if (!confirm) return;
            }
            
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ live_trading: mode === 'live' })
            });
            
            const data = await response.json();
            loadStatus();
        }
        
        async function loadStatus() {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            const status = document.getElementById('status');
            const mode = config.trading_mode.live_trading;
            
            status.className = 'status ' + (mode ? 'live' : 'paper');
            status.textContent = mode ? '🔴 LIVE MODE (Real Trades)' : '🟢 PAPER MODE (Simulated)';
            
            document.getElementById('settings-display').innerHTML = `
                <div class="setting-item">
                    <strong>Mode:</strong> ${mode ? 'LIVE' : 'PAPER'}
                </div>
                <div class="setting-item">
                    <strong>Daily Loss Limit:</strong> ${config.capital.daily_loss_limit_percent}%
                </div>
                <div class="setting-item">
                    <strong>Initial Capital:</strong> ₹${config.capital.initial_capital}
                </div>
            `;
        }
        
        loadStatus();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config', methods=['GET'])
def get_config():
    with open('config.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/config', methods=['POST'])
def set_config():
    data = request.json
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    config['trading_mode']['live_trading'] = data.get('live_trading', False)
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    return jsonify({"status": "ok", "mode": "LIVE" if data.get('live_trading') else "PAPER"})

if __name__ == '__main__':
    print("Opening http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=False, port=5000)
```

**Run it**:
```bash
pip install flask  # One-time setup
python web_config.py
# Open browser: http://localhost:5000
# Click buttons to switch modes
```

---

## ⚡ WHAT HAPPENS WHEN live_trading=false

### **Summary**:
When `live_trading=false`, the bot:
- ✅ Creates fake "PAPER" orders instead of real orders
- ✅ Simulates order fills instantly (in paper mode)
- ✅ Tracks positions only in memory (not at broker)
- ✅ Calculates P&L for simulation
- ✅ No real capital is used
- ✅ No real trades execute at broker
- ✅ Safe for testing all bugs

### **Detailed Behavior**:

#### Entry Signal (What You'll See in Logs):
```
# 1. Entry condition detected
[ENTRY CHECK] NIFTY: MACD bullish, RSI valid
[TURBO ENTRY] Entering NIFTY

# 2. Order placed (in PAPER mode)
DEBUG: Placing Order -> Symbol: 'NIFTY24JUN20500CE', Exch: 'NFO', Side: 'BUY'
PAPER ORDER placed: NIFTY24JUN20500CE
[SUCCESS] ORDER PLACED! Broker ID: PAPER_ORDER_20260623143652456789

# 3. Order fills immediately (paper mode)
Order FILLED: NIFTY24JUN20500CE @ 500.25
[ENTRY SUCCESSFUL] NIFTY | Type: CE | Premium: ₹500.25 | SL: 0.70%

# 4. Position added to memory
✅ Position stored in data/positions.json (not at broker)
```

#### Exit Signal (What You'll See in Logs):
```
# 1. Exit condition triggered
[TURBO EXIT] NIFTY (PROFIT_TARGET)
DEBUG: Placing Order -> Symbol: 'NIFTY24JUN20500CE', Exch: 'NFO', Side: 'SELL'

# 2. Order placed
PAPER ORDER placed: NIFTY24JUN20500CE
[SUCCESS] ORDER PLACED! Broker ID: PAPER_ORDER_20260623144512341234

# 3. Order fills
Order FILLED: NIFTY24JUN20500CE @ 510.50
P&L: +₹10.25 per share

# 4. Trade closed
✅ Closed trade stored in data/daily_history.json
```

#### State Files (What Changes):
```bash
# BEFORE paper trade:
data/positions.json = {}  (empty)

# DURING paper trade:
data/positions.json = {
  "NIFTY": {
    "symbol": "NIFTY24JUN20500CE",
    "entry_price": 500.25,
    "entry_time": "2026-06-23 14:36:52",
    ...
  }
}

# AFTER paper trade exits:
data/positions.json = {}  (empty again)
data/daily_history.json = [
  {
    "symbol": "NIFTY24JUN20500CE",
    "entry_price": 500.25,
    "exit_price": 510.50,
    "pnl": 10.25,
    "exit_reason": "PROFIT_TARGET"
  }
]
```

---

## 🧪 HOW TO VALIDATE BUGS IN PAPER MODE

### **Bug #1: Order Rejection Handling**

**Setup**: Paper mode doesn't reject orders, so we simulate the fix by checking logs

**What to do**:
```bash
# 1. Start bot
python main.py

# 2. Watch logs for order flow
tail -f logs/trading_bot_*.log | grep -E "SUCCESS|REJECTED|ORDER"

# 3. Expected output:
[SUCCESS] ORDER PLACED! Broker ID: PAPER_ORDER_*
# Then:
Order FILLED: ...

# 4. Verify the fix:
# ✅ If live order is placed AND then position is closed
# ✅ Exit happens ONLY after order succeeds
# ❌ If exit happens even before order placement (old bug)
```

**Validation**: Order placed → Filled → Position closed (in correct sequence)

---

### **Bug #2: Race Condition Prevention**

**What to do**:
```bash
# 1. Run bot for 1+ hour
python main.py

# 2. Watch for concurrent access (entry + exit happening simultaneously)
tail -f logs/trading_bot_*.log | grep -E "EXIT CHECK|ENTRY|LOGIC_SNAPSHOT"

# 3. Expected output:
[LOGIC_SNAPSHOT] NIFTY | Status: OK | ...
[EXIT CHECK] NIFTY | P&L: +5%
# Both can happen in same cycle (locked access)

# 4. Verify fix:
# ✅ No crashes during concurrent access
# ✅ P&L values are consistent (not torn reads)
# ✅ Position data never corrupted
```

**Validation**: Run 1+ hours, no crashes, consistent data

---

### **Bug #3: Duplicate Order Prevention**

**What to do**:
```bash
# 1. Monitor entry orders carefully
tail -f logs/trading_bot_*.log | grep "PAPER ORDER\|ENTRY SUCCESSFUL"

# 2. Expected output for ONE entry signal:
# First cycle:
PLACING ORDER: BUY 1 x NIFTY24JUN20500CE
PAPER ORDER placed: NIFTY24JUN20500CE
[ENTRY SUCCESSFUL] NIFTY | ...

# Second cycle (same symbol):
[DUPLICATE_GUARD] Entry order still pending for NIFTY. Skipping to prevent duplicate.

# After order completes:
# (Flag clears, next entry signal allowed)

# 3. Count orders in logs:
grep -c "PLACING ORDER.*NIFTY" logs/trading_bot_*.log
# Should match number of entry signals, NOT double
```

**Validation**: Only 1 order per entry signal, [DUPLICATE_GUARD] prevents seconds

---

### **Bug #4: Credentials Protection**

**What to do**:
```bash
# 1. Check file permissions
ls -la credentials.json
# Should show: -rw------- (600)

# 2. Check .gitignore
grep credentials .gitignore
# Should show: credentials.json

# 3. Search logs for tokens
grep -E "token|password|secret|access_" logs/*.log
# Should return: ZERO results

# 4. Check git history
git log --all -S "access_token" --oneline
# Should return: ZERO results
```

**Validation**: Permissions 0o600, in .gitignore, no credentials in logs

---

### **Bug #5: Daily Loss Limit Enforcement**

**What to do**:
```bash
# 1. Run bot and wait for losing trades
# Let it naturally lose ~5000+ (or simulate by editing positions)

# 2. Watch for circuit breaker activation
tail -f logs/trading_bot_*.log | grep "CIRCUIT\|loss.*limit"

# 3. Expected output:
[CIRCUIT BREAKER] Daily loss limit exceeded. Daily P&L: -5200.00 vs Limit: -5000.00. No new entries allowed.

# 4. Verify entry is blocked:
# After circuit breaker message:
[ENTRY CHECK] NIFTY: ADX valid, RSI valid, MACD valid
# But NO entry order placed (entry blocked)

# 5. Check it's active:
grep "CIRCUIT_BREAKER.*No new entries" logs/*.log
```

**Validation**: Circuit breaker blocks entries when daily loss > 5%

---

### **Bug #6 & #7: Logging Sanitization**

**What to do**:
```bash
# 1. Search all logs for credential patterns
grep -r -E "session|token|password|access_\|secret" logs/
# Should return: ZERO results

# 2. When errors occur, logs should be clean:
tail -f logs/trading_bot_*.log | grep -i "error\|login"

# 3. Expected output:
Login error: Invalid credentials
# NOT:
Login error: {'session_token': 'abc123', 'response': {...}}

# 4. Verify complete:
grep -E "\\{.*\\}" logs/trading_bot_*.log | grep -i "token\|session"
# Should return: ZERO results
```

**Validation**: grep finds zero credential patterns in logs

---

### **Bug #8: Paper Mode Works Correctly**

**What to do**:
```bash
# 1. Verify config shows paper mode
grep "live_trading" config.json
# Should show: "live_trading": false

# 2. Start bot and watch for PAPER orders
python main.py
tail -f logs/trading_bot_*.log | grep "PAPER\|ORDER"

# 3. Expected output:
PAPER ORDER placed: NIFTY24JUN20500CE
# NOT:
Order placed: Broker ID: 12345678 (real broker ID)

# 4. Verify no real orders at broker:
# Check broker account - should show ZERO trades
# (Only positions in bot memory)
```

**Validation**: All orders show "PAPER_ORDER_*", not real broker IDs

---

## 📊 FULL VALIDATION WORKFLOW

### **Day 1: Setup & Basic Testing**
```bash
# 1. Edit config (choose UI or file)
# Option A: nano config.json
# Option B: python config_editor.py
# Option C: python web_config.py (browser UI)

# 2. Set live_trading = false

# 3. Start bot
python main.py

# 4. Watch logs for first 30 min
tail -f logs/trading_bot_*.log

# 5. Verify paper trades execute
# Look for: PAPER ORDER → FILLED → [ENTRY SUCCESSFUL]/[EXIT]
```

### **Day 2: Bug-Specific Validation**
```bash
# For each bug (1-21):
# 1. Know what to look for (marker in logs)
# 2. Run bot
# 3. Wait for scenario
# 4. Check logs
# 5. Verify expected behavior

# Example for Bug #1 (Order Rejection):
grep -E "SUCCESS.*ORDER|REJECTED" logs/*.log
# Count SUCCESS vs REJECTED
# Verify all have follow-up (filled or exit)
```

### **Day 3: Stress Testing**
```bash
# Run bot for 2+ hours continuously
# Watch for:
# - No crashes
# - P&L calculations accurate
# - Positions reconcile with state files
# - No duplicate orders
# - Circuit breaker works if tested

# Sample monitoring:
watch -n 30 'echo "P&L:" && cat data/daily_state.json | jq .daily_pnl && echo "Trades:" && cat data/daily_history.json | wc -l'
```

### **Day 4: Final Sign-Off**
```bash
# If all bugs validated:
# 1. Edit config: live_trading = true
# 2. Start bot with REAL trading
# 3. Monitor closely (first hour is critical)
# 4. Reduce position size for real trading
```

---

## 🎛️ SWITCHING BETWEEN MODES

### **Option 1: Direct File Edit (Fastest)**
```bash
# Edit config.json
nano config.json
# Change: "live_trading": false to true (or vice versa)
# Save and restart bot

# Verify change
grep "live_trading" config.json
```

### **Option 2: Python Script (Interactive)**
```bash
python config_editor.py
# Select option 1 (Paper) or 2 (Live)
# Confirm
# Restart bot
```

### **Option 3: Web UI (Most User-Friendly)**
```bash
python web_config.py
# Open http://localhost:5000 in browser
# Click PAPER MODE or LIVE MODE button
# Restart bot
```

---

## ✅ VERIFICATION CHECKLIST

After switching to paper mode:

```markdown
## Paper Mode Verification Checklist

### Config
- [ ] config.json shows: "live_trading": false
- [ ] Daily loss limit: 5.0
- [ ] Initial capital: 28000

### Logs
- [ ] Logs created in logs/ directory
- [ ] No ERROR messages (at startup)
- [ ] Bot waits for 10:00 AM
- [ ] Market open: "Commencing Turbo Ops"

### Orders
- [ ] All orders show: "PAPER_ORDER_*"
- [ ] No orders to real broker
- [ ] Orders fill immediately (paper mode)

### State Files
- [ ] data/positions.json exists (may be empty)
- [ ] data/daily_history.json exists (may be empty)
- [ ] data/daily_state.json exists

### Test Results
- [ ] Bug #1-8: CRITICAL bugs validated
- [ ] Bug #9-16: HIGH bugs validated
- [ ] Bug #17-21: MEDIUM bugs validated

### Ready for Live
- [ ] All bugs validated
- [ ] No crashes or data loss
- [ ] P&L calculations correct
- [ ] Position reconciliation working

### Switch to Live
- [ ] config.json: "live_trading": true
- [ ] Restart bot
- [ ] Monitor closely (first hour)
- [ ] Verify real orders appear in broker account
```

---

## 🚀 NEXT STEPS AFTER PAPER MODE VALIDATION

**Once all bugs pass paper mode testing**:

1. **Switch to Live Trading**:
   ```bash
   # Edit config.json
   nano config.json
   # Change: "live_trading": false → true
   # Restart bot
   ```

2. **Start with Small Capital**:
   - Reduce lot sizes initially
   - Test with 1 lot instead of normal 65
   - Monitor first 1-2 hours closely

3. **Monitor Real Trading**:
   - Watch logs for real order execution
   - Verify filled prices match expectations
   - Check P&L against actual returns

4. **Scale Gradually**:
   - After 1 day: Increase to 50% normal size
   - After 1 week: Full size
   - After 1 month: Confident

---

## 📱 SUMMARY

| Feature | Paper Mode (live_trading=false) | Live Mode (live_trading=true) |
|---------|--------------------------------|------------------------------|
| Order Type | PAPER_ORDER_* (simulated) | Real broker orders |
| Capital Used | None (simulation only) | Real capital |
| Risk | Zero (testing only) | Real money at risk |
| Order Fills | Instant (simulated) | Actual broker fills |
| Position Storage | Memory only (data/) | Memory + broker |
| Perfect for | Bug validation | Real trading |
| Time to Test All 21 Bugs | 2-4 hours | Too risky to test all |

---

**You can now confidently switch to paper mode and validate all 21 bugs! 🎉**
