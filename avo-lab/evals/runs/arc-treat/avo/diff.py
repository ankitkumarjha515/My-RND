import sys

def load(p):
    rows = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if len(ln) >= 64 and all(c in "0123456789abcdef" for c in ln):
            rows.append(ln)
    return rows

a, b = load(sys.argv[1]), load(sys.argv[2])
print(f"rows: {len(a)} vs {len(b)}")
n = min(len(a), len(b))
for y in range(n):
    if a[y] != b[y]:
        for x in range(64):
            if a[y][x] != b[y][x]:
                print(f"  ({x},{y}) '{a[y][x]}' -> '{b[y][x]}'")
