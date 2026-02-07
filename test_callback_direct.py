import sys
sys.path.insert(0, 'src')

from candle_patterns.dashboard import load_sample_data

print("="*60)
print("Testing load_sample_data callback directly")
print("="*60)

try:
    # Simulate 1 click
    result = load_sample_data(1)
    print(f"\n✅ Callback executed successfully!")
    print(f"Returned {len(result)} outputs")
    
    data, msg = result
    print(f"Message: {msg}")
    
    if data:
        print(f"Data keys: {data.keys()}")
        print(f"Data['df'] records: {len(data['df'])}")
        print(f"Data['patterns']: {len(data['patterns'])}")
    else:
        print("❌ Data is None!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
