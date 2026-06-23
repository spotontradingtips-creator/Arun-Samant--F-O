import os
import glob
import pandas as pd
import json

# 1. Load CSV trades
csv_files = glob.glob("logs/live_trades_*.csv")
dfs = []
for f in csv_files:
    try:
        df = pd.read_csv(f)
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {f}: {e}")

if dfs:
    csv_df = pd.concat(dfs, ignore_index=True)
    # Ensure column names match for merging
    # CSV columns: Position_ID,Underlying,Type,Entry_Time,Entry_Price,Entry_Spot,SL_Percentage,Exit_Time,Exit_Price,Exit_Spot,Exit_Reason,P&L,P&L_%,VIX
    csv_df = csv_df[['Position_ID', 'Underlying', 'Entry_Time', 'Exit_Time', 'P&L', 'P&L_%', 'Exit_Reason']]
    csv_df.rename(columns={'Underlying': 'underlying', 'Entry_Time': 'entry_time', 'Exit_Time': 'exit_time', 'P&L': 'pnl'}, inplace=True)
else:
    csv_df = pd.DataFrame()

# 2. Load JSON history
json_data = []
if os.path.exists("data/daily_history.json"):
    with open("data/daily_history.json", "r") as f:
        try:
            trades = json.load(f)
            for t in trades:
                json_data.append({
                    'Position_ID': t.get('position_id'),
                    'underlying': t.get('underlying'),
                    'entry_time': t.get('entry_time'),
                    'exit_time': t.get('exit_time'),
                    'pnl': t.get('pnl', 0.0),
                    'P&L_%': t.get('pnl_percentage', 0.0),
                    'Exit_Reason': t.get('exit_reason')
                })
        except Exception as e:
            print(f"Error reading JSON: {e}")

json_df = pd.DataFrame(json_data)

# Combine and deduplicate
all_trades = pd.concat([csv_df, json_df], ignore_index=True)
if not all_trades.empty:
    all_trades.drop_duplicates(subset=['Position_ID'], keep='last', inplace=True)

# 3. Analyze
all_trades['entry_time'] = pd.to_datetime(all_trades['entry_time'], format='mixed')
all_trades['Month'] = all_trades['entry_time'].dt.strftime('%Y-%m')

print(f"TOTAL TRADES FOUND: {len(all_trades)}")

# Monthly Analysis
monthly_stats = all_trades.groupby('Month').agg(
    total_trades=('Position_ID', 'count'),
    wins=('pnl', lambda x: (x > 0).sum()),
    losses=('pnl', lambda x: (x < 0).sum()),
    total_pnl=('pnl', 'sum'),
    best_trade=('pnl', 'max'),
    worst_trade=('pnl', 'min')
).reset_index()

print("\n--- MONTHLY BREAKDOWN ---")
for _, row in monthly_stats.iterrows():
    win_rate = (row['wins'] / row['total_trades'] * 100) if row['total_trades'] > 0 else 0
    print(f"Month: {row['Month']} | Trades: {row['total_trades']} | Win Rate: {win_rate:.1f}% | P&L: Rs {row['total_pnl']:,.2f} | Best: Rs {row['best_trade']:,.2f} | Worst: Rs {row['worst_trade']:,.2f}")

# Overall Stats
total_trades = len(all_trades)
total_pnl = all_trades['pnl'].sum()
wins = (all_trades['pnl'] > 0).sum()
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
best_trade = all_trades['pnl'].max()
worst_trade = all_trades['pnl'].min()

print("\n--- OVERALL 5-MONTH SUMMARY ---")
print(f"Total Trades: {total_trades}")
print(f"Total Win Rate: {win_rate:.1f}%")
print(f"Total P&L: Rs {total_pnl:,.2f}")
print(f"Best Trade: Rs {best_trade:,.2f}")
print(f"Worst Trade: Rs {worst_trade:,.2f}")

# Index breakdown
print("\n--- PERFORMANCE BY INDEX ---")
idx_stats = all_trades.groupby('underlying').agg(
    total_trades=('Position_ID', 'count'),
    wins=('pnl', lambda x: (x > 0).sum()),
    total_pnl=('pnl', 'sum')
)
for index, row in idx_stats.iterrows():
    win_rate = (row['wins'] / row['total_trades'] * 100) if row['total_trades'] > 0 else 0
    print(f"{index}: {row['total_trades']} trades | Win Rate: {win_rate:.1f}% | P&L: Rs {row['total_pnl']:,.2f}")

