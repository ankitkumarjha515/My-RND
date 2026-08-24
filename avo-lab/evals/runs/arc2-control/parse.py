import sys

def load(p):
    rows, meta = [], {}
    for line in open(p):
        line = line.rstrip("\n")
        if len(line) == 64 and all(c in "0123456789abcdef" for c in line):
            rows.append(line)
        elif "=" in line:
            k, _, v = line.partition("=")
            meta[k] = v
    return rows, meta

rows, meta = load(sys.argv[1])
# find movable block: rows containing 'c'
tops = [y for y, r in enumerate(rows) if "c" in r]
if tops:
    t, b = min(tops), max(tops)
    xs = [x for y in range(t, b + 1) for x in range(64) if rows[y][x] == "c"]
    print(f"block rows {t}-{b} cols {min(xs)}-{max(xs)}")
bc = sum(r.count("b") for r in rows)
oc = sum(r.count("8") for r in rows)
nc = sum(r.count("9") for r in rows)
print(f"fuse_b={bc} lives_8={oc} nines={nc}")
print("meta:", meta.get("step"), meta.get("state"), meta.get("levels"))
