#!/usr/bin/env python
"""
Launch Dash dashboard and open browser automatically.
This works around the issue where server crashes on first non-browser HTTP request.
"""
import sys
import time
import webbrowser
import threading

sys.path.insert(0, 'src')

from candle_patterns.dashboard import app

def open_browser_after_delay():
    """Open browser in a separate thread after server has started."""
    time.sleep(3)  # Give server time to start
    print("\n→ Opening dashboard in your default browser...")
    webbrowser.open('http://localhost:8050')

if __name__ == '__main__':
    print("=" * 60)
    print("CANDLE PATTERNS DASHBOARD")
    print("=" * 60)
    print("\nStarting dashboard server...")
    print("→ Dashboard will open automatically in your browser")
    print("→ URL: http://localhost:8050")
    print("→ Press Ctrl+C to stop\n")
    
    # Start browser opener thread
    browser_thread = threading.Thread(target=open_browser_after_delay, daemon=True)
    browser_thread.start()
    
    # Run the Dash app with minimal dev tools
    try:
        app.run(
            host='0.0.0.0',
            port=8050,
            debug=False,
            dev_tools_ui=False,
            dev_tools_props_check=False,
            dev_tools_serve_dev_bundles=False,
            dev_tools_hot_reload=False,
        )
    except KeyboardInterrupt:
        print("\n\nShutdown.")
        sys.exit(0)
