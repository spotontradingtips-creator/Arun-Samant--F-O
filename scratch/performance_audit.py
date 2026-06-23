import json
import csv
import pandas as pd
import glob
import os
from datetime import datetime

INITIAL_CAPITAL = 35000

# Constants for anomaly detection
MAX_POSSIBLE_TRADE_PERCENT = 500.0  
MIN_POSSIBLE_TRADE_PERCENT = -100.0 

def load_data():
    all_trades = []
    seen_ids = set()

    # 1. Load from all CSV snapshots in logs
    csv_pattern = r'c:\Antigravity\Arun Samant - F&O\logs\live_trades_*.csv'
    for csv_file in glob.glob(csv_pattern):
        try:
            with open(csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tid = row.get('Position_ID') or row.get('id')
                    if tid and tid not in seen_ids:
                        try:
                            entry_time = row['Entry_Time']
                            try:
                                dt = datetime.fromisoformat(entry_time)
                            except:
                                dt = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S.%f%z')
                            
                            pnl = float(row['P&L'])
                            log_pct = float(row.get('P&L_%', 0))
                            
                            all_trades.append({
                                'date': dt.date(),
                                'pnl': pnl,
                                'id': tid,
                                'log_pct': log_pct,
                                'reason': row.get('Exit_Reason', '')
                            })
                            seen_ids.add(tid)
                        except:
                            continue
        except Exception:
            continue

    # 2. Load from JSON history
    json_file = r'c:\Antigravity\Arun Samant - F&O\data\daily_history.json'
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for t in data:
                tid = t.get('position_id')
                if tid and tid not in seen_ids:
                    try:
                        dt = datetime.fromisoformat(t['entry_time'])
                        all_trades.append({
                            'date': dt.date(),
                            'pnl': float(t['pnl']),
                            'id': tid,
                            'log_pct': float(t.get('pnl_percentage', 0)),
                            'reason': t.get('exit_reason', '')
                        })
                        seen_ids.add(tid)
                    except:
                        continue
    except FileNotFoundError:
        pass

    # 3. Load from portfolio_full_analysis.csv
    pfa_file = r'c:\Antigravity\Arun Samant - F&O\logs\portfolio_full_analysis.csv'
    try:
        with open(pfa_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    pnl = float(row['pnl'])
                    date_str = row['date']
                    symbol = row['symbol']
                    signature = f"{date_str}_{symbol}_{pnl}"
                    if signature not in seen_ids:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                        all_trades.append({
                            'date': dt.date(),
                            'pnl': pnl,
                            'id': signature,
                            'log_pct': 0, # Not available in this file
                            'reason': 'Historical'
                        })
                        seen_ids.add(signature)
                except:
                    continue
    except FileNotFoundError:
        pass

    return all_trades

def analyze_performance(trades):
    if not trades:
        print("No trades found to analyze.")
        return

    df = pd.DataFrame(trades)
    
    # ---------------------------------------------------------
    # ANOMALY DETECTION & CLEANING
    # ---------------------------------------------------------
    # Filtering trades that are mathematically impossible for buying options on 35k capital
    # 1. P&L > Rs 20,000 (More than 50% capital in one trade)
    # 2. P&L < Rs -10,000 (More than 30% capital in one trade, should be stopped by SL)
    # 3. Log P&L% > 500% or < -100%
    df['is_anomaly'] = (df['pnl'] > 20000) | (df['pnl'] < -10000) | (df['log_pct'] > 500) | (df['log_pct'] < -101)
    
    anomalies = df[df['is_anomaly']]
    clean_df = df[~df['is_anomaly']]
    
    def summarize(data_df):
        if data_df.empty: return pd.DataFrame()
        daily = data_df.groupby('date')['pnl'].agg(['sum', 'count']).reset_index()
        daily.columns = ['date', 'daily_pnl', 'trade_count']
        daily['daily_percent'] = (daily['daily_pnl'] / INITIAL_CAPITAL) * 100
        daily['date_dt'] = pd.to_datetime(daily['date'])
        return daily.sort_values('date')

    clean_daily = summarize(clean_df)
    
    # Metrics on CLEAN data
    total_days = len(clean_daily)
    winning_days_df = clean_daily[clean_daily['daily_pnl'] > 0]
    losing_days_df = clean_daily[clean_daily['daily_pnl'] < 0]
    
    win_rate_days = (len(winning_days_df) / total_days * 100) if total_days > 0 else 0
    avg_return_on_wins = winning_days_df['daily_percent'].mean() if not winning_days_df.empty else 0
    avg_return_daily = clean_daily['daily_percent'].mean()
    
    # Weekly Analysis (Clean)
    clean_daily['week_id'] = clean_daily['date_dt'].dt.year.astype(str) + "-" + clean_daily['date_dt'].dt.isocalendar().week.astype(str).str.zfill(2)
    weekly_summary = clean_daily.groupby('week_id')['daily_pnl'].sum().reset_index()
    weekly_summary['weekly_percent'] = (weekly_summary['daily_pnl'] / INITIAL_CAPITAL) * 100
    avg_return_weekly = weekly_summary['weekly_percent'].mean()
    
    # Monthly Analysis (Clean)
    clean_daily['month_id'] = clean_daily['date_dt'].dt.year.astype(str) + "-" + clean_daily['date_dt'].dt.month.astype(str).str.zfill(2)
    monthly_summary = clean_daily.groupby('month_id')['daily_pnl'].sum().reset_index()
    monthly_summary['monthly_percent'] = (monthly_summary['daily_pnl'] / INITIAL_CAPITAL) * 100
    avg_return_monthly = monthly_summary['monthly_percent'].mean()
    
    # OUTPUT
    print("\n" + "="*60)
    print("   CLEANED BOT PERFORMANCE REPORT (Filtering Bugs)")
    print("="*60)
    print(f"Total Trading Days    : {total_days}")
    print(f"Daily Win Rate        : {win_rate_days:.2f}%")
    print(f"Winning Days          : {len(winning_days_df)}")
    print(f"Losing Days           : {len(losing_days_df)}")
    print("-" * 60)
    print(f"Avg Daily Return (%)  : {avg_return_daily:+.2f}%")
    print(f"Avg Return on Winners : {avg_return_on_wins:+.2f}%")
    print(f"Avg Weekly Return (%) : {avg_return_weekly:+.2f}%")
    print(f"Avg Monthly Return (%): {avg_return_monthly:+.2f}%")
    print("-" * 60)
    print(f"Anomalies Filtered    : {len(anomalies)} (Data bugs/Sync errors)")
    print("="*60)
    
    print("\nRECENT CLEAN DAILY BREAKDOWN")
    recent = clean_daily.tail(15)
    print(f"{'Date':<12} | {'Return %':<10} | {'Trades':<6} | {'Status'}")
    print("-" * 55)
    for _, row in recent.iterrows():
        status = "WIN" if row['daily_pnl'] > 0 else "LOSS" if row['daily_pnl'] < 0 else "B/E"
        print(f"{row['date_dt'].strftime('%Y-%m-%d'):<12} | {row['daily_percent']:>+9.2f}% | {row['trade_count']:>6} | {status}")

    print("\nCLEANED MONTHLY SUMMARY")
    print(f"{'Month':<15} | {'Return %':<10} | {'P&L (Rs)'}")
    print("-" * 55)
    for _, row in monthly_summary.iterrows():
        year, m = row['month_id'].split('-')
        month_name = datetime(int(year), int(m), 1).strftime('%B %Y')
        print(f"{month_name:<15} | {row['monthly_percent']:>+9.2f}% | Rs {row['daily_pnl']:,.2f}")

    if len(anomalies) > 0:
        print("\nEXCLUDED ANOMALIES (Likely Logging/Sync Errors)")
        print(f"{'Date':<12} | {'P&L (Rs)':<12} | {'Reason'}")
        print("-" * 55)
        for _, row in anomalies.iterrows():
            print(f"{str(row['date']):<12} | {row['pnl']:>12,.2f} | {row['reason']}")

if __name__ == "__main__":
    trades = load_data()
    analyze_performance(trades)
