import sys

def load(p):
    return [l.rstrip("\n") for l in open(p)
            if len(l.rstrip("\n")) == 64 and all(c in "0123456789abcdef" for c in l.rstrip("\n").lower())]

g = load(sys.argv[1])
start = tuple(int(v) for v in sys.argv[2].split(","))
goal_test = sys.argv[3]  # "r,c" list separated by ; e.g. "40,14;35,14"

WALL = "4"

def can(r, c):
    if r < 0 or c < 0 or r + 5 > 64 or c + 5 > 64:
        return False
    for y in range(r, r + 5):
        for x in range(c, c + 5):
            if g[y][x] == WALL:
                return False
    return True

from collections import deque
goals = set(tuple(int(v) for v in t.split(",")) for t in goal_test.split(";"))
q = deque([start])
prev = {start: None}
while q:
    cur = q.popleft()
    if cur in goals:
        break
    r, c = cur
    for dr, dc, name in ((-5, 0, "ACTION1"), (5, 0, "ACTION2"), (0, -5, "ACTION3"), (0, 5, "ACTION4")):
        nxt = (r + dr, c + dc)
        if nxt not in prev and can(*nxt):
            prev[nxt] = (cur, name)
            q.append(nxt)

if cur not in goals:
    print("NO PATH to", goals)
    # print all reachable anchors for debugging
    print("reachable:", sorted(prev.keys()))
else:
    path = []
    while prev[cur] is not None:
        p, name = prev[cur]
        path.append(name)
        cur = p
    path.reverse()
    print("PATH:", " ".join(path))
    print("length:", len(path))
