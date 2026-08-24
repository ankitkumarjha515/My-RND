import sys
from collections import deque

fn = sys.argv[1]
lines = [l.rstrip("\n") for l in open(fn) if len(l.rstrip("\n")) == 64]
g = lines[:64]
PASS = set("0123589bc")
def ok(tl_r, tl_c):
    if tl_r < 0 or tl_c < 0 or tl_r + 4 > 59 or tl_c + 4 > 59:
        return False
    for r in range(tl_r, tl_r + 5):
        for c in range(tl_c, tl_c + 5):
            if g[r][c] not in PASS:
                return False
    return True

start = tuple(int(x) for x in sys.argv[2].split(","))
goal_test = sys.argv[3]  # "r1,r2,c1,c2" top-left window
gr1, gr2, gc1, gc2 = (int(x) for x in goal_test.split(","))

q = deque([(start, [])])
seen = {start}
while q:
    (r, c), path = q.popleft()
    if gr1 <= r <= gr2 and gc1 <= c <= gc2:
        print("PATH len", len(path), path)
        break
    for act, dr, dc in (("1", -5, 0), ("2", 5, 0), ("3", 0, -5), ("4", 0, 5)):
        nr, nc = r + dr, c + dc
        if (nr, nc) not in seen and ok(nr, nc):
            seen.add((nr, nc))
            q.append(((nr, nc), path + [act]))
else:
    print("NO PATH")
