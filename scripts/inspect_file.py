import sys

path = sys.argv[1]
with open(path, "rb") as f:
    data = f.read()
print("len", len(data))
print("first100", data[:100])
print("last100", data[-100:])
print("has_null", b"\x00" in data)
