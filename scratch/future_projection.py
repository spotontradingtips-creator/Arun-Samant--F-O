import json
import csv
import pandas as pd
import glob
from datetime import datetime, time

INITIAL_CAPITAL = 35000

def load_data():
    all_trades = []
    seen_ids = set()
    
    # Load from all CSVs
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
                            
                            all_trades.append({
                                'date': dt.date(),
                                'time': dt.time(),
                                'pnl': float(row['P&L']),
                                'id': tid,
                                'pct': float(row.get('P&L_%', 0))
                            })
                            seen_ids.add(tid)
                        except: continue
        except: continue
    
    # Load from JSON
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
                            'time': dt.time(),
                            'pnl': float(t['pnl']),
                            'id': tid,
                            'pct': float(t.get('pnl_percentage', 0))
                        })
                        seen_ids.add(tid)
                    except: continue
    except: pass
    
    return all_trades

def projection_analysis(trades):
    df = pd.DataFrame(trades)
    
    # Clean anomalies (massive bugs)
    df = df[ (df['pnl'] < 20000) & (df['pnl'] > -10000) ]
    
    # 1. Identify "Preventable" losses
    m_start = time(9, 15)
    m_end = time(9, 30)
    
    # Morning Noise (9:15-9:30)
    morning_noise_trades = df[ (df['time'] >= m_start) & (df['time'] < m_end) ]
    noise_pnl = morning_noise_trades['pnl'].sum()
    
    # 2. Large 1st Trade Drawdowns (Now capped at 1500)
    daily_first_trades = df.sort_values(['date', 'time']).groupby('date').first().reset_index()
    excess_1st_drawdown = daily_first_trades[ daily_first_trades['pnl'] < -1500 ]['pnl'].apply(lambda x: x + 1500).sum()
    
    # 3. Overall Performance
    current_total_pnl = df['pnl'].sum()
    
    # Projected Total (Removing morning noise and capping 1st trade loss)
    # Note: Removing morning noise means we don't have those trades at all.
    # Note: Capping 1st trade means we add back the 'excess' loss.
    projected_cleanup = (current_total_pnl - noise_pnl) - excess_1st_drawdown 
    # Wait, excess_1st_drawdown is negative, so subtracting it adds it back.
    
    days = len(df['date'].unique())
    raw_daily_avg = (current_total_pnl / days) / INITIAL_CAPITAL * 100
    proj_daily_avg = (projected_cleanup / days) / INITIAL_CAPITAL * 100
    
    print(f"Total Trading Days: {days}")
    print(f"Historical Morning Noise Loss (9:15-9:30): Rs {noise_pnl:,.2f}")
    print(f"Historical Excess 1st Trade Drawdown: Rs {excess_1st_drawdown:,.2f}")
    print("-" * 30)
    print(f"Raw Avg Daily ROI: {raw_daily_avg:.2f}%")
    print(f"Projected Avg Daily ROI (with new fixes): {proj_daily_avg:.2f}%")
    print(f"Estimated Monthly Projection: {proj_daily_avg * 20:.2f}%")

if __name__ == "__main__":
    trades = load_data()
    projection_analysis(trades)
