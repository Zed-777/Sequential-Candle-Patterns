#!/usr/bin/env python
"""
Run Dash with all dev tools disabled to prevent crashes.
"""
import sys
sys.path.insert(0, 'src')

from candle_patterns.dashboard import app

print("Starting Dash app with all dev tools disabled...")
print("Open your browser to: http://localhost:8050")
print("Press Ctrl+C to stop\n")

if __name__ == '__main__':
    # Disable all dev/debug features that might cause issues on Python 3.14
    app.run(
        host='0.0.0.0',
        port=8050,
        debug=False,
        dev_tools_ui=False,          # Disable debug panel
        dev_tools_props_check=False,  # Disable prop type checking
        dev_tools_serve_dev_bundles=False,  # Don't serve hot reload bundles
        dev_tools_hot_reload=False,   # Disable hot reload
    )
