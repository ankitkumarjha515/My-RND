import importlib.util

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), mod.__dict__)

li = int(sys_arg) if (sys_arg := __import__("sys").argv[1]) else 3
g = mod.Ls20()
g.perform_action(__import__("arcengine", fromlist=["ActionInput"]).ActionInput(
    id=__import__("arcengine", fromlist=["GameAction"]).GameAction.RESET))
g.set_level(li)
lv = g.current_level
print("level_index:", g.level_index)
print("StepsDecrement-ish fuel cols:", g._step_counter_ui.total_steps if hasattr(g._step_counter_ui, 'total_steps') else "?")
for sp in list(lv._sprites):
    tags = getattr(sp, "_tags", None) or getattr(sp, "tags", None)
    cls = type(sp).__name__
    try:
        pos = (sp.x, sp.y)
    except Exception:
        pos = None
    print(cls, pos, tags if tags is not None else "", str(sp)[:80])
