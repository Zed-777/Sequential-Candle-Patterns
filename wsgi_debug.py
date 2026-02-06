import os
import sys
import logging

os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

# Enable detailed logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

print('Step 1: Importing dashboard...')
try:
    from candle_patterns.dashboard import app
    print('✓ Dashboard imported')
except Exception as e:
    print(f'✗ Import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('Step 2: Starting server...')
try:
    print('Server binding to 0.0.0.0:8050 (use_reloader=False, threaded=True)')
    app.run(
        host='0.0.0.0',
        port=8050,
        debug=False,
        use_reloader=False,
        threaded=True
    )
except KeyboardInterrupt:
    print('\nShutdown requested.')
except Exception as e:
    print(f'✗ Server error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
