import os
import sys

os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

from candle_patterns.dashboard import app, server

if __name__ == '__main__':
    # Use Flask dev server with explicit error handling for Windows
    try:
        app.run(host='0.0.0.0', port=8050, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print('\nShutdown requested.')
    except Exception as e:
        print(f'Server error: {e}')
        import traceback
        traceback.print_exc()
