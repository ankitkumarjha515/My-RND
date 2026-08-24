import sys

def load(p):
    rows = []
    meta = {}
    for line in open(p):
        line = line.rstrip("\n")
        if len(line) == 64 and all(c in "0123456789abcdef" for c in line):
            rows.append(line)
        elif "=" in line:
            k, _, v = line.partition("=")
            meta[k] = v
    return rows, meta

a, ma = load(sys.argv[1])
b, mb = load(sys.argv[2])
for y in range(min(len(a), len(b))):
    if a[y] != b[y]:
        xs = [x for x in range(64) if a[y][x] != b[y][x]]
        print(f"row {y}: cols {min(xs)}-{max(xs)} ({len(xs)} cells)")
        print("  before:", "".join(a[y][x] for x in range(min(xs), max(xs)+1)))
        print("  after :", "".join(b[y][x] for x in range(min(xs), max(xs)+1)))
print("meta before:", {k: v for k, v in ma.items() if k in ("step", "state", "levels")})
print("meta after :", {k: v for k, v in mb.items() if k in ("step", "state", "levels")})
