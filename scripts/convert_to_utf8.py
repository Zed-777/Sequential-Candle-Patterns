from pathlib import Path
import shutil
import time
files=['PATTERN_CATALOG.md','progress_tracker.csv','PROJECT_PLAN.md']
root=Path('.').resolve()
for p in files:
    fp=root/p
    if not fp.exists():
        print('missing',p); continue
    bak=fp.with_suffix(fp.suffix+'.corrupt.bak')
    i=1
    while bak.exists():
        bak=fp.with_name(fp.stem+f'.corrupt.{i}.bak'+fp.suffix)
        i+=1
    print('backing up',fp,'->',bak)
    shutil.copy2(fp,bak)
    b=fp.read_bytes()
    text=None
    # Try utf-8 first
    try:
        text=b.decode('utf-8')
        print(p,'decoded as utf-8')
    except Exception:
        # try utf-16 (handles BOMs)
        try:
            text=b.decode('utf-16')
            print(p,'decoded as utf-16')
        except Exception as e:
            print('fallback decode',p,str(e))
            # as last resort, replace nulls and try utf-8 with errors
            text=b.replace(b'\x00',b'').decode('utf-8',errors='replace')
            print(p,'decoded with replacements')
    if text is None:
        print('could not decode',p)
        continue
    # normalize line endings
    text=text.replace('\r\n','\n').replace('\r','\n')
    # write back as utf-8
    fp.write_text(text,encoding='utf-8')
    print('wrote cleaned',p)
print('done')
