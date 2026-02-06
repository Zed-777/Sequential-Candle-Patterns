import pandas as pd
import numpy as np
from pathlib import Path

# Test sample data generation
dates = pd.date_range(end=pd.Timestamp.now('UTC'), periods=200, freq='1h')
price = 20000 + np.cumsum(np.random.randn(len(dates)) * 50)
open_p = price + np.random.randn(len(dates)) * 5
close_p = price + np.random.randn(len(dates)) * 5
high_p = np.maximum(open_p, close_p) + np.abs(np.random.randn(len(dates)) * 10)
low_p = np.minimum(open_p, close_p) - np.abs(np.random.randn(len(dates)) * 10)

sdf = pd.DataFrame({
    'timestamp': dates.astype(str),
    'open': open_p,
    'high': high_p,
    'low': low_p,
    'close': close_p
})

sample_path = Path('data/samples/sample_synthetic.csv')
sample_path.parent.mkdir(parents=True, exist_ok=True)
sdf.to_csv(sample_path, index=False)

min_price = sdf['open'].min()
max_price = sdf['high'].max()
print(f'Sample data generated: {sample_path}')
print(f'  - Rows: {len(sdf)}')
print(f'  - Columns: {list(sdf.columns)}')
print(f'  - Price range: {min_price:.2f} - {max_price:.2f}')
