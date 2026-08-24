import sys
from collections import deque

def base_grid():
    ls = [l.rstrip("\n") for l in open("avo/s000.txt", encoding="utf-8")]
    g = [list(l) for l in ls if len(l) == 64 and all(ch in "0123456789abcdef" for ch in l)]
    # erase initial avatar overlay (top2=c rest=9 at r45-49 c34-38) -> under is floor 3
    for r in range(45, 50):
        for c in range(34, 39):
            if g[r][c] in ("c", "9"):
                g[r][c] = "3"
    return g

WALL = set("48")

def can(g, R, C):
    # avatar occupies rows R..R+4, cols C..C+4; all cells must be non-wall
    for r in range(R, R + 5):
        for c in range(C, C + 5):
            if not (0 <= r < len(g) and 0 <= c < 64):
                return False
            if g[r][c] in WALL:
                return False
    return True

def bfs(g, R0, C0):
    seen = {(R0, C0)}
    q = deque([(R0, C0)])
    par = {}
    while q:
        R, C = q.popleft()
        for dr, dc, m in ((-5, 0, "U"), (5, 0, "D"), (0, -5, "L"), (0, 5, "R")):
            NR, NC = R + dr, C + dc
            if (NR, NC) not in seen and can(g, NR, NC):
                seen.add((NR, NC))
                par[(NR, NC)] = ((R, C), m)
                q.append((NR, NC))
    return seen, par

g = base_grid()
start = (40, 34)  # current top-left of avatar after U,U,D,R from spawn... verify: spawn (45,34); U->40; U->35; D->40; R->(40,39)? 
# Actually current real pos: after A1(U):40, A1(U):35, A2(D):40, A4(R):39 cols -> (40,39)
start = (40, 39)
seen, par = bfs(g, *start)
print(f"reachable 5x5 anchors from {start}: {len(seen)}")
targets = {
    "glyph-cover (30,19)": (30, 19),
    "room-interior candidates": [(9, 34), (9, 36), (11, 34), (11, 36)],
    "corridor (20,35)": (20, 35),
    "bottomleft area": [(55, 2), (53, 2), (58, 2)],
}
def path_to(t, par):
    if t not in par and t != start:
        return None
    seq = []
    cur = t
    while cur != start:
        prev, m = par[cur]
        seq.append(m)
        cur = prev
    return list(reversed(seq))

for name, ts in targets.items():
    ts = ts if isinstance(ts, list) else [ts]
    for t in ts:
        p = path_to(t, par)
        print(f"{name} {t}: {'REACHABLE via ' + ''.join(p) if p else 'NOT reachable'}")
print()
# print all reachable anchor rows/cols summary
rows = sorted(set(r for r, c in seen))
cols = sorted(set(c for r, c in seen))
print("anchor rows:", rows)
print("anchor cols:", cols)
