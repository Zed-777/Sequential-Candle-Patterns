#!/usr/bin/env python
"""
Simple direct test of Dash app without WSGI complexity.
"""
import sys
sys.path.insert(0, 'src')

from candle_patterns.dashboard import app

print("Starting Dash app directly...")
print("Open your browser to: http://localhost:8050")
print("Press Ctrl+C to stop\n")

if __name__ == '__main__':
    # Try with minimal config, all dev tools disabled
    app.run(
        host='0.0.0.0',
        port=8050,
        debug=False,
        dev_tools_ui=False,
        dev_tools_props_check=False,
        dev_tools_serve_dev_bundles=False,
        dev_tools_hot_reload=False,
    )
