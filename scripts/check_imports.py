import sys
import os

print("cwd=", os.getcwd())
SRC = os.path.join(os.getcwd(), "src")
print("exists src", os.path.exists(SRC))
if SRC not in sys.path:
    sys.path.insert(0, SRC)
print("sys.path[0]=", sys.path[0])
try:
    import candle_patterns

    print("candle_patterns loaded from", candle_patterns.__file__)
except Exception as e:
    print("import error", type(e), e)

# check for nulls in test files
for root, _, files in os.walk("tests"):
    for fn in files:
        if fn.endswith(".py"):
            path = os.path.join(root, fn)
            with open(path, "rb") as f:
                data = f.read()
                print(path, "len", len(data), "has_null", b"\x00" in data)
