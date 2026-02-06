import sys
import os
import time
import threading

os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

print('Importing dashboard...')
from candle_patterns.dashboard import app, server

print('Starting Flask server with error capture...')
print('Navigate to http://localhost:8050')
print('Press Ctrl+C to stop\n')

# Run server in a way that catches and displays errors
try:
    server.run(
        host='0.0.0.0',
        port=8050,
        debug=False,
        use_reloader=False,
        threaded=True
    )
except KeyboardInterrupt:
    print('\nShutdown.')
    sys.exit(0)
except Exception as e:
    print(f'\n❌ ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
