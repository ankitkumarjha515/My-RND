"""H1 checker — TTL+LRU cache. Usage: python h1_checker.py <task_dir>

The performance group runs the solution in a SUBPROCESS with a hard timeout:
a non-compliant (e.g. O(n)-per-op) implementation gets killed and FAILs
instead of hanging the whole checker.
"""
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

DRIVER = r'''
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("sol", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
t = 0.0
def clk():
    return t
c = mod.TTLCache(50000, clk)
state = 123456789
def rnd(n):
    global state
    state = (state * 1103515245 + 12345) % (2**31)
    return state % n
t0 = time.perf_counter()
for i in range(150000):
    op = rnd(10)
    k = "k" + str(rnd(50000))
    if op < 6:
        c.put(k, i, ttl=rnd(1000))
    elif op < 9:
        c.get(k)
    else:
        c.delete(k)
dt = time.perf_counter() - t0
print(f"PERF_SECONDS {dt:.3f}")
'''


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def main():
    task = Path(sys.argv[1])
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    mod = None
    sol = task / "solution.py"
    if sol.exists():
        try:
            spec = importlib.util.spec_from_file_location("ttl_solution", sol)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            grp("imports", False, f"{type(exc).__name__}: {exc}")
    if mod is None and not results:
        grp("imports", False, "solution.py missing")

    TTLCache = getattr(mod, "TTLCache", None) if mod else None
    if not isinstance(TTLCache, type):
        grp("has-ttlcache", False)
        for g in ("basic-ops", "expiry-semantics", "lru-eviction", "performance"):
            grp(g, False)
    else:
        grp("has-ttlcache", True)
        failures = []

        def check(label, cond):
            if not cond:
                failures.append(label)

        def case_basic():
            clk = FakeClock()
            c = TTLCache(2, clk)
            try:
                TTLCache(0, clk)
                check("capacity-validation", False)
            except ValueError:
                check("capacity-validation", True)
            check("miss-default", c.get("a") is None and c.get("a", 7) == 7)
            c.put("a", 1)
            check("roundtrip", c.get("a") == 1)
            c.put("a", 2)  # update existing
            check("update-value", c.get("a") == 2)
            check("delete-hit", c.delete("a") is True)
            check("delete-miss", c.delete("a") is False)
            c.put("x", 5, ttl=10)
            c.put("y", 6)
            check("clear-count", c.clear() == 2)
            check("cleared-empty", c.get("x") is None)

        def case_expiry():
            # Integer timestamps keep the >= boundary exact (no float dust).
            clk = FakeClock()
            c = TTLCache(10, clk)
            c.put("t", "v", ttl=5)
            clk.advance(4)
            check("before-expiry-live", c.get("t") == "v")
            clk.advance(1)              # now == inserted+5 -> expired (exclusive)
            check("boundary-expired", c.get("t") is None)
            c.put("n", 1)               # capacity must have been reclaimed
            c.put("m", 2)
            c.put("k", 3)
            check("expired-freed-capacity",
                  c.delete("n") and c.delete("m") and c.delete("k"))
            c.put("p", 9, ttl=3)
            check("delete-live-true", c.delete("nope") is False)
            clk.advance(3)
            check("delete-after-expiry-false", c.delete("p") is False)
            c.put("q", 1)               # p was expired; must not consume capacity
            c.put("r", 2)
            check("expired-not-counted", c.delete("q") and c.delete("r"))
            clk2 = FakeClock()
            cn = TTLCache(5, clk2)
            cn.put("forever", 1)        # ttl=None never expires
            clk2.advance(10 ** 9)
            check("none-ttl-immortal", cn.get("forever") == 1)

        def case_lru():
            clk = FakeClock()
            c = TTLCache(3, clk)
            c.put("a", 1); c.put("b", 2); c.put("c", 3)   # order a<b<c
            c.get("a")                                    # refresh a -> LRU is b
            c.put("d", 4)
            check("evicts-lru-not-mru", c.get("b", "MISS") == "MISS" and c.get("a") == 1)
            c.put("e", 5)                                 # LRU now c
            check("evicts-next-lru", c.get("c", "MISS") == "MISS" and c.get("d") == 4)
            clk_e = FakeClock()
            ce = TTLCache(3, clk_e)
            ce.put("x", 1, ttl=5); ce.put("y", 2); ce.put("z", 3)
            clk_e.advance(5)                              # x expired
            ce.put("w", 4)                                # reclaim x, not evict y
            vals = [ce.get(k, "MISS") for k in ("x", "y", "z", "w")]
            check("expired-reclaimed-first", vals == ["MISS", 2, 3, 4])

        def case_perf():
            try:
                proc = subprocess.run(
                    [sys.executable, "-c", DRIVER, str(sol)],
                    capture_output=True, text=True, timeout=30,
                )
            except subprocess.TimeoutExpired:
                check("150k-ops-under-5s", False,
                      "killed at 30s — implementation is not O(1) per op")
                return
            if proc.returncode != 0:
                check("150k-ops-under-5s", False,
                      (proc.stderr or "driver crashed").strip().splitlines()[-1][:200])
                return
            line = [ln for ln in proc.stdout.splitlines()
                    if ln.startswith("PERF_SECONDS")]
            if not line:
                check("150k-ops-under-5s", False, "no PERF_SECONDS output")
                return
            dt = float(line[-1].split()[1])
            check("150k-ops-under-5s", dt < 5.0)
            print(f"     perf: {dt:.2f}s for 150k mixed ops (cap=50000)")

        for name, fn in [("basic-ops", case_basic),
                         ("expiry-semantics", case_expiry),
                         ("lru-eviction", case_lru),
                         ("performance", case_perf)]:
            failures.clear()
            try:
                fn()
                err = None
            except Exception as exc:  # noqa: BLE001
                err = f"{type(exc).__name__}: {exc}"
            ok = err is None and not failures
            grp(name, ok, err or ("; ".join(failures[:4]) if failures else ""))

    weights = {"basic-ops": 25, "expiry-semantics": 30, "lru-eviction": 30,
               "performance": 15}
    score = sum(w for name, w in weights.items()
                if any(name in line and line.startswith("OK") for line, _ in results))
    perf_failed = any(line.startswith("FAIL performance") for line, _ in results)
    if perf_failed:
        score = min(score, 89)
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
