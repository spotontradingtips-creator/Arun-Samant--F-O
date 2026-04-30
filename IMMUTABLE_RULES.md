# 🛡️ SENTINEL TRADING BOT: IMMUTABLE RULES MANIFEST

This document is the **Single Source of Truth** for the FnO Trading Bot. 
These rules are **HARDCODED** into the system logic and must NEVER be modified without explicit user authorization.

## 1. Safety & Risk Guards (Recovery Mode)
- **1st Trade Hard SL**: **₹2,000**. If the first trade of the day hits this loss, exit immediately. (Upgraded from ₹1,500)
- **Global Win-Lock Floor**: **₹1,000 Step / ₹500 Floor** (Discrete Logic). 
  - For every ₹1,000 in total daily profit reached, the system permanently locks in ₹500 of that profit.
- **Safety Net**: **-50% Premium Loss**. Force exit if any option premium drops by 50% regardless of spot price.
- **Daily Loss Limit**: **5% of Synchronized Capital**. Hard stop if daily P&L drops by 5% of the starting balance.

## 2. Entry Conditions (Standard Accuracy)
- **RSI Ceiling (CE)**: **70.0** (Confirmed 2026-04-10)
- **RSI Ceiling (PE)**: **70.0** (Confirmed 2026-04-10)
- **MACD Histogram Jump (HUNTER)**: 
  - CE: Must jump by **>= +1.0** vs previous 15m candle.
  - PE: Must jump by **<= -1.0** vs previous 15m candle.
- **RSI Flow (HUNTER)**: 
  - CE: RSI must be **RISING**.
  - PE: RSI must be **FALLING**.
- **ADX Filter (INTRADAY TREND)**: **>= 23.0** on the **15-minute** timeframe. (Daily ADX requirement removed).
- **VWAP Gate (DIRECTIONAL MASTER)**: 
  - CE: Enter ONLY if Spot Price is **ABOVE** 15m VWAP.
  - PE: Enter ONLY if Spot Price is **BELOW** 15m VWAP.
  - [HARD-GATE]: Entry is BLOCKED if VWAP is unavailable (nan/0).
  - Calculation: VWAP is anchored to the 15m timeframe using Future Proxy Volume for Indices.
- **VIX Filter (VOLATILITY)**: **>= 12.0** (India VIX). Skip all trading if volatility is too low.
- **Trading Window (TIME)**: 
  - Start: **09:30 AM** (9:15 AM + 15m Morning Buffer).
  - Cutoff: **03:15 PM** (No new entries after this time).
  - Market Close: **03:30 PM**.

## 3. Trailing Stop Loss (TSL) Ladder (Recovery Mode)
| Stage | Description | Trade P&L Reached | Locked Floor | Gap (Breathing Room) |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | **BREATHE** | ₹500 | **₹150** | ₹350 |
| **Stage 2** | **BANKER** | ₹1,000 | **₹550** | ₹450 |
| **Stage 3** | **RUNNER** | ₹1,800 | **₹1,300** | ₹500 |
| **Stage 4** | **EXPAND** | ₹3,000 | **₹2,300** | ₹700 |
| **Stage 5** | **MOONSHOT** | ₹5,000 | **₹3,800** | ₹1,200 |
| **Stage 6** | **TRAIL** | ₹7,000+ | **75% of Peak** | 25% of P&L |

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
- **Registered Public IP**: **`49.37.133.14`**. (Verified: 2026-04-27).
- **Self-Correction**: If the bot detects an IP Mismatch, it MUST automatically output the current public IP for user portal update.

## 9. Indicator Integrity (Rule 74)
- **Daily ADX Integrity**: Rule 22 (Daily ADX >= 22.0) MUST be calculated exclusively on true 1-Day candle bars. 
  - If the Broker Daily API is stale, the bot MUST resample 1-minute data using a strict **'1D' frequency**. 
  - Using intraday frequencies (15m/60m) for Daily ADX is forbidden as it inflates trend strength.
- **RSI Continuity (Rule 75)**: RSI must always use the research-verified Monday OHLC anchors (Monday April 20) in its lookback window to prevent "Historical Drift" after weekends.
  - **Indicator Precision (Rule 76)**: Minimum **250 bars** required for Daily ADX stabilization.
  - **Titan-Shield Primary (Rule 97.1)**: The bot MUST bypass the broker's Daily Historical API for Indices and use **YFinance** as the primary source for the 250-bar Daily ADX backbone. 
  - **Zero-Gap Injection**: The current Live LTP from the broker must be injected into the last YFinance bar to ensure real-time ADX precision without synthetic gaps.
  - **Hard-Coded Priority**: This hierarchy is locked in `src/market_data.py` and `src/fno_trading_bot.py`.

## 10. Empowerment Recovery (Rule 80)
- **April 21 Recovery**: Explicitly authorized override of the Daily Loss Limit (Rule 11) to allow recovery trading after the SENSEX SL hit. 
- **Hard-Gate Continuity**: All indicators (RSI, ADX, MACD Jump) are hard-coded to top-level function gates and can NEVER be bypassed.

---
## 11. The Shield of Integrity (Rule 100)
- **Unoverridable Hard-Gates**: Mandatory indicators (VWAP Gate, RSI, 15m ADX >= 23.0, MACD Jump >= 1.0) are HARD-CODED at the entry function's leading edge.
  - **VWAP Priority**: The 15m VWAP is the primary directional anchor. No CE entry below VWAP; no PE entry above VWAP.
- **Twin-Gate Ground-Truth Sync**: Every trade entry MUST be preceded by a dual-source indicator check (mStock LTP vs YFinance LTP).
- **Morning Audit (09:15 AM)**: The bot will perform a full comparison of the `config.json` vs. the `IMMUTABLE_RULES.md` and refuse to trade if a single numeric discrepancy exists.
- **Textbook Persistence**: No configuration adjustment is valid unless it is first recorded in this Manifest.

---
## 12. Data Continuity & Synthesis Guards (Broker-Blind Failsafe)
- **Volume Resilience**: When engaging fallback or gap-synthesis mechanisms, the system MUST enforce the existence of a 'volume' column (default to 0 if missing from the upstream source) before index-slicing. This guarantees zero `KeyError` crashes during indicator evaluation.
- **NoneType Indicator Guards**: The entry loop MUST validate indicator states (`i_df` or `d_df`) and explicitly flush cache and safely `continue` the cycle if `None` is returned, completely neutralizing `TypeError` subscript exceptions.

---
*Last Updated: 2026-04-29*
*Status: 100% SOUND-PROOFED*
