import sys

def grid(p):
    ls = [l.rstrip("\n") for l in open(p, encoding="utf-8")]
    return [l for l in ls if len(l) == 64 and all(ch in "0123456789abcdef" for ch in l)]

def main():
    g = grid(sys.argv[1])
    print(f"{sys.argv[1]}: {len(g)}x{len(g[0])}")
    # find avatar (c cells)
    av = [(r, c) for r, row in enumerate(g) for c, ch in enumerate(row) if ch == "c"]
    if av:
        rs = sorted(set(r for r, c in av)); cs = sorted(set(c for r, c in av))
        print(f"avatar rows {rs[0]}-{rs[-1]} cols {cs[0]}-{cs[-1]}")
    bs = sum(row.count("b") for row in g)
    print(f"fuel b remaining: {bs}")
    # optional window print: r0 r1 c0 c1
    if len(sys.argv) >= 6:
        r0, r1, c0, c1 = map(int, sys.argv[2:6])
        hdr = "    " + "".join(str(c // 10 % 10) for c in range(c0, c1 + 1))
        hdr2 = "    " + "".join(str(c % 10) for c in range(c0, c1 + 1))
        print(hdr); print(hdr2)
        for r in range(max(0, r0), min(len(g), r1 + 1)):
            print(f"r{r:02d} {g[r][c0:c1+1]}")

main()
