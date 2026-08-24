import importlib.util

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
src = open(SRC, encoding="utf-8").read()
exec(compile(src, SRC, "exec"), mod.__dict__)

game = mod.Ls20()
from arcengine import GameAction, ActionInput
fr = game.perform_action(ActionInput(id=GameAction.RESET))

lv = game.current_level
walls = [s for s in lv._sprites if s.tags and "ihdgageizm" in s.tags]
print("num walls:", len(walls))
blocked = set()
for w in walls:
    for dx in range(w.width):
        for dy in range(w.height):
            blocked.add((w.x + dx, w.y + dy))

# render frame from engine for comparison
import numpy as np
arr = fr.frame[0] if isinstance(fr.frame, tuple) else fr.frame
print("frame type:", type(fr.frame), getattr(arr, "shape", None))

def can(R, C):
    for r in range(R, R + 5):
        for c in range(C, C + 5):
            if (r, c) in blocked:
                return False
    return True

anchors = [(R, C) for R in range(0, 60, 5) for C in range(0, 60, 5)]
print("free anchors sample:", [a for a in anchors if can(*a)][:50])
print("is (34,10) free?", can(34, 10))
print("is (19,30) free?", can(19, 30))
print("is (34,45) free?", can(34, 45))

# BFS over anchors from start
from collections import deque
start = (34, 45)
seen = {start}
q = deque([start])
par = {}
while q:
    R, C = q.popleft()
    for dr, dc, m in ((-5, 0, "U"), (5, 0, "D"), (0, -5, "L"), (0, 5, "R")):
        N = (R + dr, C + dc)
        if N not in seen and can(*N):
            seen.add(N); par[N] = ((R, C), m); q.append(N)

def path(t):
    if t == start:
        return ""
    if t not in par:
        return None
    seq = []
    cur = t
    while cur != start:
        p, m = par[cur]
        seq.append(m); cur = p
    return "".join(reversed(seq))

print("reachable:", len(seen))
for name, t in [("cycler", (19, 30)), ("goal", (34, 10)), ("goal2", (34, 15))]:
    print(name, t, path(t))

