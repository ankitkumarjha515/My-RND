import importlib.util
import sys
from arcengine import GameAction, ActionInput

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), mod.__dict__)

li = int(sys.argv[1])
seq = sys.argv[2]
g = mod.Ls20()
g.perform_action(ActionInput(id=GameAction.RESET))
g.set_level(li)
ok = False
for i, c in enumerate(seq):
    g.perform_action(ActionInput(id=getattr(GameAction, "ACTION" + c)))
    st = str(g._state)
    if "GAME_OVER" in st or "LOSE" in st or "NOT_PLAYABLE" in st:
        print(f"DIE at act {i+1} ({c}) state={st}")
        sys.exit(1)
    if g.level_index != li:
        print(f"WIN at act {i+1}: level_index {li} -> {g.level_index}, fuel_left={g._step_counter_ui.current_steps}, lives={g.aqygnziho}")
        ok = True
        break
if not ok:
    print(f"NO WIN after {len(seq)} acts: pos=({g.gudziatsk.x},{g.gudziatsk.y}) goals={g.lvrnuajbl} fuel={g._step_counter_ui.current_steps} state={g._state}")
    sys.exit(1)
