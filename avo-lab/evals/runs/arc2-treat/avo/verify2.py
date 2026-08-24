import importlib.util
from arcengine import GameAction, ActionInput

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), mod.__dict__)

g = mod.Ls20()
g.perform_action(ActionInput(id=GameAction.RESET))
# replicate LIVE state: avatar at (14,30), rot idx 3 (fresh default), ~23 fuel columns left
g.gudziatsk.set_position(14, 30)
g._step_counter_ui.current_steps = 23
# keep REAL decrement (efipnixsvl=1)

def report(tag):
    av = g.gudziatsk
    print(f"{tag}: pos=({av.x},{av.y}) shape={g.fwckfzsyc} color={g.hiaauhahz} rot={g.cklxociuu} "
          f"goals={g.lvrnuajbl} level={g.level_index} fuel={g._step_counter_ui.current_steps}")

seq = [GameAction.ACTION4] + [GameAction.ACTION1]*2 + [GameAction.ACTION4]*3 + [GameAction.ACTION1]*3
report("start(live-mirror)")
total = 0
for i, a in enumerate(seq):
    g.perform_action(ActionInput(id=a))
    total += 1
    extra = 0
    while not (not g.euemavvxz and g.akoadfsur == 0 and g.ebfuxzbvn == 0 and g.is_action_complete()):
        g.perform_action(ActionInput(id=GameAction.ACTION1))
        total += 1
        extra += 1
    report(f"{i+1}: {a.name} (+{extra} pump)")
print("TOTAL server actions needed:", total)
print("final _state:", g._state)
