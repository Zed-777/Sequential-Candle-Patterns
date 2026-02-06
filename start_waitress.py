#!/usr/bin/env python
"""
Start the Dash dashboard using Waitress (Windows-compatible WSGI server).
Waitress is pure Python and works on all platforms including Windows.
"""
import os
import sys
import logging

# Set PYTHONPATH
os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print('Importing Dash dashboard...')
try:
    from candle_patterns.dashboard import server
    print('Dashboard imported successfully')
except Exception as e:
    print(f'Failed to import dashboard: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    try:
        from waitress import serve
    except ImportError:
        print('Waitress not installed. Installing...')
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'waitress'])
        from waitress import serve
    
    print('\nStarting Dash app on http://localhost:8050')
    print('Open your browser and navigate to: http://localhost:8050')
    print('Press Ctrl+C to stop\n')
    
    try:
        # Serve with Waitress
        # Set channel_timeout=0 to disable timeout, threads for concurrency
        serve(
            server, 
            host='127.0.0.1', 
            port=8050, 
            threads=4,
            channel_timeout=0
        )
    except KeyboardInterrupt:
        print('\nShutdown.')
        sys.exit(0)
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
