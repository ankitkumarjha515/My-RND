"""Feasibility probe: run an ARC-AGI-3 environment fully locally, no API key."""
import sys

import arc_agi
from arcengine import GameAction

arc = arc_agi.Arcade(environments_dir="avo-lab/vendor/arcenv-test/environment_files")
env = arc.make("ab12-v1", seed=0, render_mode="terminal")

print("== initial frame ==")
frame = env.reset()
print(type(frame).__name__)
print(frame.grid if hasattr(frame, "grid") else frame)

print("== take 3 actions ==")
total = 0
for x, y in [(32, 32), (10, 10), (40, 40)]:
    result = env.step(GameAction.ACTION6, data={"x": x, "y": y})
    total += 1
    state = getattr(result, "state", None)
    score = getattr(result, "score", None)
    print(f"action {total}: state={state} score={score}")

print("FEASIBLE: local ARC-AGI-3 environment ran offline, no API key")
