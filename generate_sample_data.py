import pandas as pd
import numpy as np
from datetime import datetime

# Generate 200 days of Bitcoin data (daily candles)
np.random.seed(42)  # For reproducibility
end_date = datetime(2025, 8, 22)
dates = pd.date_range(end=end_date, periods=200, freq='D')

# Realistic BTC price movement
base_price = 42000
drift = 0.0003
volatility = 0.025

prices = [base_price]
for _ in range(199):
    daily_return = drift + volatility * np.random.randn()
    new_price = prices[-1] * (1 + daily_return)
    prices.append(new_price)

prices = np.array(prices)

# Generate OHLC data
data = []
for i, date in enumerate(dates):
    close = prices[i]
    open_price = close + np.random.randn() * 300
    high = max(open_price, close) + abs(np.random.randn() * 500)
    low = min(open_price, close) - abs(np.random.randn() * 500)
    
    data.append({
        'timestamp': date.strftime('%Y-%m-%d 00:00:00'),
        'open': round(open_price, 2),
        'high': round(high, 2),
        'low': round(low, 2),
        'close': round(close, 2)
    })

df = pd.DataFrame(data)
df.to_csv('data/samples/sample_synthetic.csv', index=False)

print(f'✅ Created sample BTC data: {len(df)} days')
print(f'Date range: {df.iloc[0]["timestamp"]} to {df.iloc[-1]["timestamp"]}')
print(f'Price range: ${df["low"].min():.2f} - ${df["high"].max():.2f}')
print(f'\nFirst 3 rows:')
print(df.head(3))
print(f'\nLast 3 rows:')
print(df.tail(3))
