import urllib.request
url='http://127.0.0.1:8050'
try:
    r=urllib.request.urlopen(url, timeout=5)
    html=r.read().decode('utf-8')
    print('LENGTH', len(html))
    print('HAS_CLEANUP', 'cleanup-btn' in html)
    print('HAS_NAV', 'Candle Patterns' in html)
    print('\n--- HTML SNIPPET ---\n')
    print(html[:1200])
except Exception as e:
    print('ERR', e)
