import pandas as pd

def analyze_points():
    df = pd.read_excel('PNL.xlsx', skiprows=17)
    df = df.dropna(subset=['Contract Name', 'Buy Date'])
    
    # Calculate points captured
    df['Points Captured'] = df['Sell Rate'] - df['Buy Rate']
    
    # Nifty options have qty 65 (mostly), HDFC had 550.
    # The user is asking for points they sold at.
    
    points = df['Points Captured'].round(1) # round to 1 decimal for grouping
    
    avg_points = points.mean()
    median_points = points.median()
    
    # Let's count frequencies using bins or direct rounded values
    rounded_ints = points.round(0).astype(int)
    mode_points = rounded_ints.mode().tolist()
    freq = rounded_ints.value_counts().sort_index()
    
    with open('scratch/points_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total Trades Analyzed: {len(df)}\n")
        f.write(f"Average Points Captured: {avg_points:.2f}\n")
        f.write(f"Median Points Captured: {median_points:.2f}\n")
        f.write(f"Most Frequent Points Captured (Rounded to whole numbers): {mode_points}\n\n")
        f.write("Frequency Distribution (Rounded Points -> Number of Trades):\n")
        for pts, count in freq.items():
            f.write(f"  {pts} points: {count} times\n")
            
        f.write("\nDetailed Breakdown:\n")
        for _, row in df.iterrows():
            f.write(f"{row['Contract Name']} | Buy: {row['Buy Rate']:.2f} | Sell: {row['Sell Rate']:.2f} | Points: {(row['Sell Rate'] - row['Buy Rate']):.2f}\n")

if __name__ == '__main__':
    analyze_points()
