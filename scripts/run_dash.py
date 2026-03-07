import sys
import os
os.environ['PYTHONPATH'] = 'src'
sys.path.insert(0, 'src')

try:
    from candle_patterns.dashboard import app
    print('[OK] Dashboard app imported successfully')
    print('[OK] Server object:', app.server)
    print('[OK] Running on port 8050 via app.run()')
    app.run(host='0.0.0.0', port=8050, debug=False, use_reloader=False)
except Exception as e:
    import traceback
    print('[ERROR]', e)
    traceback.print_exc()
    import sys
    sys.exit(1)
