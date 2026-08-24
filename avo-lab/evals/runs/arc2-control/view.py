import sys

def load(p):
    rows = []
    for line in open(p):
        line = line.rstrip("\n")
        if len(line) == 64 and all(c in "0123456789abcdef" for c in line.lower()):
            rows.append(line)
    return rows

rows = load(sys.argv[1])
# Print with column ruler
print("    " + "".join(str((x // 10) % 10) if x % 5 == 0 else " " for x in range(64)))
print("    " + "".join(str(x % 10) if x % 5 == 0 else " " for x in range(64)))
for y, r in enumerate(rows):
    print(f"{y:3d} {r}")
# Special cell inventory
from collections import Counter
c = Counter(ch for r in rows for ch in r)
print("counts:", dict(sorted(c.items())))
