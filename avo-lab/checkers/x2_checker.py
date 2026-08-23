"""X2 checker - ten-constraint report. Usage: python x2_checker.py <task_dir>"""
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROWS = [
    ("north", "anvil", 4, "12.505"), ("south", "bolt", 11, "0.355"),
    ("east", "crate", 7, "4.10"), ("west", "dowel", 2, "1.115"),
    ("north", "bolt", 6, "0.355"), ("east", "anvil", 3, "12.505"),
    ("west", "crate", 9, "4.10"), ("south", "dowel", 5, "1.115"),
    ("north", "crate", 8, "4.10"), ("east", "bolt", 12, "0.355"),
    ("west", "anvil", 1, "12.505"), ("south", "crate", 10, "4.10"),
]


def money(d: Decimal) -> float:
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def expected():
    rev_by_region, units_total = {}, 0
    prod_rev = {}
    for region, product, units, cost in ROWS:
        price = Decimal(cost) * Decimal("1.5")
        line_rev = Decimal(units) * price
        rev_by_region[region] = rev_by_region.get(region, Decimal(0)) + line_rev
        prod_rev[product] = prod_rev.get(product, Decimal(0)) + line_rev
        units_total += units
    grand = sum(rev_by_region.values(), Decimal(0))
    top3 = [p for p, _ in sorted(prod_rev.items(), key=lambda kv: (-kv[1], kv[0]))][:3]
    west_units = sum(u for r, _, u, _ in ROWS if r == "west")
    margin = int((Decimal(west_units) * 100 / Decimal(units_total))
                 .quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return {
        "grand": money(grand), "units": units_total,
        "regions_desc": {k: money(v) for k, v in sorted(rev_by_region.items(), reverse=True)},
        "top3": top3, "margin": margin,
    }


def main():
    task = Path(sys.argv[1])
    exp = expected()
    results = []

    def grp(name, ok, detail=""):
        results.append((f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", ok))

    data = None
    jp = task / "report.json"
    try:
        raw = json.loads(jp.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            # order check needs the raw text; use object_pairs via reparse
            pairs = json.loads(jp.read_text(encoding="utf-8"),
                               object_pairs_hook=lambda p: p)
            keys = [k for k, _ in pairs] if isinstance(pairs, list) else list(raw)
            data = (raw, keys)
    except Exception as exc:  # noqa: BLE001
        grp("C1-json-keys-order", False, f"unparsable/missing: {exc}")

    if data is not None:
        raw, keys = data
        grp("C1-json-keys-order", keys == ["meta", "totals", "regions", "top_products"],
            f"got {keys}")
        grp("C2-meta-exact", raw.get("meta") == {"generated_by": "AVO-R2", "source_rows": 12})
        g = raw.get("totals", {}).get("grand_revenue")
        grp("C3-grand-revenue", isinstance(g, (int, float)) and abs(g - exp["grand"]) <= 0.01,
            f"expected ~{exp['grand']}")
        u = raw.get("totals", {}).get("units_total")
        grp("C4-units-total", u == exp["units"], f"expected {exp['units']}")
        regs = raw.get("regions")
        ok5 = (isinstance(regs, dict) and list(regs.keys()) == list(exp["regions_desc"].keys())
               and all(abs(regs[k] - v) <= 0.01 for k, v in exp["regions_desc"].items()))
        grp("C5-regions-desc-order", ok5,
            f"expected keys {list(exp['regions_desc'])}")
        tp = raw.get("top_products")
        grp("C6-top-products", tp == exp["top3"], f"expected {exp['top3']}")

    tp = task / "report.txt"
    txt = tp.read_text(encoding="utf-8") if tp.exists() else None
    if txt is None:
        for c in ("C7-six-lines", "C8-separator-line",
                  "C9-total-and-terminal-percent", "C10-no-commas-no-lowercase"):
            grp(c, False)
    else:
        lines = txt.split("\n")
        trailing_nl = txt.endswith("\n")
        body = lines[:-1] if trailing_nl else lines
        if body and body[-1] == "" and trailing_nl:
            pass
        grp("C7-six-lines", len(body) == 6 and trailing_nl,
            f"{len(body)} content lines, trailing_nl={trailing_nl}")
        grp("C8-separator-line", len(body) >= 3 and body[2] == "---")
        last_char_ok = bool(txt) and txt.rstrip("\n").endswith("%")
        line1_ok = len(body) >= 1 and body[0] == f"TOTAL: {exp['grand']} USD"
        mline = body[-1] if body else ""
        margin_ok = mline.startswith("MARGIN ") and mline.endswith("%") \
            and mline[len("MARGIN "):-1].strip().isdigit() \
            and int(mline[len("MARGIN "):-1].strip()) == exp["margin"]
        grp("C9-total-and-terminal-percent",
            line1_ok and last_char_ok and margin_ok,
            f"line1_ok={line1_ok} ends%={last_char_ok} margin(expected {exp['margin']})={mline!r}")
        grp("C10-no-commas-no-lowercase",
            "," not in txt and not re.search(r"[a-z]", txt))

    score = sum(10 for _, ok in results if ok)
    for line, _ in results:
        print(line.rstrip())
    verdict = "PASS" if score == 100 else "FAIL"
    print(f"SCORE {score}/100 {verdict}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
