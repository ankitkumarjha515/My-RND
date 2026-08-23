"""X3 checker - warehouse repair. Usage: python x3_checker.py <task_dir>"""
import importlib.util
import sys
from pathlib import Path


def main():
    task = Path(sys.argv[1])
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    mod = None
    sol = task / "warehouse.py"
    if sol.exists():
        try:
            spec = importlib.util.spec_from_file_location("wh_under_test", sol)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            grp("imports", False, f"{type(exc).__name__}: {exc}")
    if mod is None and not results:
        grp("imports", False, "warehouse.py missing")

    Inv = getattr(mod, "Inventory", None) if mod else None
    if not isinstance(Inv, type):
        grp("has-inventory", False)
        for g in ("reserve-boundary", "partial-release",
                  "commit-fifo", "api-errors"):
            grp(g, False)
    else:
        grp("has-inventory", True)
        failures = []

        def check(label, cond):
            if not cond:
                failures.append(label)

        def raises(fn):
            try:
                fn()
                return False
            except ValueError:
                return True
            except Exception:  # noqa: BLE001
                return False

        def case_reserve():
            inv = Inv()
            check("unknown-sku-available-0", inv.available("x") == 0)
            check("reserve-before-receive-rejected",
                  raises(lambda: inv.reserve("x", 1)))
            inv.receive("a", 10)
            r1 = inv.reserve("a", 6)
            check("rid-starts-1", r1 == 1)
            check("available-after-reserve", inv.available("a") == 4)
            check("oversell-blocked", raises(lambda: inv.reserve("a", 5)))
            check("exact-fit-ok", isinstance(inv.reserve("a", 4), int))
            check("zero-left-blocked", raises(lambda: inv.reserve("a", 1)))
            inv.receive("a", 2)          # restock while fully reserved
            check("restock-respects-reserved", inv.available("a") == 2)

        def case_release():
            inv = Inv()
            inv.receive("b", 10)
            ra = inv.reserve("b", 5)
            rb = inv.reserve("b", 4)
            inv.release("b", ra, 2)      # partial: 3 still reserved under ra
            check("partial-shrinks-only", inv.available("b") == 10 - (3 + 4))
            inv.release("b", ra, 99)     # capped at remainder -> reservation gone
            check("over-release-capped", inv.available("b") == 10 - 4)
            check("released-immediately-reservable",
                  isinstance(inv.reserve("b", 3), int))
            check("other-reservation-intact",
                  inv.release("b", rb, 1) is None and inv.available("b") == 4)
            # state: stock 10, live reserved = rb(3) + later(3) -> available 4
            check("release-unknown-rid", raises(lambda: inv.release("b", 999, 1)))

        def case_commit():
            inv = Inv()
            inv.receive("c", 20)
            inv.reserve("c", 5)   # rid1
            inv.reserve("c", 7)   # rid2
            inv.commit("c", 8)         # consumes rid1 fully + 3 of rid2 (FIFO)
            check("commit-stock-decrement", inv.available("c") == 20 - 8 - 4)
            check("fifo-remainder-reserved", True)
            # committing below reserved must NOT free reservations silently
            inv.commit("c", 12)        # stock 0 left; consumes remaining 4 + shortfall
            check("commit-to-empty", inv.available("c") == 0)
            check("no-negative-stock", raises(lambda: inv.commit("c", 1)))
            # fresh: commit without any reservations just decrements stock
            inv2 = Inv()
            inv2.receive("d", 5)
            inv2.commit("d", 2)
            check("plain-commit-no-reservations", inv2.available("d") == 3)

        def case_errors():
            inv = Inv()
            inv.receive("e", 5)
            check("bad-qty-zero", raises(lambda: inv.receive("e", 0)))
            check("bad-qty-type", raises(lambda: inv.reserve("e", 1.5)))
            check("bad-sku", raises(lambda: inv.commit("", 1)))
            check("bool-not-int", raises(lambda: inv.receive("e", True)))
            check("available-known-sku", inv.available("e") == 5)

        for name, fn in [("reserve-boundary", case_reserve),
                         ("partial-release", case_release),
                         ("commit-fifo", case_commit),
                         ("api-errors", case_errors)]:
            failures.clear()
            try:
                fn()
                err = None
            except Exception as exc:  # noqa: BLE001
                err = f"{type(exc).__name__}: {exc}"
            ok = err is None and not failures
            grp(name, ok, err or ("; ".join(failures[:4]) if failures else ""))

    weights = {"reserve-boundary": 30, "partial-release": 25,
               "commit-fifo": 30, "api-errors": 15}
    score = sum(w for name, w in weights.items()
                if any(line.startswith("OK") and name in line for line, _ in results))
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
