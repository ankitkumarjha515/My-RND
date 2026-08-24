import sys
sys.path.insert(0, "avo")
from collections import deque

def grid(p):
    ls = [l.rstrip("\n") for l in open(p, encoding="utf-8")]
    return [list(l) for l in ls if len(l) == 64 and all(ch in "0123456789abcdef" for ch in l)]

def erase_avatar(g):
    for r in range(64):
        for c in range(64):
            if g[r][c] == "c":
                g[r][c] = "3"
            elif g[r][c] == "9":
                # careful: only avatar 9s are at rows top+2..top+4; erase only contiguous with c-region above
                pass
    return g

def build(state):
    # start from s0018 (verified base config, avatar on glyph -> erase avatar overlay first)
    g = grid("avo/s0018.txt")
    for r in range(28, 36):
        for c in range(17, 26):
            if g[r][c] in ("c", "9"):
                g[r][c] = "3"
    if "A" in state:  # T1: r57-58 c3-4 <-> c7-8
        for r in (57, 58):
            g[r][3], g[r][7] = g[r][7], g[r][3]
            g[r][4], g[r][8] = g[r][8], g[r][4]
    if "B" in state:  # T2: r55-56 c5-6 <-> r59-60 c5-6
        for c in (5, 6):
            g[55][c], g[59][c] = g[59][c], g[55][c]
            g[56][c], g[60][c] = g[60][c], g[56][c]
    return g

WALL = set("48")

def can(g, R, C):
    if R < 0 or C < 0 or R + 5 > len(g) or C + 5 > 64:
        return False
    for r in range(R, R + 5):
        for c in range(C, C + 5):
            if g[r][c] in WALL:
                return False
    return True

for st in ("", "A", "B", "AB"):
    g = build(st)
    seen = {(40, 19)}
    q = deque([(40, 19)])
    while q:
        R, C = q.popleft()
        for dr, dc in ((-5, 0), (5, 0), (0, -5), (0, 5)):
            NR, NC = R + dr, C + dc
            if (NR, NC) not in seen and can(g, NR, NC):
                seen.add((NR, NC)); q.append((NR, NC))
    print(f"state '{st or 'base'}': {len(seen)} anchors; rows {sorted(set(r for r,c in seen))}")
