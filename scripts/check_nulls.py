from pathlib import Path
for p in ['PATTERN_CATALOG.md','progress_tracker.csv','PROJECT_PLAN.md']:
    fp=Path(p)
    b=fp.read_bytes()
    n=b.count(b'\x00')
    print(p,'nulls=',n,'size=',len(b))
    if n>0:
        idx=b.find(b'\x00')
        start=max(0,idx-30)
        end=min(len(b),idx+30)
        print(p,'snippet bytes:',b[start:end])
