import os,sys
root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ignore_dirs=set(['.git','.venv','.pytest_cache','.ruff_cache','.ipynb_checkpoints','env','venv','__pycache__'])
large=[]
bad_encoding=[]
for dirpath,dirs,files in os.walk(root):
    rel=os.path.relpath(dirpath, root)
    if rel=='.': rel_parts=[]
    else: rel_parts=rel.split(os.sep)
    if any(p in ignore_dirs for p in rel_parts):
        continue
    for f in files:
        fp=os.path.join(dirpath,f)
        try:
            size=os.path.getsize(fp)
        except OSError:
            continue
        if size>1024*1024:
            large.append((os.path.relpath(fp,root),size))
        try:
            with open(fp,'rb') as fh:
                content=fh.read()
            if b'\x00' in content[:1024*64]:
                bad_encoding.append((os.path.relpath(fp,root),'NULL_BYTE'))
            else:
                try:
                    content.decode('utf-8')
                except Exception as e:
                    bad_encoding.append((os.path.relpath(fp,root),str(e)))
        except Exception as e:
            bad_encoding.append((os.path.relpath(fp,root),str(e)))

print('LARGE_FILES_START')
for p,s in sorted(large,key=lambda x:-x[1]):
    print(p,s)
print('LARGE_FILES_END')
print('BAD_ENCODING_START')
for p,msg in bad_encoding:
    print(p,msg)
print('BAD_ENCODING_END')
