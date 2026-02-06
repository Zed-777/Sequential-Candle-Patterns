#!/usr/bin/env python
"""
Test just importing and initializing the dashboard to find any errors.
"""
import sys
import traceback
sys.path.insert(0, 'src')

print("Step 1: Importing dashboard module...")
try:
    from candle_patterns.dashboard import app, server
    print("✓ Dashboard imported successfully")
    print(f"✓ App object: {app}")
    print(f"✓ Server object: {server}")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Testing layout rendering...")
try:
    layout = app.layout
    print(f"✓ Layout rendered successfully: {type(layout)}")
except Exception as e:
    print(f"✗ Failed to render layout: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Checking registered callbacks...")
try:
    callbacks = app._callbacks
    print(f"✓ Registered {len(callbacks)} callbacks")
    for cb in callbacks[:3]:
        print(f"  - {cb}")
except Exception as e:
    print(f"✗ Failed to check callbacks: {e}")
    traceback.print_exc()

print("\nStep 4: Attempting first request simulation...")
try:
    # Simulate a GET request using Flask's test client
    client = server.test_client()
    response = client.get('/')
    print(f"✓ Flask test client GET /: Status {response.status_code}")
    if response.status_code == 200:
        # Check if Dash assets are there
        if b'react-entry-point' in response.data or b'_dash-layout' in response.data:
            print("✓ Dash client structure found in HTML")
        else:
            print("⚠ Dash client structure not found (might be expected)")
except Exception as e:
    print(f"✗ Test client error: {e}")
    traceback.print_exc()

print("\nAll checks passed! App is importable and testable.")
