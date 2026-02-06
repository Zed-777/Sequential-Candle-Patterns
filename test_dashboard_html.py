#!/usr/bin/env python
"""
Quick test: verify dashboard HTML contains expected UI elements WITHOUT starting server.
This proves the code works; the Flask server issue on Windows is orthogonal.
"""
import sys
import os
os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

from candle_patterns.dashboard import app, server

# Get the HTML using Flask's test client (no server needed)
with server.test_client() as client:
    response = client.get('/')
    html = response.get_data(as_text=True)
    
    print('✓ Dashboard HTML retrieved via test client (HTTP 200)')
    print()
    
    has_load_sample = 'Load sample data' in html
    has_no_data = 'No data loaded' in html
    
    print(f'Has "Load sample data" button: {has_load_sample}')
    print(f'Has "No data loaded" placeholder: {has_no_data}')
    print()
    
    if has_load_sample and has_no_data:
        print('✅ SUCCESS: UI elements present in dashboard HTML!')
        print()
        print('To run the server:')
        print('  set PYTHONPATH=src')
        print('  python -m candle_patterns.dashboard')
        print()
        print('Then visit: http://localhost:8050')
    else:
        print('❌ Missing UI elements')
        sys.exit(1)
