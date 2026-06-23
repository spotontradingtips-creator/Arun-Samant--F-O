# MORNING READINESS CHECKLIST

Follow these steps every morning at **09:00 AM** to ensure the bot is ready for a safe and profitable session.

### 1. Connectivity & Authentication (FIRST STEP)
- **Dashboard Status**: Open the Sentinel Hub in your browser.
- **Login Request**: The header must show **"STATUS: ONLINE"** in green.
- **OTP Entry**: If it shows "SESSION EXPIRED", click **"INITIATE LOGIN REQUEST"**, check your phone, and enter the OTP immediately. **The bot cannot talk to the market without this.**

### 2. State Cleanup
- **Check active positions**: Open `data/positions.json`. If you have no overnight trades, this file must be `{}`.
- **Clear old logs**: Ensure you are looking at the log file with today's date.

### 3. Automated Audit (CRITICAL)
Run the following command in your terminal:
```powershell
python src/pre_flight_audit.py
```
**Wait for ALL CHECKS to return [PASS].** This scan proves that the "Safety Shield" (15-min rule) is active in the code.
- **Check for [WARM-UP] logs**: If the bot says "Indicators Warming Up", wait a few minutes until it has 100 bars.
- [ ] **Check Data Synthesis**: Verify logs do NOT show `NIFTY ENTRY BLOCKED: DATA BLIND SPOT`. If they do, wait for the `[FIX]` synthesis heartbeats to appear.
- [ ] **Verify Indicator Warm-up**: Ensure RSI is roughly aligned with live charts (not stuck at Friday's close).
- [ ] **Monitor Entry Conditions**: Confirm bot is scanning for Nifty, BNF, and Sensex.
- **Check for [FIX] logged**: Verify that 1m-resampling or YFinance fallbacks correctly triggered to fix any "Stale" indicator readings.

### 4. Launch Sequence
1. **Restart the Bot**: Close any old terminal windows. Run `python main.py`.
2. **Verify Heartbeat**: Ensure you see "ENTRY MONITORING THREAD STARTED" in the logs.
3. **Verify Settings**: Check the Dashboard to confirm your **Profit Target (Rs 350)** and **Lots** are exactly what you want.

---
> [!IMPORTANT]
> The bot is now "Hardcoded" to wait for 15-minute candle closes. **Never expect a reversal exit at 09:20 or 09:27**; it will always happen at 09:30, 09:45, etc.
