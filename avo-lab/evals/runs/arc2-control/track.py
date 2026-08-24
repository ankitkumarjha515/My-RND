import glob, re

for f in sorted(glob.glob("grids/s*.txt")):
    rows = [l.rstrip("\n") for l in open(f)
            if len(l.rstrip("\n")) == 64 and all(c in "0123456789abcdef" for c in l.rstrip("\n").lower())]
    cs = [(y, x) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "c"]
    step = "?"
    for l in open(f):
        m = re.match(r"step=(\d+)", l)
        if m:
            step = m.group(1)
            break
    if cs:
        ys = [p[0] for p in cs]
        xs = [p[1] for p in cs]
        print(f"{f}: step={step} player rows {min(ys)}-{max(ys)} cols {min(xs)}-{max(xs)}")
    else:
        print(f"{f}: step={step} NO PLAYER FOUND")
