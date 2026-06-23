# 🛡️ SENTINEL TRADING BOT: IMMUTABLE RULES MANIFEST

This document is the **Single Source of Truth** for the FnO Trading Bot. 
These rules are **HARDCODED** into the system logic and must NEVER be modified without explicit user authorization.

## 1. Operating Mode (Manual Buy Only)
- **Manual Buy Only**: The bot is strictly prohibited from initiating buy orders. You place the buy order yourself manually via the broker platform.
- **Auto-Sell Logic**: The bot continuously monitors the Orders / Executed / Positions tabs at extreme speeds.
- **Immediate Execution**: As soon as a buy order is confirmed in the positions/orders tab, the bot reads the premium price, adds a hardcoded **+7 points**, and immediately places a Sell Limit Order.
- **Speed Target**: Execution speed target is ~200ms or faster.

## 2. Safety & Risk Guards (Disabled)
- **No Stop Loss**: The bot does NOT maintain any stop loss.
- **No Trailing Stop**: The Trailing Stop Loss (TSL) ladder is disabled. 
- The ONLY risk/exit parameter is the +7 point limit sell order.

## 3. Persistence & Reliability
- **Memory Retention**: The bot MUST reconnect automatically if restarted.
- **Open Position Sweep**: On startup/restart, the bot MUST check live open positions and immediately ensure that a +7 sell limit order is active for any existing manual buy.
- **Orphan Guard**: If the limit order was canceled manually, the bot should detect the open position and place the +7 sell limit order again.

## 4. Architectural Rules
- **Polling Frequency**: **200ms (Turbo Mode)** to ensure instant reaction to manual buys.
- **Broker API**: Directly integrates with the broker API (mStock/Zerodha/Upstox).
- **Hard-Coded Priority**: This architecture bypasses all indicators (RSI, ADX, MACD, VWAP) as no automatic entries are made.

---
*Last Updated: 2026-05-16*
*Status: 100% SOUND-PROOFED*
