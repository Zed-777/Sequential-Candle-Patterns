"""Test: Can we manually invoke the load_sample_data callback?"""
import sys
sys.path.insert(0, 'src')

print("Attempting to import and test the callback directly...\n")

try:
    from candle_patterns.dashboard import load_sample_data
    print("✅ Successfully imported load_sample_data function")
    
    # Try calling it with n_clicks=1
    print("\nCalling load_sample_data(n_clicks=1)...")
    result = load_sample_data(1)
    
    data, msg = result
    print(f"\n✅ Callback executed successfully!")
    print(f"   Message: {msg}")
    
    if data:
        print(f"   Data keys: {list(data.keys())}")
        print(f"   DataFrame rows: {len(data['df'])}")
        print(f"   Patterns detected: {len(data['patterns'])}")
    else:
        print(f"   ❌ Data is empty!")
        
except ImportError as e:
    print(f"❌ Cannot import: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
