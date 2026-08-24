import importlib.util
import sys
from collections import deque
from arcengine import GameAction, ActionInput

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), mod.__dict__)


def make_game(level_index):
    g = mod.Ls20()
    g.perform_action(ActionInput(id=GameAction.RESET))
    g.set_level(level_index)
    g._step_counter_ui.efipnixsvl = 0  # freeze fuel during search
    return g


class Solver:
    def __init__(self, level_index):
        self.li = level_index
        self.g = make_game(level_index)
        lv = self.g.current_level
        self.wanderers = []
        for base in lv.get_sprites_by_tag("xfmluydglp"):
            for tag in ("ttfwljgohq", "soyhouuebz", "rhsxkxzdjz"):
                for cy in lv.get_sprites_by_tag(tag):
                    from arcengine import BlockingMode
                    # replicate game's pairing rule: overlap
                    if (base.x <= cy.x < base.x + base.width and base.y <= cy.y < base.y + base.height):
                        for obj in self.g.wsoslqeku:
                            if obj._sprite is cy:
                                self.wanderers.append(obj)
        self.pads = list(self.g.plrpelhym)

    def snapshot(self):
        g, lv = self.g, self.g.current_level
        return (
            g.gudziatsk.x, g.gudziatsk.y,
            g.fwckfzsyc, g.hiaauhahz, g.cklxociuu,
            tuple(g.lvrnuajbl),
            tuple((w._sprite.x, w._sprite.y, w._dir, w._undo_x, w._undo_y, w._undo_dir) for w in self.wanderers),
            tuple(s.is_visible for s in lv.get_sprites_by_tag("rjlbuycveu")),
        )

    def restore(self, s):
        g, lv = self.g, self.g.current_level
        x, y, shp, col, rot, goals, wanders, _padvis = s
        if g.level_index != self.li:  # a trial won; jump back
            g.set_level(self.li)
        av = g.gudziatsk
        av.set_position(x, y)
        g.fwckfzsyc, g.hiaauhahz, g.cklxociuu = shp, col, rot
        g.htkmubhry.pixels = g.ijessuuig[shp].pixels.copy()
        g.htkmubhry.color_remap(None, g.tnkekoeuk[col])
        g.htkmubhry.set_rotation(g.dhksvilbb[rot])
        g.lvrnuajbl = list(goals)
        for w, st in zip(self.wanderers, wanders):
            wx, wy, wd, ux, uy, ud = st
            w._sprite.set_position(wx, wy)
            w._dir, w._undo_x, w._undo_y, w._undo_dir = wd, ux, uy, ud
        # ensure any collected pads are back & flags consistent
        want = set(i for i, got in enumerate(goals) if not got)
        have = {self.pads.index(sp) for sp in lv.get_sprites_by_tag("rjlbuycveu")}
        for i in range(len(self.pads)):
            pad = self.pads[i]
            disp = g.srgbthxut[i]
            if i in want and pad not in lv._sprites:
                lv.add_sprite(pad)
                if disp is not None and disp not in lv._sprites:
                    lv.add_sprite(disp)
        g.akoadfsur = 0
        g.ebfuxzbvn = 0
        g.euemavvxz = []

    def actions(self):
        return [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]

    def solve(self, max_states=200000):
        g = self.g
        start = self.snapshot()
        parent = {start: None}
        seen = {start}
        q = deque([start])
        win = None
        while q and win is None:
            s = q.popleft()
            for a in self.actions():
                self.restore(s)
                g.perform_action(ActionInput(id=a))
                ns = self.snapshot()
                if ns == s:
                    continue
                if ns not in seen:
                    seen.add(ns)
                    parent[ns] = (s, a)
                    if g.level_index != self.li or (len(ns[5]) and all(ns[5])):
                        win = ns
                        break
                    if len(seen) > max_states:
                        print("state cap hit")
                        return None, None
                    q.append(ns)
        if win is None:
            return None, None
        seq = []
        cur = win
        while parent[cur] is not None:
            ps, a = parent[cur]
            seq.append(a.value)
            cur = ps
        seq.reverse()
        return seq, len(seen)


def replay(level_index, seq, freeze_fuel=False):
    """Replay on fresh instance; returns (won, fuel_min, frames)."""
    g = make_game(level_index)
    if freeze_fuel:
        pass
    else:
        g._step_counter_ui.efipnixsvl = 1
    fuel_min = g._step_counter_ui.current_steps
    for v in seq:
        g.perform_action(ActionInput(id=getattr(GameAction, "ACTION%d" % v)))
        cs = g._step_counter_ui.current_steps
        fuel_min = min(fuel_min, cs)
        if cs < 0:
            return False, fuel_min, None
        if g.level_index != level_index:
            return True, fuel_min, None
    return bool(g.lvrnuajbl and all(g.lvrnuajbl)), fuel_min, None


if __name__ == "__main__":
    li = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    s = Solver(li)
    print(f"level {li}: wanderers={len(s.wanderers)} pads={len(s.pads)}")
    seq, n = s.solve()
    if seq is None:
        print("NO SOLUTION FOUND")
        sys.exit(1)
    names = {1: "U", 2: "D", 3: "L", 4: "R"}
    print(f"solution ({len(seq)} acts, {n} states): {''.join(names[v] for v in seq)}")
    won, fmin, _ = replay(li, seq)
    print(f"replay with real fuel: won={won} fuel_min={fmin}")




