from pathlib import Path
p=Path('PROJECT_PLAN.md')
b=p.read_bytes()
print('orig nulls',b.count(b'\x00'), 'len',len(b))
# try utf-16
try:
    text=b.decode('utf-16')
    print('decoded utf-16 OK')
except Exception as e:
    print('utf-16 failed',e)
    text=b.decode('utf-8',errors='replace')
# normalize and write
text=text.replace('\r\n','\n').replace('\r','\n')
# as an extra step, remove stray nulls
text=text.replace('\x00','')
# write
p.write_text(text,encoding='utf-8')
print('wrote cleaned PROJECT_PLAN.md, new len',p.stat().st_size)
