"""Probe 2: list official environments and play one via the toolkit."""
import arc_agi
from arcengine import GameAction

arc = arc_agi.Arcade()
envs = arc.get_environments()
print("env count:", len(envs))
sample = []
for e in envs[:10]:
    gid = e.get("game_id") if isinstance(e, dict) else getattr(e, "game_id", None)
    sample.append(gid)
print("sample ids:", sample)

target = None
for e in envs:
    gid = e.get("game_id") if isinstance(e, dict) else getattr(e, "game_id", None)
    if gid and gid.startswith("ls20"):
        target = gid
        break
target = target or sample[0]
print("trying:", target)

env = arc.make(target, render_mode=None)  # no terminal render -> avoids TTY issues
frame = env.reset()
grid = getattr(frame, "grid", None)
print("reset ok; grid:", (len(grid), len(grid[0])) if grid else "n/a")
r1 = env.step(GameAction.ACTION1)
print("ACTION1 ->", getattr(r1, "state", None))
r2 = env.step(GameAction.ACTION6, data={"x": 15, "y": 15})
print("ACTION6 ->", getattr(r2, "state", None))
print("OFFICIAL-GAME-PLAYABLE: yes")
