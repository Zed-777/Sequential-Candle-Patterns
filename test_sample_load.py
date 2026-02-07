import sys
sys.path.insert(0, 'src')
import pandas as pd
from candle_patterns.detection import detect_patterns

# Simulate what load_sample_data does
sample_path = 'data/samples/sample_synthetic.csv'
df = pd.read_csv(sample_path)

# Convert timestamp
if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')

# Detect patterns
patterns = detect_patterns(df)
print(f'✅ Loaded {len(df)} rows, detected {len(patterns)} patterns')

# Create the data dict
data = {
    'filename': 'sample_synthetic.csv',
    'upload_id': None,
    'df': df.to_dict('records'),
    'patterns': patterns
}
print(f'✅ Data prepared: {len(data["df"])} records, {len(data["patterns"])} patterns')
print(f'✅ Sample record: {data["df"][0]}')
print(f'✅ Sample pattern: {data["patterns"][0]}')
