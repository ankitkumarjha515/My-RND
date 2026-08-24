import importlib.util
from arcengine import GameAction, ActionInput

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), mod.__dict__)

def fresh():
    g = mod.Ls20()
    g.perform_action(ActionInput(id=GameAction.RESET))
    g._step_counter_ui.efipnixsvl = 0
    return g

g = fresh()

def report(tag):
    av = g.gudziatsk
    print(f"{tag}: pos=({av.x},{av.y}) shape={g.fwckfzsyc} color={g.hiaauhahz} rot={g.cklxociuu} "
          f"goals={g.lvrnuajbl} level={g.level_index} counter={g._step_counter_ui.current_steps}")

seq = [GameAction.ACTION3]*3 + [GameAction.ACTION1]*4 + [GameAction.ACTION4]*3 + [GameAction.ACTION1]*3  # L L L U U U U R R R U U U
report("start")
for i, a in enumerate(seq):
    g.perform_action(ActionInput(id=GameAction(a)))
    # pump animations with RESET-action-free frames: use step via complete? just pump ACTION1 but track
    extra = 0
    while not (not g.euemavvxz and g.akoadfsur == 0 and g.ebfuxzbvn == 0 and g.is_action_complete()):
        g.perform_action(ActionInput(id=GameAction.ACTION1))
        extra += 1
    report(f"after {i+1} ({a.name}, +{extra} pump)")
print("state:", str(g.state))

