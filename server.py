#!/usr/bin/env python
"""
Start the Dash dashboard.
This script configures the environment and starts the app properly.
"""
import os
import sys

# Set PYTHONPATH early
os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

print('Importing Dash dashboard...')
from candle_patterns.dashboard import app

if __name__ == '__main__':
    print('Starting Dash app on http://localhost:8050')
    print('Press Ctrl+C to stop\n')
    
    # Use app.run() with dev_tools_hot_reload disabled 
    # and use_reloader=False to avoid Werkzeug issues
    try:
        app.run(
            host='127.0.0.1',
            port=8050,
            debug=False,
            dev_tools_hot_reload=False
        )
    except KeyboardInterrupt:
        print('\nShutdown.')
        sys.exit(0)
