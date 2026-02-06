#!/usr/bin/env python
"""
Comprehensive test to verify Load Sample Data button functionality.
"""
import sys
sys.path.insert(0, 'src')

import json
from pathlib import Path
from candle_patterns.dashboard import app, server

print("=" * 70)
print("BUTTON CALLBACK TEST")
print("=" * 70)

# Test 1: Verify app imports
print("\n✓ Test 1: App imports successfully")

# Test 2: Verify callback is registered
print("✓ Test 2: Checking registered callbacks...")
try:
    # Get the app's callback function
    from candle_patterns.dashboard import load_sample_data
    print("  ✓ load_sample_data callback found")
except Exception as e:
    print(f"  ✗ Callback not found: {e}")

# Test 3: Check layout for button
print("\n✓ Test 3: Checking dashboard layout...")
client = server.test_client()
response = client.get('/')
html = response.data.decode()

checks = {
    'load-sample-btn': 'Button ID present',
    'Load sample data': 'Button text present',
    'candle-chart': 'Chart div present',
    'pattern-checklist': 'Pattern checklist present',
    'history-select': 'History dropdown present',
}

for check_str, check_name in checks.items():
    if check_str in html:
        print(f"  ✓ {check_name}")
    else:
        print(f"  ✗ {check_name} - NOT FOUND!")

# Test 4: Simulate button click via callback directly
print("\n✓ Test 4: Testing callback directly (simulate click)...")
try:
    # The callback expects n_clicks value
    # When button is clicked in browser, n_clicks is incremented
    result = load_sample_data(1)  # n_clicks = 1
    
    if result and len(result) == 2:
        data, msg = result
        if data:
            print(f"  ✓ Callback returned data")
            print(f"  ✓ Message: {msg}")
            if 'df' in data and data['df']:
                print(f"  ✓ Data contains {len(data['df'])} records")
            if 'patterns' in data:
                print(f"  ✓ Data contains {len(data['patterns'])} detected patterns")
        else:
            print(f"  ✗ Callback returned None for data")
    else:
        print(f"  ✗ Callback returned unexpected format: {result}")
except Exception as e:
    print(f"  ✗ Callback error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test callback with n_clicks = 0 (should return None)
print("\n✓ Test 5: Testing callback with n_clicks=None (initial state)...")
try:
    result = load_sample_data(None)
    if result == (None, ""):
        print("  ✓ Correctly returns None for initial state")
    else:
        print(f"  ✗ Unexpected result: {result}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 6: Check if sample file generation works
print("\n✓ Test 6: Testing synthetic sample generation...")
try:
    sample_path = Path("data/samples/sample_synthetic.csv")
    if sample_path.exists():
        print(f"  ✓ Sample file exists: {sample_path}")
    else:
        print(f"  ⚠ Sample file will be generated on button click")
        print(f"  → Location: {sample_path}")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("BUTTON TEST COMPLETE")
print("=" * 70)
print("\nNEXT STEPS:")
print("1. Refresh browser at http://localhost:8050")
print("2. Click the 'Load sample data' button")
print("3. Check browser console (F12) for errors")
print("4. Check terminal for callback logs")
print("5. Verify chart populates with candlestick data")
print("=" * 70)
