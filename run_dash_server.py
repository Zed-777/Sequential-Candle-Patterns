#!/usr/bin/env python
"""
Dash server launcher for Windows.
Avoids Werkzeug reloader issues by using WERKZEUG_RUN_MAIN env var.
"""
import os
import sys

# Set environment before importing anything
os.environ['PYTHONPATH'] = 'src'
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

sys.path.insert(0, 'src')

from candle_patterns.dashboard import server

if __name__ == '__main__':
    print('Starting Dash server on http://localhost:8050')
    print('Press Ctrl+C to stop\n')
    
    try:
        # Use the Flask server directly with minimal options
        server.run(
            host='0.0.0.0',
            port=8050,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print('\nShutdown requested.')
        sys.exit(0)
    except Exception as e:
        print(f'Server error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
