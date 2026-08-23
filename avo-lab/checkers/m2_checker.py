"""M2 checker — cart seeded defects. Usage: python m2_checker.py <task_dir>"""
import importlib.util
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path


def half_up(x: float) -> float:
    return float(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol


def run_case(fn):
    """Each case builds its own cart; returns True on success."""
    fn()


def main():
    task = Path(sys.argv[1])
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    mod = None
    sol = task / "cart.py"
    if sol.exists():
        try:
            spec = importlib.util.spec_from_file_location("cart_under_test", sol)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            grp("imports", False, f"{type(exc).__name__}: {exc}")
    if mod is None and not results:
        grp("imports", False, "cart.py missing")

    Cart = getattr(mod, "Cart", None) if mod else None
    if not isinstance(Cart, type):
        grp("has-cart", False)
        for g in ("basic-ops", "rounding-at-end", "coupon-stacking", "bulk-boundary"):
            grp(g, False)
    else:
        grp("has-cart", True)
        failures = []

        def check(label, cond):
            if not cond:
                failures.append(label)

        def case_basic():
            c = Cart()
            check("empty-total", c.total() == 0.0 and isinstance(c.total(), float))
            c.add("a", 2, 3.333)
            check("add-total", approx(c.total(), 6.67))
            try:
                c.remove("zz")
                check("remove-keyerror", False)
            except KeyError:
                check("remove-keyerror", True)
            c.add("a", 1, 5.0)   # increments qty, latest price wins
            check("latest-price", approx(c.total(), 15.0))
            c.add("b", 4, 2.5)
            c.remove("b")
            check("removed-excluded", approx(c.total(), 15.0))
            c.set_quantity("a", 3)
            check("set-qty", approx(c.total(), 15.0))

        def case_rounding():
            c = Cart()
            c.add("x", 2, 1.111)   # 2.222
            check("round-once-1", approx(c.total(), 2.22))
            c.add("y", 7, 1.115)   # raw 10.027 -> 10.03; per-line rounding gives 10.02
            check("half-up-boundary", approx(c.total(), 10.03))
            c2 = Cart()
            c2.add("p", 1, 2.004)
            c2.add("q", 1, 2.004)  # 4.008 -> 4.01 (per-line would give 4.00)
            check("no-per-line-rounding", approx(c2.total(), 4.01))
            try:
                c.add("bad", 0, 5.0)
                check("qty-zero-valueerror", False)
            except ValueError:
                check("qty-zero-valueerror", True)
            try:
                c.set_quantity("x", 0)
                check("setqty-zero-valueerror", False)
            except ValueError:
                check("setqty-zero-valueerror", True)

        def case_coupons():
            # NOTE: 8 units keeps every cart here BELOW the bulk threshold so
            # coupon math is isolated from the >=10 bulk rule.
            c = Cart()
            c.add("g", 8, 12.5)   # subtotal 100
            c.apply_coupon("SAVE10")
            check("one-coupon", approx(c.total(), 90.0))
            c.apply_coupon("SAVE10")
            check("multiplicative-stack", approx(c.total(), 81.0))
            c2 = Cart()
            c2.add("g", 8, 12.5)
            c2.apply_coupon("SAVE25")
            c2.apply_coupon("SAVE10")
            check("mixed-stack-order-independent", approx(c2.total(), 67.50))
            try:
                Cart().apply_coupon("FREE99")
                check("invalid-coupon", False)
            except ValueError:
                check("invalid-coupon", True)

        def case_bulk():
            c = Cart()                      # exactly 10 units qualifies (>=)
            c.add("u", 10, 10.0)
            check("boundary-inclusive", approx(c.total(), 95.0))
            c9 = Cart()
            c9.add("u", 9, 10.0)
            check("below-boundary", approx(c9.total(), 90.0))
            cb = Cart()
            cb.add("u", 10, 10.0)
            cb.apply_coupon("SAVE10")
            check("coupon-then-bulk", approx(cb.total(), 85.50))
            c3 = Cart()
            c3.add("u", 20, 5.0)
            c3.apply_coupon("SAVE10")
            c3.apply_coupon("SAVE10")
            c3.apply_coupon("SAVE25")       # 100 * .9*.9*.75*.95 = 57.71...
            check("three-coupon-bulk-halfup", approx(c3.total(), 57.71))
            c4 = Cart()
            c4.add("m", 6, 1.237)
            c4.add("n", 6, 0.833)           # units 12 -> bulk; raw: 7.422+4.998=12.42*0.95=11.799
            check("mixed-basket", approx(c4.total(), 11.80))

        for name, fn in [("basic-ops", case_basic),
                         ("rounding-at-end", case_rounding),
                         ("coupon-stacking", case_coupons),
                         ("bulk-boundary", case_bulk)]:
            failures.clear()
            try:
                fn()
                err = None
            except Exception as exc:  # noqa: BLE001
                err = f"{type(exc).__name__}: {exc}"
            ok = err is None and not failures
            grp(name, ok, err or ("; ".join(failures[:4]) if failures else ""))

    weights = [25, 25, 25, 25]
    score = sum(w for (_, ok), w in zip(results[1:], weights) if ok)
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
