import sys
import os
os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

from candle_patterns.dashboard import app, server

with server.test_client() as client:
    response = client.get('/')
    html = response.get_data(as_text=True)
    
    # Check for key Dash/component IDs instead
    print('Checking for Dash component IDs:')
    print(f'  load-sample-btn: {"load-sample-btn" in html}')
    print(f'  candle-chart: {"candle-chart" in html}')
    print(f'  pattern-checklist: {"pattern-checklist" in html}')
    print(f'  tabs: {"tabs" in html}')
    print(f'  upload-data: {"upload-data" in html}')
    print()
    
    # Show first 2000 chars
    print('=== HTML (first 2000 chars) ===')
    print(html[:2000])
