import time
import urllib.request
for i in range(40):
    try:
        r = urllib.request.urlopen('http://127.0.0.1:8050', timeout=2)
        html = r.read().decode('utf-8')
        print('READY')
        open('page_after_restart.html','w',encoding='utf-8').write(html)
        break
    except Exception as e:
        print('waiting', i, e)
        time.sleep(0.5)
else:
    print('FAILED')
