import pandas as pd

def analyze():
    # Read excel skipping the first 17 rows
    df = pd.read_excel('PNL.xlsx', skiprows=17)
    df = df.dropna(subset=['Contract Name', 'Buy Date'])
    
    total_trades = len(df)
    winning_trades = df[df['Net Realized P / L'] > 0]
    losing_trades = df[df['Net Realized P / L'] <= 0]
    
    win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
    total_profit_4_days = df['Net Realized P / L'].sum()
    
    today_profit = 2551
    total_profit_week = total_profit_4_days + today_profit
    
    capital = 28000
    roi = (total_profit_week / capital) * 100
    
    with open('scratch/pnl_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total Trades in File: {total_trades}\n")
        f.write(f"Win Rate (4 days): {win_rate:.2f}% ({len(winning_trades)} Wins / {len(losing_trades)} Losses)\n")
        f.write(f"Profit (4 days): Rs {total_profit_4_days:.2f}\n")
        f.write(f"Profit (5 days inc today): Rs {total_profit_week:.2f}\n")
        f.write(f"ROI on 28k for the week: {roi:.2f}%\n")
        
        f.write("\n--- TRADES ANALYSIS ---\n")
        for _, row in df.iterrows():
            contract = row['Contract Name']
            buy_date = row['Buy Date']
            pnl = row['Net Realized P / L']
            qty = row['Qty']
            buy_rate = row['Buy Rate']
            sell_rate = row['Sell Rate']
            f.write(f"{buy_date}: {contract} | Qty: {qty} | Buy: {buy_rate:.2f} | Sell: {sell_rate:.2f} | PnL: {pnl:.2f}\n")

if __name__ == '__main__':
    analyze()
