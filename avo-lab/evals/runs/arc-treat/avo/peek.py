import sys
p = sys.argv[1]
rows = [ln.rstrip("\n") for ln in open(p, encoding="utf-8")
        if len(ln.rstrip("\n")) >= 64 and all(c in "0123456789abcdef" for c in ln.rstrip("\n"))]

def show(y0, y1, x0, x1, label):
    print(f"--- {label} rows {y0}-{y1} cols {x0}-{x1}")
    for y in range(y0, y1 + 1):
        print(f"{y:2d} {rows[y][x0:x1+1]}")

show(39, 46, 24, 48, "around assembly")   # assembly now cols 39-43 rows 40-44
show(29, 36, 14, 28, "avatar area")
