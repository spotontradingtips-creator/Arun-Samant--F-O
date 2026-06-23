#!/bin/bash
#
# Full Day Paper Mode Testing Launcher
# Launches bot, sets up monitoring, and validates bugs hourly
#

set -e  # Exit on any error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$PROJECT_DIR/logs"
MONITORING_DIR="$PROJECT_DIR/monitoring"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ANTIGRAVITY BOT - FULL DAY PAPER MODE TESTING LAUNCHER   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# ==============================================================================
# STEP 1: VERIFY SETUP
# ==============================================================================
echo -e "\n${YELLOW}[1/5] Verifying Setup${NC}"

# Check .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}❌ ERROR: .env file not found${NC}"
    echo "Please create .env with mStock credentials:"
    echo "  API_KEY=your_key"
    echo "  API_SECRET=your_secret"
    echo "  CLIENT_CODE=your_code"
    echo "  PASSWORD=your_password"
    exit 1
fi
echo -e "${GREEN}✅ .env file found${NC}"

# Check config.json
if ! grep -q '"live_trading": false' "$PROJECT_DIR/config.json"; then
    echo -e "${RED}❌ WARNING: live_trading might not be set to false${NC}"
    grep "live_trading" "$PROJECT_DIR/config.json"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo -e "${GREEN}✅ config.json verified (PAPER MODE)${NC}"

# Create logs directory
mkdir -p "$LOGS_DIR"
echo -e "${GREEN}✅ Logs directory ready: $LOGS_DIR${NC}"

# Create monitoring reports directory
mkdir -p "$MONITORING_DIR/validation_reports"
echo -e "${GREEN}✅ Monitoring directory ready${NC}"

# ==============================================================================
# STEP 2: STOP ANY EXISTING BOT PROCESS
# ==============================================================================
echo -e "\n${YELLOW}[2/5] Cleaning Up Existing Processes${NC}"

# Kill any existing bot processes
if pgrep -f "python main.py" > /dev/null; then
    echo "Stopping existing bot processes..."
    pkill -f "python main.py" || true
    sleep 2
    echo -e "${GREEN}✅ Existing processes stopped${NC}"
else
    echo -e "${GREEN}✅ No existing processes found${NC}"
fi

# ==============================================================================
# STEP 3: LAUNCH BOT IN BACKGROUND
# ==============================================================================
echo -e "\n${YELLOW}[3/5] Launching Bot in Background${NC}"

cd "$PROJECT_DIR"

# Launch bot with output redirection
nohup python main.py >> "$LOGS_DIR/bot_launch.log" 2>&1 &
BOT_PID=$!

echo "Waiting for bot to start..."
sleep 5

# Verify bot is running
if ps -p $BOT_PID > /dev/null; then
    echo -e "${GREEN}✅ Bot launched successfully (PID: $BOT_PID)${NC}"
else
    echo -e "${RED}❌ Bot failed to start${NC}"
    echo "Check logs: $LOGS_DIR/bot_launch.log"
    cat "$LOGS_DIR/bot_launch.log"
    exit 1
fi

# ==============================================================================
# STEP 4: VERIFY BOT IS RUNNING
# ==============================================================================
echo -e "\n${YELLOW}[4/5] Verifying Bot Startup${NC}"

sleep 3

# Check for errors in initial logs
LATEST_LOG=$(ls -t "$LOGS_DIR"/trading_bot_*.log 2>/dev/null | head -1)
if [ -z "$LATEST_LOG" ]; then
    echo -e "${RED}❌ No trading bot logs created${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Bot logs: $(basename $LATEST_LOG)${NC}"

# Show initial startup messages
echo -e "\n${BLUE}Initial Bot Output:${NC}"
head -20 "$LATEST_LOG"

# ==============================================================================
# STEP 5: SETUP MONITORING
# ==============================================================================
echo -e "\n${YELLOW}[5/5] Setting Up Hourly Monitoring${NC}"

# Create monitoring script wrapper
cat > "$MONITORING_DIR/run_hourly_validation.sh" << 'EOF'
#!/bin/bash
# Run hourly validation every hour

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

while true; do
    echo "Running hourly validation at $(date)"
    python "$PROJECT_DIR/monitoring/hourly_validation.py"
    echo "Next validation in 60 minutes..."
    sleep 3600
done
EOF

chmod +x "$MONITORING_DIR/run_hourly_validation.sh"

# Launch monitoring in background
nohup "$MONITORING_DIR/run_hourly_validation.sh" >> "$MONITORING_DIR/monitoring.log" 2>&1 &
MONITORING_PID=$!

echo -e "${GREEN}✅ Monitoring script started (PID: $MONITORING_PID)${NC}"

# ==============================================================================
# SUMMARY
# ==============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    SETUP COMPLETE ✅                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}WHAT'S RUNNING:${NC}"
echo "  🤖 Bot Process ID: $BOT_PID"
echo "  📊 Monitoring PID: $MONITORING_PID"
echo "  📁 Logs Directory: $LOGS_DIR"

echo -e "\n${GREEN}HOW TO MONITOR:${NC}"
echo "  1. Watch logs in real-time:"
echo "     tail -f $LOGS_DIR/trading_bot_*.log | grep -E 'PAPER|SUCCESS|REJECTED|CIRCUIT|ERROR'"
echo ""
echo "  2. Check hourly validation reports:"
echo "     ls -la $MONITORING_DIR/validation_reports/"
echo ""
echo "  3. View bot status:"
echo "     ps -p $BOT_PID  (should show: running)"
echo ""
echo "  4. View monitoring status:"
echo "     ps -p $MONITORING_PID  (should show: running)"

echo -e "\n${GREEN}TESTING SCHEDULE:${NC}"
echo "  ⏰ Hourly: Automated bug validation (every hour)"
echo "  📊 End of day: Complete summary report"
echo "  🔍 Continuous: Log analysis for issues"

echo -e "\n${YELLOW}IMPORTANT:${NC}"
echo "  ✓ Bot is in PAPER MODE (live_trading=false)"
echo "  ✓ All orders are PAPER_ORDER_* (simulated)"
echo "  ✓ Real market data (NSE/BSE prices)"
echo "  ✓ No real capital used"
echo "  ✓ Safe to run all day"

echo -e "\n${BLUE}COMMANDS FOR MANAGING:${NC}"
echo "  Stop bot:        kill $BOT_PID"
echo "  Stop monitoring: kill $MONITORING_PID"
echo "  View bot logs:   tail -f $LOGS_DIR/trading_bot_*.log"
echo "  View full logs:  cat $LOGS_DIR/trading_bot_*.log"
echo "  Kill all:        pkill -f 'python main.py' && pkill -f 'run_hourly'"

echo -e "\n${GREEN}✅ Full day testing is now active!${NC}"
echo -e "Bot will run continuously until market close (3:30 PM IST)"
echo -e "Check back hourly for validation reports\n"
