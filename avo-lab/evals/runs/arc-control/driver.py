"""ARC-AGI-3 session driver: persistent background server + blocking client.

The server holds the live game object in memory. The client communicates via
cmd.txt / resp.txt files so a sub-agent can drive the game one shell call at
a time.

Setup (once per session, from the session directory):
  Start-Process -WindowStyle Hidden <venv-python> driver.py serve <game_id>

Then each action (blocks until the server replies):
  python driver.py client ACT ACTION1
  python driver.py client ACT ACTION6 12 34
  python driver.py client STATUS
"""
import json
import sys
import time
from pathlib import Path

CMD = Path("cmd.txt")
RESP = Path("resp.txt")
READY = Path("ready.txt")
LOG = Path("arc_log.jsonl")
CHARS = "0123456789abcdef"


def frame_info(resp):
    grid = None
    fr = getattr(resp, "frame", None)
    if fr:
        try:
            layer = fr[0]
            grid = ["".join(CHARS[int(v) % 16] for v in row) for row in layer]
        except Exception:
            grid = None
    return {
        "state": str(getattr(resp, "state", None)),
        "levels_completed": getattr(resp, "levels_completed", None),
        "win_levels": getattr(resp, "win_levels", None),
        "available_actions": [str(a) for a in (getattr(resp, "available_actions", None) or [])],
        "grid": grid,
    }


def render(info, steps, baseline):
    lines = list(info["grid"] or ["(no grid)"])
    lines.append(f"step={steps} state={info['state']} "
                 f"levels={info['levels_completed']}/{info['win_levels']}")
    if baseline:
        lines.append(f"human_baseline_actions_per_level={baseline}")
    lines.append(f"available_actions={info['available_actions']}")
    return "\n".join(lines)


def serve(game_id):
    import arc_agi
    for f in (CMD, RESP, READY, LOG):
        if f.exists():
            f.unlink()
    arc = arc_agi.Arcade()
    card = arc.create_scorecard()
    env = arc.make(game_id, scorecard_id=card, render_mode=None)
    resp = env.reset()
    steps = 0
    baseline = None
    try:
        envs = {e.game_id: e for e in arc.get_environments()}
        baseline = envs[game_id].baseline_actions
    except Exception:
        pass
    info = frame_info(resp)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"step": steps, **{k: v for k, v in info.items() if k != "grid"}}) + "\n")
    READY.write_text(render(info, steps, baseline), encoding="utf-8")
    RESP.write_text(render(info, steps, baseline), encoding="utf-8")

    while True:
        if CMD.exists():
            try:
                raw = CMD.read_text(encoding="utf-8").strip()
                CMD.unlink()
                parts = raw.split()
                if parts[0] == "QUIT":
                    RESP.write_text("server quitting", encoding="utf-8")
                    break
                if parts[0] == "STATUS":
                    RESP.write_text(render(info, steps, baseline), encoding="utf-8")
                    time.sleep(0.05)
                    continue
                if parts[0] == "ACT":
                    from arcengine import GameAction
                    act = getattr(GameAction, parts[1], None)
                    if act is None:
                        RESP.write_text(f"ERROR unknown action {parts[1]}", encoding="utf-8")
                        continue
                    data = None
                    if len(parts) >= 4:
                        data = {"x": int(parts[2]), "y": int(parts[3])}
                    resp = env.step(act, data=data)
                    steps += 1
                    info = frame_info(resp)
                    with LOG.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps({"step": steps, **{k: v for k, v in info.items() if k != "grid"}}) + "\n")
                    RESP.write_text(render(info, steps, baseline), encoding="utf-8")
                    continue
                RESP.write_text(f"ERROR bad command: {raw}", encoding="utf-8")
            except Exception as exc:  # noqa: BLE001 — server must survive agent mistakes
                try:
                    RESP.write_text(f"ERROR {type(exc).__name__}: {exc}", encoding="utf-8")
                except Exception:
                    pass
        time.sleep(0.1)


def client(parts):
    deadline = time.time() + 90
    while not READY.exists() and time.time() < deadline:
        time.sleep(0.5)
    if not READY.exists():
        raise SystemExit("server not ready after 90s; is it running?")
    RESP.unlink(missing_ok=True)
    CMD.write_text(" ".join(parts), encoding="utf-8")
    while time.time() < deadline:
        if RESP.exists():
            try:
                print(RESP.read_text(encoding="utf-8"))
                return
            except Exception:
                time.sleep(0.05)
        time.sleep(0.1)
    raise SystemExit("timeout waiting for server response")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "serve":
        serve(sys.argv[2])
    elif c == "client":
        client(sys.argv[2:])
    else:
        raise SystemExit(__doc__)
