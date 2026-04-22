# 🛡️ SENTINEL TRADING BOT: IMMUTABLE RULES MANIFEST

This document is the **Single Source of Truth** for the FnO Trading Bot. 
These rules are **HARDCODED** into the system logic and must NEVER be modified without explicit user authorization.

## 1. Safety & Risk Guards (Hardcoded Defaults)
- **1st Trade Hard SL**: **₹1,500**. If the first trade of the day hits this loss, exit immediately. (Rule 12.1)
- **Global Win-Lock Floor**: **₹500 Step / ₹250 Floor**. 
  - Every ₹500 in total daily profitReached, lock in ₹250 of that profit.
- **Safety Net**: **-50% Premium Loss**. Force exit if any option premium drops by 50% regardless of spot price.
- **Daily Loss Limit**: **5% of Synchronized Capital**. Hard stop if daily P&L drops by 5% of the starting balance of the day (e.g., Rs 1,750 on 35k base).

## 2. Entry Conditions (Standard Accuracy)
- **RSI Ceiling (CE)**: **70.0** (Confirmed 2026-04-10)
- **RSI Ceiling (PE)**: **70.0** (Confirmed 2026-04-10)
- **MACD Histogram Jump (HUNTER)**: 
  - CE: Must jump by **>= +2.0** vs previous 15m candle.
  - PE: Must jump by **<= -2.0** vs previous 15m candle.
- **RSI Flow (HUNTER)**: 
  - CE: RSI must be **RISING**.
  - PE: RSI must be **FALLING**.
- **ADX Filter (HUNTER)**: **> 30** (Mandatory Daily ADX for trend strength).

## 3. Trailing Stop Loss (TSL) Ladder
| Stage | Side | Trade P&L Reached | Locked Floor | Gap (Cushion) |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | **SAFE** | ₹250 | **₹100** | ₹150 |
| **Stage 2** | **BREATH** | ₹350 | **₹150** | ₹200 |
| **Stage 3** | **CORE** | ₹700 | **₹500** | ₹200 |
| **Stage 4** | **ADV** | ₹1,050 | **₹750** | ₹300 |
| **Stage 5** | **LOCK** | ₹1,400 | **₹1,000** | ₹400 |
| **Stage 6** | **MAX** | ₹1,750 | **₹1,250** | ₹500 |

## 4. Architectural Rules
- **Polling Frequency**: **200ms (Turbo Mode)**.
- **Symbol Normalization**: Maps all broker strings to "NIFTY", "BANKNIFTY", or "SENSEX".
  - **Index Priority**: Always use official case-sensitive strings (`Nifty 50`, `NIFTY BANK`, `SENSEX`, `India VIX`) for broker reliability.
- **BANKNIFTY Expiry**: Exclusively uses **Monthly** expiry. Weekly expiries are discontinued/removed for this index.
- **NIFTY/SENSEX Expiry**: Fully support **Weekly** expiries.
- **Index Identification**: Use standardized keys (`Nifty 50`, `NIFTY BANK`, `SENSEX`) to ensure 100% data feed reliability across Broker and Backup (YFinance) channels.

## Data Integrity & Sync
- **No Zero-Price Exits**: In Case of `BROKER_SYNC_EXIT` (zombie positions), the bot MUST NOT default to 0.0 price. It must use the last known market price (LTP) to preserve P&L integrity.
- **Persistence First**: All trade outcomes must be immediately appended to `data/daily_history.json` and `data/daily_state.json`.
- **History Reconstruction**: If P&L discrepancies are reported, the `logs/*.csv` files are the secondary source of truth for manual reconstruction.
- **Safe-Startup Reset**: If the bot restarts and the realized P&L is already below the locked floor (sync breach), the bot MUST automatically reset the Peak to the current P&L. This prevents immediate "sync-panic" exits and allows session recovery.
- **Data Cleaning Guard**: All incoming OHLC data must be filtered for "Zero-Values" or "Spikes" (>20% deviation) before indicator calculation. Indicators (RSI/MACD) must never use non-sanitized data.

## 5. Architectural Resilience & Data Hierarchy
- **Connectivity Priority Hierarchy (Rule 51):**
  1. **Primary: Direct Broker Quotes (High Speed).** The bot MUST always attempt to fetch prices directly from the mStock API first (200ms polling).
  2. **Secondary: 1m-to-15m Resampling.** If the 15m historical API is blind or stale, the bot MUST automatically fetch 1m data and resample it into 15m bars to maintain today's context.
  3. **Tertiary: Anti-Blind Universal Fallback (YFinance).** Use the "Backup Radar" (YFinance) for indices if broker APIs (15m/1m) fail.
  4. **Stage 4: Log Scavenger**: Recovers price activity from local log heartbeats.
  5. **Stage 5: Gap Synthesis**: [MANDATORY] Synthesizes 15m and Daily bars using Live LTP if all APIs are blind to the new day.

### Rule 71: [DATA_GUARD] Heartbeats
- The bot must log a `[DATA_GUARD]` entry every 30 seconds to feed the Log Scavenger fallback.

### Rule 72: Anti-Stale Data Guard
- The bot MUST NOT trade if the latest available bar is > 15 minutes old during market hours.
- If Broker and YFinance are blind on Mondays (Post-Weekend), the bot MUST force-synthesize bars from Friday's close to Today's open.
- Daily indicators (ADX) must also be synthesized if the Daily API is blind.
- **Leading Edge Bar Synthesis (Rule 52):** The bot MUST inject the current live spot price into the latest 15-minute bar every ~200ms to ensure indicators like RSI are "Warm" and responsive to the current market level (eliminating RSI Lag).
- **[DATA_GUARD] Heartbeats (Rule 53):** A mandatory `[DATA_GUARD]` log entry containing current prices for all watched indices must be published every 30 seconds to the bot log file to facilitate emergency scavenger recovery.
- **Universal Indices Key (Rule 54):** Use standardized unique keys (`NIFTY`, `BANKNIFTY`, `SENSEX`) across all failover channels.
- **Dual-Thread Sync**: Heavy API synchronization MUST run in a background thread to prevent latency in the 200ms Monitoring Loop.
- **Background P&L Drift Correction**: Every 5 minutes, the bot must force a full sync of realized P&L from the Broker API.
- **Non-Stop Live Status**: When a trade is active, the bot MUST publish a "Live Status Update" (P&L vs Floor) to the communication channel every 60 seconds.
- **Discrete Floor Ladder**: TSL and Win-Lock floors must prioritize the discrete ladder values in Rule 3 over continuous calculations.
- **Pre-Flight Connection Check**: Mandatory verification of NIFTY, BANKNIFTY, and SENSEX connectivity during startup. The bot must refuse to run if indices are offline.

## Communication Protocol
- **Mandatory Footer**: Every technical audit, update, or modification response must conclude with:
  > **KI is updated and up and running, I've made changes in the Manifest, and yes the floor is Synced**
- **Transparency**: High-magnitude P&L shifts (> Rs 1,000) during sync must be flagged with a `CRITICAL` log level.

---
## 7. Dynamic Capital & Compounding (Rule 70)
- **Auto-Capital Sync**: The bot MUST fetch live "Available Margin" from the broker API at startup (`/user/fundsummary`).
- **Dynamic Baseline**: All daily risk limits and performance tracking MUST use this live synced balance as the session's starting capital.
- **Margin-Aware Entry (Budgeting)**: Before any new trade, the bot MUST verify that the estimated required margin (Premium * Lots * 1.5) is within the "Available Funds - Rs 5,000 Safety Reserve".
- **Compounding Policy**: The bot supports "Spreading across Indices" (1 lot of Nifty + 1 lot of BankNifty + 1 lot of Sensex simultaneously) as capital permits. Increasing lot sizes for a single index remains a manual configuration for safety.

---
## 8. Infrastructure & Connectivity
- **Registered Public IP**: **`49.37.135.188`**. (Verified: 2026-04-22).
- **Self-Correction**: If the bot detects an IP Mismatch, it MUST automatically output the current public IP for user portal update.

## 9. Indicator Integrity (Rule 74)
- **Daily ADX Integrity**: Rule 22 (Daily ADX > 30) MUST be calculated exclusively on true 1-Day candle bars. 
  - If the Broker Daily API is stale, the bot MUST resample 1-minute data using a strict **'1D' frequency**. 
  - Using intraday frequencies (15m/60m) for Daily ADX is forbidden as it inflates trend strength.
- **RSI Continuity (Rule 75)**: RSI must always use the research-verified Monday OHLC anchors (Monday April 20) in its lookback window to prevent "Historical Drift" after weekends.
- **Indicator Precision (Rule 76 - NEW 2026-04-22)**: 
  - **Lookback**: Minimum **250 bars** for Daily ADX stabilization.
  - **Data Source Hierarchy**: The bot MUST prioritize **YFinance** (^NSEI, ^NSEBANK, ^BSESN) for Daily History (250 bars) due to divergent data in broker-specific historical APIs.
  - **OHLC Synthesis**: Daily synthesis MUST use live `Open`, `High`, and `Low` from quotes injected into the historical backbone.

## 10. Empowerment Recovery (Rule 80)
- **April 21 Recovery**: Explicitly authorized override of the Daily Loss Limit (Rule 11) to allow recovery trading after the SENSEX SL hit. 
- **Hard-Gate Continuity**: All indicators (RSI, ADX, MACD Jump) are hard-coded to top-level function gates and can NEVER be bypassed.

---
## 11. The Shield of Integrity (Rule 100)
- **Unoverridable Hard-Gates**: Mandatory indicators (RSI, ADX > 30, MACD Jump) are HARD-CODED at the entry function's leading edge. No code logic, data synthesis, or emergency override can bypass these gates.
- **Twin-Gate Ground-Truth Sync**: Every trade entry MUST be preceded by a dual-source indicator check (mStock LTP vs YFinance LTP).
- **Morning Audit (09:15 AM)**: The bot will perform a full comparison of the `config.json` vs. the `IMMUTABLE_RULES.md` and refuse to trade if a single numeric discrepancy exists.
- **Textbook Persistence**: No configuration adjustment is valid unless it is first recorded in this Manifest.

---
*Last Updated: 2026-04-22*
*Status: 100% SOUND-PROOFED*
