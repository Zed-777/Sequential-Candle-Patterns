import time
import urllib.request
import sys

time.sleep(1)
try:
    resp = urllib.request.urlopen('http://127.0.0.1:8050')
    html = resp.read().decode('utf-8')
    print('HTTP 200 OK - page retrieved')
    print('Has "Load sample data":', 'Load sample data' in html)
    print('Has "No data loaded":', 'No data loaded' in html)
    print('\n=== First 1500 chars of HTML ===')
    print(html[:1500])
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
