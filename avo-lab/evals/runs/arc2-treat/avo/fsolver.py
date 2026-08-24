import importlib.util
import sys
from collections import deque
from arcengine import GameAction, ActionInput

SRC = r"environment_files\ls20\9607627b\ls20.py"
spec = importlib.util.spec_from_loader("ls20mod", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), mod.__dict__)

ACTS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]


def make_game(level_index):
    g = mod.Ls20()
    g.perform_action(ActionInput(id=GameAction.RESET))
    g.set_level(level_index)
    return g


class FuelSolver:
    """BFS over engine states including fuel/lives/pickups. No freezing."""

    def __init__(self, level_index):
        self.li = level_index
        self.g = make_game(level_index)
        lv0 = self.g.current_level
        self.pickups = list(lv0.get_sprites_by_tag("npxgalaybz"))
        self.pads = list(self.g.plrpelhym)
        self.disps = list(self.g.srgbthxut)
        self.wanderers = list(getattr(self.g, "wsoslqeku", []))

    def snap(self):
        g = self.g
        lv = g.current_level
        pickups = tuple((sp.is_visible, sp in lv._sprites) for sp in self.pickups)
        pads_vis = tuple(sp.is_visible for sp in lv.get_sprites_by_tag("rjlbuycveu"))
        pad_present = tuple(sp in lv._sprites for sp in self.pads)
        disp_present = tuple(d is not None and d in lv._sprites for d in self.disps)
        wand = tuple(
            (w._sprite.x, w._sprite.y, w._dir, w._undo_x, w._undo_y, w._undo_dir)
            for w in self.wanderers
        )
        return (
            g.gudziatsk.x, g.gudziatsk.y,
            g.fwckfzsyc, g.hiaauhahz, g.cklxociuu,
            tuple(g.lvrnuajbl),
            g._step_counter_ui.current_steps,
            g.aqygnziho,
            pickups, pad_present, disp_present,
            wand,
        )

    def restore(self, s):
        g = self.g
        (x, y, shp, col, rot, goals, steps, lives,
         pickups, pad_present, disp_present, wand) = s
        if g.level_index != self.li:
            g.set_level(self.li)
        av = g.gudziatsk
        av.set_position(x, y)
        g.fwckfzsyc, g.hiaauhahz, g.cklxociuu = shp, col, rot
        g.htkmubhry.pixels = g.ijessuuig[shp].pixels.copy()
        g.htkmubhry.color_remap(None, g.tnkekoeuk[col])
        g.htkmubhry.set_rotation(g.dhksvilbb[rot])
        g.lvrnuajbl = list(goals)
        g._step_counter_ui.current_steps = steps
        g.aqygnziho = lives
        lv = g.current_level
        for sp, (vis, present) in zip(self.pickups, pickups):
            sp.set_visible(vis)
            if present and sp not in lv._sprites:
                lv.add_sprite(sp)
            elif not present and sp in lv._sprites:
                lv.remove_sprite(sp)
        for i, pad in enumerate(self.pads):
            want = bool(pad_present[i])
            have = pad in lv._sprites
            if want and not have:
                lv.add_sprite(pad)
            elif have and not want:
                lv.remove_sprite(pad)
            disp = g.srgbthxut[i]
            if disp is not None:
                wdisp = bool(disp_present[i])
                hdisp = disp in lv._sprites
                if wdisp and not hdisp:
                    lv.add_sprite(disp)
                elif hdisp and not wdisp:
                    lv.remove_sprite(disp)
        g.akoadfsur = 0
        g.ebfuxzbvn = 0
        g.euemavvxz = []
        for w, (wx, wy, wd, ux, uy, udir) in zip(self.wanderers, wand):
            w._sprite.set_position(wx, wy)
            w._dir = wd
            w._undo_x = ux
            w._undo_y = uy
            w._undo_dir = udir

    def solve(self, init_state=None, max_states=400000):
        g = self.g
        if init_state is not None:
            self.restore(init_state)
        start = self.snap()
        parent = {start: None}
        seen = {start}
        q = deque([start])
        win = None
        while q:
            s = q.popleft()
            for a in ACTS:
                self.restore(s)
                g.perform_action(ActionInput(id=a))
                won = g.level_index != self.li
                if str(g._state) in ("GameState.GAME_OVER", "GameState.LOSE"):
                    continue
                if won:
                    ns = ("WIN",)
                else:
                    ns = self.snap()
                if ns == s:
                    continue
                if ns not in seen:
                    seen.add(ns)
                    parent[ns] = (s, a)
                    if ns[0] == "WIN" or (len(ns[5]) > 1 and all(ns[5])):
                        win = ns
                        break
                    if len(seen) > max_states:
                        print("cap")
                        return None, None
                    q.append(ns)
            if win:
                break
        if win is None:
            return None, len(seen)
        seq = []
        cur = win
        while parent[cur] is not None:
            ps, a = parent[cur]
            seq.append(a.name[-1])
            cur = ps
        seq.reverse()
        return seq, len(seen)


if __name__ == "__main__":
    li = int(sys.argv[1])
    fs = FuelSolver(li)
    if len(sys.argv) > 2 and sys.argv[2] == "live":
        # mirror current live state for level li
        fuel = int(sys.argv[3]); lives = int(sys.argv[4])
        g = fs.g
        g._step_counter_ui.current_steps = fuel
        g.aqygnziho = lives
    seq, n = fs.solve(fs.snap())
    if seq is None:
        print("NO SOLUTION", n)
        sys.exit(1)
    M = {"1": "U", "2": "D", "3": "L", "4": "R"}
    print(f"solution {len(seq)} acts ({n} states): {''.join(M[c] for c in seq)}")
    # verify by replay on fresh mirror
    g2 = make_game(li)
    ok = True
    for c in seq:
        g2.perform_action(ActionInput(id=getattr(GameAction, "ACTION" + c)))
        if str(g2._state) in ("GameState.GAME_OVER", "GameState.LOSE"):
            ok = False; break
        if len(g2.lvrnuajbl) and all(g2.lvrnuajbl):
            ok = True; break
    print("replay won:", ok and (len(g2.lvrnuajbl) and all(g2.lvrnuajbl)), "final fuel:", g2._step_counter_ui.current_steps, "lives:", g2.aqygnziho)
    print("SEQ1:" + "".join(seq))


