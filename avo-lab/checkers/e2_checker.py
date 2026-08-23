"""E2 checker — CSV revenue stats. Usage: python e2_checker.py <task_dir>"""
import csv
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path


def money(d: Decimal) -> float:
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def expected(task: Path):
    regions = {"north": Decimal(0), "south": Decimal(0),
               "east": Decimal(0), "west": Decimal(0)}
    qty_by_product = {}
    total = Decimal(0)
    n = 0
    with (task / "sales.csv").open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            n += 1
            line = Decimal(row["quantity"]) * Decimal(row["unit_price"])
            regions[row["region"]] += line
            total += line
            qty_by_product[row["product"]] = (
                qty_by_product.get(row["product"], 0) + int(row["quantity"])
            )
    top = sorted(qty_by_product.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return {
        "total_orders": n,
        "revenue_by_region": {k: money(v) for k, v in regions.items()},
        "top_product": top,
        "grand_total": money(total),
    }


def main():
    task = Path(sys.argv[1])
    exp = expected(task)
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    path = task / "stats.json"
    got = None
    if path.exists():
        try:
            got = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            grp("json-parses", False, str(exc))
    if got is not None:
        grp("json-parses", True)
        grp("total-orders", isinstance(got.get("total_orders"), int)
            and got["total_orders"] == exp["total_orders"],
            f"expected {exp['total_orders']}")
        rev = got.get("revenue_by_region")
        ok_rev = isinstance(rev, dict) and set(rev) == set(exp["revenue_by_region"]) and all(
            isinstance(v, (int, float)) and abs(v - exp["revenue_by_region"][k]) <= 0.01
            for k, v in rev.items())
        grp("revenue-by-region", ok_rev,
            f"expected {exp['revenue_by_region']}")
        gt = got.get("grand_total")
        grp("grand-total", isinstance(gt, (int, float))
            and abs(gt - exp["grand_total"]) <= 0.01,
            f"expected {exp['grand_total']}")
        grp("top-product", got.get("top_product") == exp["top_product"],
            f"expected {exp['top_product']!r}")
    elif not results:
        grp("json-parses", False, "stats.json missing")
        grp("total-orders", False)
        grp("revenue-by-region", False)
        grp("grand-total", False)
        grp("top-product", False)

    weights = (10, 20, 30, 20, 20)[: len(results)]
    score = sum(w for (_, ok), w in zip(results, weights) if ok)
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
